"""
Get timing endpoints from .sdf file or STA report
"""
import re
from config import CELL_PIN_SEP

def get_timing_endpoint_from_sdc(sdc_path):
    '''If a port is constrainted in .sdf file, then it is a timing endpoint'''
    print("Extracting which pins are timing endpoints")
    with open(sdc_path) as f:
        content = f.read()
    pattern = re.compile(r'\[get_ports \{([\w\[\]]+?)\}\]')
    res = pattern.findall(content)
    return res


def get_timing_endpoint_from_STA_report(path_report):
    """Get timing endpoints from STA report"""
    print("Extracting which pins are timing endpoints from STA report")
    with open(path_report) as f:
        lines = f.readlines()
    
    pattern = re.compile(r"\s+")
    p_start = re.compile(r"^\s*")
    p_end = re.compile(r"\s*$")

    res = []

    # _697_/Q (gcd)                        resp_msg[15] (output)                  -0.087461
    for line in lines[2:]:
        line = p_start.sub("", line)
        line = p_end.sub("", line)
        line = pattern.sub(" ", line)
        if line == "":
            continue
        endpoint = line.split(' ')[2].replace('/', CELL_PIN_SEP)
        res.append(endpoint)
        
    return sorted(res)