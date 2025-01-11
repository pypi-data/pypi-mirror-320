import copy
import gzip
import math
import os
import struct
import time
import zlib
from functools import cmp_to_key

from Crypto.Cipher import AES
from scapy.layers.inet import TCP, IP
from scapy.packet import Raw
from zstandard import ZstdDecompressor

from xbase_util.common_util import parse_chunked_body, filter_visible_chars
from xbase_util.xbase_constant import pattern_chuncked, pattern_gzip


def fix_pos(pos, packetPosEncoding):
    if pos is None or len(pos) == 0:
        return
    if packetPosEncoding == "gap0":
        last = 0
        lastgap = 0
        for i, pos_item in enumerate(pos):
            if pos[i] < 0:
                last = 0
            else:
                if pos[i] == 0:
                    pos[i] = last + lastgap
                else:
                    lastgap = pos[i]
                    pos[i] += last
                last = pos[i]


def group_numbers(nums):
    result = []
    for num in nums:
        if num < 0:
            result.append([num])
        elif result:
            result[-1].append(num)
    return result


def decompress_streaming(compressed_data, session_id):
    try:
        decompressor = ZstdDecompressor()
        with decompressor.stream_reader(compressed_data) as reader:
            decompressed_data = reader.read()
            return decompressed_data
    except Exception as e:
        print(f"解码错误：{e}  {session_id}")
        return bytearray()


def readUInt32BE(buffer, offset):
    return struct.unpack('>I', buffer[offset:offset + 4])[0]


def readUInt32LE(buffer, offset):
    return struct.unpack('<I', buffer[offset:offset + 4])[0]


def writeUInt32BE(buffer, pos, value):
    struct.pack_into('>I', buffer, pos, value)
    return buffer


def read_header(param_map, session_id):
    shortHeader = None
    headBuffer = os.read(param_map['fd'], 64)
    if param_map['encoding'] == 'aes-256-ctr':
        if 'iv' in param_map:
            param_map['iv'][12:16] = struct.pack('>I', 0)
            headBuffer = bytearray(
                AES.new(param_map['encKey'], AES.MODE_CTR, nonce=param_map['iv']).decrypt(bytes(headBuffer)))
        else:
            print("读取头部信息失败，iv向量为空")
    elif param_map['encoding'] == 'xor-2048':
        for i in range(len(headBuffer)):
            headBuffer[i] ^= param_map['encKey'][i % 256]
    if param_map['uncompressedBits']:
        if param_map['compression'] == 'gzip':
            headBuffer = zlib.decompress(bytes(headBuffer), zlib.MAX_WBITS | 16)
        elif param_map['compression'] == 'zstd':
            headBuffer = decompress_streaming(headBuffer, session_id)
    headBuffer = headBuffer[:24]
    magic = struct.unpack('<I', headBuffer[:4])[0]
    bigEndian = (magic == 0xd4c3b2a1 or magic == 0x4d3cb2a1)
    nanosecond = (magic == 0xa1b23c4d or magic == 0x4d3cb2a1)
    if not bigEndian and magic not in {0xa1b2c3d4, 0xa1b23c4d, 0xa1b2c3d5}:
        raise ValueError("Corrupt PCAP header")
    if magic == 0xa1b2c3d5:
        shortHeader = readUInt32LE(headBuffer, 8)
        headBuffer[0] = 0xd4  # Reset header to normal
    if bigEndian:
        linkType = readUInt32BE(headBuffer, 20)
    else:
        linkType = readUInt32LE(headBuffer, 20)
    return headBuffer, shortHeader, bigEndian, linkType, nanosecond


def create_decipher(pos, param_map):
    writeUInt32BE(param_map['iv'], pos, 12)
    return AES.new(param_map['encKey'], AES.MODE_CTR, nonce=param_map['iv'])


def read_packet_internal(pos_arg, hp_len_arg, param_map, session_id):
    pos = pos_arg
    hp_len = hp_len_arg
    if hp_len == -1:
        if param_map['compression'] == "zstd":
            hp_len = param_map['uncompressedBitsSize']
        else:
            hp_len = 2048
    inside_offset = 0
    if param_map['uncompressedBits']:
        inside_offset = pos & param_map['uncompressedBitsSize'] - 1
        pos = math.floor(pos / param_map['uncompressedBitsSize'])
    pos_offset = 0
    if param_map['encoding'] == 'aes-256-ctr':
        pos_offset = pos % 16
        pos = pos - pos_offset
    elif param_map['encoding'] == 'xor-2048':
        pos_offset = pos % 256
        pos = pos - pos_offset

    hp_len = 256 * math.ceil((hp_len + inside_offset + pos_offset) / 256)
    buffer = bytearray(hp_len)
    os.lseek(param_map['fd'], pos, os.SEEK_SET)
    read_buffer = os.read(param_map['fd'], len(buffer))
    if len(read_buffer) - pos_offset < 16:
        return None
    if param_map['encoding'] == 'aes-256-ctr':
        decipher = create_decipher(pos // 16, param_map)
        read_buffer = bytearray(decipher.decrypt(read_buffer))[pos_offset:]
    elif param_map['encoding'] == 'xor-2048':
        read_buffer = bytearray(b ^ param_map['encKey'][i % 256] for i, b in enumerate(read_buffer))[pos_offset:]
    if param_map['uncompressedBits']:
        try:
            if param_map['compression'] == 'gzip':
                read_buffer = zlib.decompress(read_buffer, zlib.MAX_WBITS | 16)
            elif param_map['compression'] == 'zstd':
                read_buffer = decompress_streaming(read_buffer, session_id)
        except Exception as e:
            print(f"PCAP uncompress issue:  {pos} {len(buffer)} {read_buffer} {e}")
            return None
    if inside_offset:
        read_buffer = read_buffer[inside_offset:]
    header_len = 16 if param_map['shortHeader'] is None else 6
    if len(read_buffer) < header_len:
        if hp_len_arg == -1 and param_map['compression'] == 'zstd':
            return read_packet_internal(pos_arg, param_map['uncompressedBitsSize'] * 2, param_map, session_id)
        print(f"Not enough data {len(read_buffer)} for header {header_len}")
        return None
    packet_len = struct.unpack('>I' if param_map['bigEndian'] else '<I', read_buffer[8:12])[
        0] if param_map['shortHeader'] is None else \
        struct.unpack('>H' if param_map['bigEndian'] else '<H', read_buffer[:2])[0]
    if packet_len < 0 or packet_len > 0xffff:
        return None
    if header_len + packet_len <= len(read_buffer):
        if param_map['shortHeader'] is not None:
            t = struct.unpack('<I', read_buffer[2:6])[0]
            sec = (t >> 20) + param_map['shortHeader']
            usec = t & 0xfffff
            new_buffer = bytearray(16 + packet_len)
            struct.pack_into('<I', new_buffer, 0, sec)
            struct.pack_into('<I', new_buffer, 4, usec)
            struct.pack_into('<I', new_buffer, 8, packet_len)
            struct.pack_into('<I', new_buffer, 12, packet_len)
            new_buffer[16:] = read_buffer[6:packet_len + 6]
            return new_buffer
        return read_buffer[:header_len + packet_len]

    if hp_len_arg != -1:
        return None

    return read_packet_internal(pos_arg, 16 + packet_len, param_map, session_id)


def read_packet(pos, param_map, session_id):
    if 'fd' not in param_map or not param_map['fd']:
        time.sleep(0.01)
        return read_packet(pos, param_map['fd'], session_id)
    return read_packet_internal(pos, -1, param_map, session_id)


def get_file_and_read_pos(session_id, file, pos_list):
    filename = file['name']
    if not os.path.isfile(filename):
        print(f"文件不存在:{filename}")
        return None
    encoding = file.get('encoding', 'normal')
    encKey = None
    iv = None
    compression = None
    if 'dek' in file:
        dek = bytes.fromhex(file['dek'])
        encKey = AES.new(file['kek'].encode(), AES.MODE_CBC).decrypt(dek)

    if 'uncompressedBits' in file:
        uncompressedBits = file['uncompressedBits']
        uncompressedBitsSize = 2 ** uncompressedBits
        compression = 'gzip'
    else:
        uncompressedBits = None
        uncompressedBitsSize = 0
    if 'compression' in file:
        compression = file['compression']

    if 'iv' in file:
        iv_ = bytes.fromhex(file['iv'])
        iv = bytearray(16)
        iv[:len(iv_)] = iv_
    fd = os.open(filename, os.O_RDONLY)
    param_map = {
        "fd": fd,
        "encoding": encoding,
        "iv": iv,
        "encKey": encKey,
        "uncompressedBits": uncompressedBits,
        "compression": compression,
        "uncompressedBitsSize": uncompressedBitsSize
    }
    res = bytearray()
    headBuffer, shortHeader, bigEndian, linkType, nanosecond = read_header(param_map, session_id)
    res.extend(headBuffer)
    param_map['shortHeader'] = shortHeader
    param_map['bigEndian'] = bigEndian
    # _________________________________
    byte_array = bytearray(0xfffe)
    next_packet = 0
    b_offset = 0
    packets = {}
    # packet_objs = []
    i = 0
    for pos in pos_list:
        packet_bytes = read_packet(pos, param_map, session_id)
        # if reture_obj:
        #     obj = decode_obj(packet_bytes, bigEndian, linkType, nanosecond, )
        #     packet_objs.append(copy.deepcopy(obj))
        if not packet_bytes:
            continue
        packets[i] = packet_bytes
        while next_packet in packets:
            buffer = packets[next_packet]

            next_packet += 1
            # del packets[next_packet]
            next_packet = next_packet + 1
            if b_offset + len(buffer) > len(byte_array):
                res.extend(byte_array[:b_offset])
                b_offset = 0
                byte_array = bytearray(0xfffe)
            byte_array[b_offset:b_offset + len(buffer)] = buffer
            b_offset += len(buffer)
        i = i + 1
    os.close(fd)
    res.extend(byte_array[:b_offset])
    return res


def process_session_id_disk_simple(id, node, packet_pos, esdb, pcap_path_prefix):
    packetPos = packet_pos
    file = esdb.get_file_by_file_id(node=node, num=abs(packetPos[0]),
                                    prefix=None if pcap_path_prefix == "origin" else pcap_path_prefix)
    if file is None:
        return None, None
    fix_pos(packetPos, file['packetPosEncoding'])
    pos_list = group_numbers(packetPos)[0]
    pos_list.pop(0)
    return get_file_and_read_pos(id, file, pos_list)


def parse_body(data,session_id='none'):
    if data.find(b"\r\n\r\n") != -1:
        res = data.split(b"\r\n\r\n", 1)
        header = res[0]
        body = res[1]
    else:
        header = data
        body = b''
    chunked_pattern = pattern_chuncked.search(header)
    gzip_pattern = pattern_gzip.search(header)
    need_gzip = gzip_pattern and b'gzip' in gzip_pattern.group()
    if chunked_pattern and b'chunked' in chunked_pattern.group():
        body = parse_chunked_body(body, need_un_gzip=need_gzip,session_id=session_id)
    elif need_gzip:
        try:
            body = gzip.decompress(body)
        except:
            print("解压失败")
            pass
    result_body_str = filter_visible_chars(body)
    return filter_visible_chars(header), result_body_str


def reassemble_session_pcap(reassemble_tcp_res, skey,session_id='none'):
    my_map = {
        'key': '',
        'req_header': '',
        'req_body': '',
        'req_time': 0,
        'req_size': 0,
        'res_header': '',
        'res_body': '',
        'res_time': 0,
        'res_size': 0,
    }
    packet_list = []
    for index, packet in enumerate(reassemble_tcp_res):
        header, body = parse_body(packet['data'], session_id=session_id)
        if index == len(reassemble_tcp_res) - 1:
            packet_list.append(copy.deepcopy(my_map))
        if packet['key'] == skey:
            if index != 0:
                packet_list.append(copy.deepcopy(my_map))
                my_map = {
                    'key': packet['key'],
                    'req_header': '',
                    'req_body': b'',
                    'req_time': 0,
                    'req_size': 0,
                    'res_header': '',
                    'res_body': b'',
                    'res_time': 0,
                    'res_size': 0,
                }
            my_map["req_header"] = header
            my_map["req_body"] = body
            my_map["req_time"] = packet['ts']
            my_map["req_size"] = len(packet['data'])
        else:
            my_map["res_header"] = header
            my_map["res_body"] = body
            my_map["res_time"] = packet['ts']
            my_map["res_size"] = len(packet['data'])
    return packet_list


def reassemble_tcp_pcap(p):
    packets = [{'pkt': item} for item in p if TCP in item and Raw in item]
    packets2 = []
    info = {}
    keys = []
    for index, packet in enumerate(packets):
        data = packet['pkt'][Raw].load
        flags = packet['pkt'][TCP].flags
        seq = packet['pkt'][TCP].seq
        if len(data) == 0 or 'R' in flags or 'S' in flags:
            continue
        key = f"{packet['pkt'][IP].src}:{packet['pkt'][IP].sport}"
        if key not in info.keys():
            info[key] = {
                "min": seq,
                "max": seq,
                "wrapseq": False,
                "wrapack": False,
            }
            keys.append(key)
        elif info[key]["min"] > seq:
            info[key]['min'] = seq
        elif info[key]["max"] < seq:
            info[key]['max'] = seq
        packets2.append(packet)
    if len(keys) == 1:
        key = f"{packets2[0]['pkt'][IP].dst}:{packets2[0]['pkt'][IP].dport}"
        ack = packets2[0]['pkt'][TCP].ack
        info[key] = {
            "min": ack,
            "max": ack,
            "wrapseq": False,
            "wrapack": False,
        }
        keys.append(key)
    if len(packets2) == 0:
        return []
    needwrap = False
    if info[keys[0]] and info[keys[0]]['max'] - info[keys[0]]['min'] > 0x7fffffff:
        info[keys[0]]['wrapseq'] = True
        info[keys[0]]['wrapack'] = True
        needwrap = True
    if info[keys[1]] and info[keys[1]]['max'] - info[keys[1]]['min'] > 0x7fffffff:
        info[keys[1]]['wrapseq'] = True
        info[keys[0]]['wrapack'] = True
        needwrap = True
    if needwrap:
        for packet in packets2:
            key = f"{packet['ip']['addr1']}:{packet['tcp']['sport']}"
            if info[key]['wrapseq'] and packet['tcp']['seq'] < 0x7fffffff:
                packet['tcp']['seq'] += 0xffffffff
            if info[key]['wrapack'] and packet['tcp']['ack'] < 0x7fffffff:
                packet['tcp']['ack'] += 0xffffffff
    clientKey = f"{packets2[0]['pkt'][IP].src}:{packets2[0]['pkt'][IP].sport}"

    def compare_packets(a, b):
        a_seq = a['pkt'][TCP].seq
        b_seq = b['pkt'][TCP].seq
        a_ack = a['pkt'][TCP].ack
        b_ack = b['pkt'][TCP].ack
        a_data = a['pkt'][Raw].load
        b_data = b['pkt'][Raw].load
        a_ip = a['pkt'][IP].src
        a_port = a['pkt'][TCP].sport
        b_port = b['pkt'][TCP].sport
        b_ip = b['pkt'][IP].src
        if a_ip == b_ip and a_port == b_port:
            return a_seq - b_seq
        if clientKey == f"{a_ip}:{a_port}":
            return (a_seq + len(a_data) - 1) - b_ack
        return a_ack - (b_seq + len(b_data) - 1)

    packets2.sort(key=cmp_to_key(compare_packets))
    # del packets[num_packets:]
    # Now divide up conversation
    clientSeq = 0
    hostSeq = 0
    previous = 0
    results = []
    for i, item in enumerate(packets2):
        sip = item['pkt'][IP].src
        sport = item['pkt'][IP].sport
        seq = item['pkt'][TCP].seq
        data = item['pkt'][Raw].load
        pkey = f"{sip}:{sport}"
        seq_datalen = seq + len(data)
        if pkey == clientKey:
            if clientSeq >= seq_datalen:
                continue
            clientSeq = seq_datalen
        else:
            if hostSeq >= seq_datalen:
                continue
            hostSeq = seq_datalen
        if len(results) == 0 or pkey != results[len(results) - 1]['key']:
            previous = seq
            results.append({
                'key': pkey,
                'data': copy.deepcopy(data),
                'ts': float(item['pkt'].time),
                'pkt': item['pkt'],
            })
        elif seq - previous > 0xffff:
            results.append(
                {'key': '',
                 'data': b'',
                 'ts': float(item['pkt'].time),
                 'pkt': item['pkt'],
                 })
            previous = seq
            results.append({
                'key': pkey,
                'data': copy.deepcopy(data),
                'ts': float(item['pkt'].time),
                'pkt': item['pkt'],
            })
        else:
            previous = seq
            results[-1]['data'] += data
    return results
