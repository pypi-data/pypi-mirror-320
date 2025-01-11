import re

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
    if len(all_packets) != 0:
        all_req_size = [item['req_size'] for item in all_packets if item['key'] == skey]
        all_res_size = [item['res_size'] for item in all_packets if item['key'] != skey]
        num_1, num_2, num_3, num_4, num_5 = get_res_status_code_list(all_packets)
        # 获取请求头参数数量
        req_header_count_list = [req['req_header'].count(":") for req in all_packets]
        # 请求的时间间隔
        request_flattened_time = [item['req_time'] for item in all_packets]
        request_time_diffs = [request_flattened_time[i + 1] - request_flattened_time[i] for i in
                              range(len(request_flattened_time) - 1)]
        request_mean_diff = round(np.nanmean(request_time_diffs), 5) or 0
        request_variance_diff = round(np.nanvar(request_time_diffs), 5) or 0
        # 响应的时间间隔
        response_flattened_time = [item['res_time'] for item in all_packets]
        response_time_diffs = [response_flattened_time[i + 1] - response_flattened_time[i] for i in
                               range(len(response_flattened_time) - 1)]
        response_mean_diff = round(np.nanmean(response_time_diffs), 5) or 0
        response_variance_diff = round(np.nanvar(response_time_diffs), 5) or 0

        time_period = [(abs(item['res_time'] - item['req_time'])) for item in
                       all_packets if item['res_time'] != 0 and item['req_time'] != 0]
