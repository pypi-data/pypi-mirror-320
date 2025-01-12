from scapy.utils import rdpcap

from xbase_util.pcap_util import reassemble_tcp_pcap, reassemble_session_pcap

if __name__ == '__main__':
    packets_scapy = reassemble_tcp_pcap(rdpcap("test1.pcap"))
    skey = '10.28.7.53:58598'
    all_packets = reassemble_session_pcap(packets_scapy, skey=skey,session_id='emmmmm')
    print(all_packets)