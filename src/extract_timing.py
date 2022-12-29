import re
from collections import defaultdict
import numpy as np
from config.config import CELL_PIN_SEP
from config.config import CONNECTION_SEP
import copy

def extract_timing(sdf_file):
    print("Extracting timing (AT, RAT, slew)")
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
        pin_name = r[1].replace('/',CELL_PIN_SEP)
        if pin_name in atslew.keys():
            pass
        else:
            atslew[pin_name] = {}
        atslew[pin_name][r[0]] = [float(i) for i in r[2:]]
    return atslew


def extract_net_delay(sdf_file_content):
    # (INTERCONNECT req_msg[16] input8/A (0.000::0.000) (0.000::0.000))
    # (INTERCONNECT req_msg[16] input8/A (0.000::0.000))
    # \ maybe exists in this line
    # p = re.compile(r'INTERCONNECT ([\w\[\]\.\\\/]*?) ([\w\[\]\.\\\/]*?) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\)')
    p = re.compile(r'\(INTERCONNECT[\s\S]*?\n')
    p_float = re.compile(r'[+-]?\d*\.?\d+')
    res = p.findall(sdf_file_content)
    net_delay = {}
    for r in res:
        tmp = r.split(' ')
        cell_pin1 = tmp[1].replace('/',CELL_PIN_SEP)
        cell_pin2 = tmp[2].replace('/',CELL_PIN_SEP)

        if '\\' in cell_pin1:
            # print(f"\\ is in {cell_pin1}, remove it")
            cell_pin1 = cell_pin1.replace('\\', '')
        
        if '\\' in cell_pin2:
            # print(f"\\ is in {cell_pin2}, remove it")
            cell_pin2 = cell_pin2.replace('\\', '')

        numbers = ''.join(tmp[3:])
        numbers = p_float.findall(numbers)
        if len(numbers) < 4:
            print(f"interconnection delay for {cell_pin1}{CONNECTION_SEP}{cell_pin2} is not enough as 4 elements, only {len(numbers)}")
            if len(numbers) == 0:
                numbers = [0.0] * 4
            else:
                tmp = copy.copy(numbers)
                for i in range(4 - len(numbers)):
                    numbers.append(tmp[i % len(tmp)])


        key = cell_pin1 + CONNECTION_SEP + cell_pin2
        net_delay[key] = [float(i) for i in numbers[0:4]]
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
            pin_src = cell + CELL_PIN_SEP + r[2]
            pin_dst = cell + CELL_PIN_SEP + r[3]
            ans[pin_src + CONNECTION_SEP + pin_dst].append([float(i) for i in list(r[4:])])
    for k in ans.keys():
        ans[k] = np.stack(ans[k], axis=0).mean(axis=0).tolist()
    return dict(ans)



if __name__ == "__main__":
    res = extract_timing('data\\6_final.sdf')
    for item in res[0].items():
        print(item)