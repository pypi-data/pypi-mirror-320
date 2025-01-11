from scapy.packet import Raw
from scapy.utils import rdpcap

from xbase_util.pcap_util import reassemble_tcp_pcap, reassemble_session_pcap

if __name__ == '__main__':
    packets_scapy = reassemble_tcp_pcap(rdpcap("test.pcap"))
    skey = '10.28.7.1:57266'
    all_packets = reassemble_session_pcap(packets_scapy, skey=skey,session_id='enn')

    print(all_packets)