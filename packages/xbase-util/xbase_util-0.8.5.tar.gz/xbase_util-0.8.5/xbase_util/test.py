import re
from collections import Counter

import numpy as np
from scapy.packet import Raw
from scapy.utils import rdpcap

from xbase_util.common_util import get_res_status_code_list
from xbase_util.pcap_util import reassemble_tcp_pcap, reassemble_session_pcap
from xbase_util.xbase_constant import res_status_code_pattern

if __name__ == '__main__':
    packets_scapy = reassemble_tcp_pcap(rdpcap("gzip2.pcap"))
    skey = '10.28.7.16:54398'
    streams = b""
    for pkt in packets_scapy:
        if Raw in pkt:
            streams += pkt[Raw].load
    text_data = streams.decode('ascii', errors='ignore')
    all_packets = reassemble_session_pcap(packets_scapy, skey=skey)

