import re
from collections import defaultdict

def extract_timing(sdf_file):
    with open(sdf_file) as f:
        c = f.read()
    atslew = extract_atslew(c)
    net_delay = extract_net_delay(c)
    
    return atslew, net_delay


def extract_atslew(sdf_file_content):
    p = re.compile(r'\((\w+) (\w+/\w+) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\)\)')
    res = p.findall(sdf_file_content)
    atslew = {}
    for r in res:
        pin_name = r[1].replace('/','.')
        if pin_name in atslew.keys():
            pass
        else:
            atslew[pin_name] = {}
        atslew[pin_name][r[0]] = r[2:]
    return atslew


def extract_net_delay(sdf_file_content):
    p = re.compile(r'INTERCONNECT (\w+/?\w+) (\w+/?\w+) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\)')
    res = p.findall(sdf_file_content)
    net_delay = defaultdict(lambda:{})
    for r in res:
        net_delay[r[0].replace('/','.')][r[1].replace('/','.')] = r[2:]
    return dict(net_delay)

if __name__ == "__main__":
    res = extract_timing('data\\6_final.sdf')
    for v in res.values():
        print(v)