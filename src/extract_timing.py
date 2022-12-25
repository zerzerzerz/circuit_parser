import re
from collections import defaultdict
import numpy as np

def extract_timing(sdf_file):
    with open(sdf_file) as f:
        c = f.read()
    atslew = extract_atslew(c)
    net_delay = extract_net_delay(c)
    cell_delay = extract_cell_delay(c)
    return atslew, net_delay, cell_delay


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
        atslew[pin_name][r[0]] = [float(i) for i in r[2:]]
    return atslew


def extract_net_delay(sdf_file_content):
    p = re.compile(r'INTERCONNECT (\w+/?\w+) (\w+/?\w+) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\)')
    res = p.findall(sdf_file_content)
    net_delay = {}
    for r in res:
        key = r[0].replace('/','.') + '->' + r[1].replace('/','.')
        net_delay[key] = [float(i) for i in r[2:]]
    return dict(net_delay)


def extract_cell_delay(sdf_file_content):
    p = re.compile(r'\(CELLTYPE "(\w+)"\)\s+\(INSTANCE (\w+)\)|IOPATH (\w+) (\w+) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\)')
    res = p.findall(sdf_file_content)
    cell = pin_src = pin_src = None
    ans = defaultdict(lambda: [])
    for r in res:
        if r[1] != '':
            cell = r[1]
        else:
            pin_src = cell + '.' + r[2]
            pin_dst = cell + '.' + r[3]
            ans[pin_src + '->' + pin_dst].append([float(i) for i in list(r[4:])])
    for k in ans.keys():
        ans[k] = np.stack(ans[k], axis=0).mean(axis=0).tolist()
    return dict(ans)



if __name__ == "__main__":
    res = extract_timing('data\\6_final.sdf')
    for item in res[0].items():
        print(item)