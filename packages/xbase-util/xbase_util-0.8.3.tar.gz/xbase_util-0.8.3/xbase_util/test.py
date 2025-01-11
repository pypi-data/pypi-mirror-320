from scapy.utils import rdpcap

from xbase_util.pcap_util import reassemble_tcp_pcap, reassemble_session_pcap

if __name__ == '__main__':
    packets = reassemble_tcp_pcap(rdpcap("gzip2.pcap"))
    res=reassemble_session_pcap(packets, skey='10.28.7.16:54398')
    print(res)
