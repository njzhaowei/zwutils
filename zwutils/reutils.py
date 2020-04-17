import re

def find_ip(s):
    # re_str = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}[:\d{1,5}]*'
    re_str = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?[:\d{1,5}]*)'
    rtn = re.findall(re_str, s)
    return rtn

def find_port(s, port_start=1024):
    re_str = r'\d{1,5}'
    rtn = re.findall(re_str, s)
    rtn = [int(r) for r in rtn if int(r)>=port_start]
    return rtn