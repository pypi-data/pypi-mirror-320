from scapy.packet import Raw
from scapy.utils import rdpcap

from xbase_util.pcap_util import reassemble_tcp_pcap, reassemble_session_pcap

if __name__ == '__main__':
    packets_scapy = reassemble_tcp_pcap(rdpcap("gzip2.pcap"))
    skey = '10.28.7.16:54398'
    streams = b""
    for pkt in packets_scapy:
        if Raw in pkt:
            streams += pkt[Raw].load
    text_data = streams.decode('ascii', errors='ignore')
    all_packets = reassemble_session_pcap(packets_scapy, skey=skey,session_id='enn')

