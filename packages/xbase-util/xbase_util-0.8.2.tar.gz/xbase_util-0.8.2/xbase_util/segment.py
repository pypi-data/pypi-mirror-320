from scapy.all import *
from scapy.layers.inet import TCP

from xbase_util.packet_util import filter_visible_chars
from xbase_util.xbase_util import parse_chunked_body

REQUEST_LINE_RE = re.compile(rb"^(GET|POST|PUT|DELETE|OPTIONS|HEAD|PATCH)\s[^\r\n]+\r\n", re.MULTILINE)
RESPONSE_LINE_RE = re.compile(rb"^HTTP/\d\.\d\s+\d{3}\s?[^\r\n]*", re.IGNORECASE)


def read_packets(packets):
    last_seq_len = -1
    last_ack = -1
    packet_list = []
    tmp_data = b''
    tmp_packets = []
    for index, pkt in enumerate(packets):
        data = pkt[Raw].load if Raw in pkt else b''
        ack = pkt[TCP].ack
        seq = pkt[TCP].seq
        if seq == last_seq_len:
            # print(f"检测到连续包 数据长度:{len(data)} + seq:{seq}={len(data) + seq}  ack:{ack}")
            tmp_data += data
            tmp_packets.append(pkt)
        elif seq == last_ack:
            if tmp_data != b'':
                if REQUEST_LINE_RE.match(tmp_data) or RESPONSE_LINE_RE.match(tmp_data):
                    packet_list.append({'data': copy.deepcopy(tmp_data), 'pkts': copy.deepcopy(tmp_packets)})
                else:
                    # print("没有新的请求或者响应，就把数据加到上一个里面")
                    if len(packet_list) > 0:
                        # 之前找到过有请求，可以添加到之前的数据，否则说明一开始就没找到请求
                        packet_list[-1]['pkts'].extend(copy.deepcopy(tmp_packets))
                        packet_list[-1]['data'] += tmp_data

            tmp_data = data
            tmp_packets = [pkt]
            # print(f"顺序正确 数据长度:{len(data)} + seq:{seq}={len(data) + seq}  ack:{ack}")
        else:
            # print(f"顺序错误 数据长度:{len(data)} + seq:{seq}={len(data) + seq}  ack:{ack}")
            if len(data) > 0:
                # 但是有数据
                tmp_data += data
                tmp_packets.append(pkt)
        last_ack = ack
        last_seq_len = seq + len(data)
    if tmp_data != b'':
        packet_list.append({'data': copy.deepcopy(tmp_data), 'pkts': copy.deepcopy(tmp_packets)})
        tmp_packets.clear()
    return packet_list


def parse_req_or_res(data, pkts):
    if data.find(b"\r\n\r\n") != -1:
        res = data.split(b"\r\n\r\n", 1)
        header = res[0]
        body = res[1]
    else:
        header = data
        body = b''
    body = parse_chunked_body(body)
    result_body_str = filter_visible_chars(body)
    return filter_visible_chars(header), result_body_str, [float(pkt.time) for pkt in pkts]


def get_all_packets_by_segment(packets):
    res = read_packets(packets)
    request_packets = [item for item in res if REQUEST_LINE_RE.match(item['data'])]
    response_packets = [
        {'first_seq': item['pkts'][0][TCP].seq, 'pkts': item['pkts'], 'first_ack': item['pkts'][0][TCP].ack,
         'data': item['data']} for item in
        res if RESPONSE_LINE_RE.match(item['data'])]
    packet_list = []
    for request in request_packets:
        pkt_list = request['pkts']
        last_pkt = pkt_list[-1]
        ack = last_pkt[TCP].ack
        response = [item for item in response_packets if item['first_seq'] == ack]
        if len(response) > 0:
            res_header, res_body, res_times = parse_req_or_res(response[0]['data'], response[0]['pkts'])
            req_header, req_body, req_times = parse_req_or_res(request['data'], request['pkts'])
            packet_list.append({
                "req_header": req_header,
                "req_body": req_body,
                "req_time": req_times,
                "req_packets": len(request['pkts']),
                "res_header": res_header,
                "res_body": res_body,
                "res_time": res_times,
                "res_packets": len(response[0]['pkts']),
            })
        else:
            # print("没响应")
            req_header, req_body, req_times = parse_req_or_res(request['data'], request['pkts'])
            packet_list.append({
                "req_header": req_header,
                "req_body": req_body,
                "req_time": req_times,
                "req_packets": len(request['pkts']),
                "res_header": '',
                "res_body": '',
                "res_time": [],
                "res_packets": 0,
            })
    return packet_list
