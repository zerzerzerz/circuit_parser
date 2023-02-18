"""
Extract timing information from .sdf file.
Instance name maybe ugly like RAM\.MUX\.MUX\[21\].
remove all slash
"""
import re
from collections import defaultdict
import numpy as np
from config import CELL_PIN_SEP, VERBOSE, CONNECTION_SEP
import copy

def extract_timing(sdf_file):
    """
    Extract timing information from .sdf file, which returns AT, RAT, Slew.
    Instance name maybe ugly like RAM\.MUX\.MUX\[21\]
    """
    with open(sdf_file) as f:
        c = f.read()
    atslew = extract_atslew(c)
    net_delay = extract_net_delay(c)
    cell_delay = extract_cell_delay(c)
    return atslew, net_delay, cell_delay


def extract_atslew(sdf_file_content):
    # (AT output52/A (0.216::0.381) (0.202::0.372))
    # (AT req_msg[0] (0.092::0.092) (0.092::0.092))
    # \w
    # .
    # [
    # ]
    # \
    # /
    # so this match above chars [\w\.\[\]\\\/]
    print("Extracting AT, RAT, SlEW from .sdf")
    p = re.compile(r'\((AT|RAT|SLEW) ([\w\.\[\]\\\/]*?) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\)\)')
    res = p.findall(sdf_file_content)
    atslew = {}
    for r in res:
        pin_name = r[1].replace('/',CELL_PIN_SEP).replace('\\', '')
        if pin_name in atslew.keys():
            pass
        else:
            atslew[pin_name] = {}
        atslew[pin_name.replace('\\', '')][r[0]] = [float(i) for i in r[2:]]
    return atslew


def extract_net_delay(sdf_file_content):
    # (INTERCONNECT req_msg[16] input8/A (0.000::0.000) (0.000::0.000))
    # (INTERCONNECT req_msg[16] input8/A (0.000::0.000))
    # \ maybe exists in this line
    # p = re.compile(r'INTERCONNECT ([\w\[\]\.\\\/]*?) ([\w\[\]\.\\\/]*?) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\)')
    print("Extracting net delay from .sdf")
    p = re.compile(r'\(INTERCONNECT.*?\n')
    p_float = re.compile(r'[+-]?\d*\.?\d+')
    res = p.findall(sdf_file_content)
    net_delay = {}
    for r in res:
        tmp = r.split(' ')
        cell_pin1 = tmp[1].replace('/',CELL_PIN_SEP).replace('\\', '')
        cell_pin2 = tmp[2].replace('/',CELL_PIN_SEP).replace('\\', '')

        numbers = ''.join(tmp[3:])
        numbers = p_float.findall(numbers)
        if len(numbers) < 4:
            if VERBOSE:
                print(f"interconnection delay for {cell_pin1}{CONNECTION_SEP}{cell_pin2} is not enough as 4 elements, only {len(numbers)}")
            if len(numbers) == 0:
                numbers = [0.0] * 4
            else:
                tmp = copy.copy(numbers)
                for i in range(4 - len(numbers)):
                    numbers.append(tmp[i % len(tmp)])


        key = cell_pin1 + CONNECTION_SEP + cell_pin2
        net_delay[key.replace('\\', '')] = [float(i) for i in numbers[0:4]]
    return dict(net_delay)


def extract_cell_delay(sdf_file_content):
    print("Extracting cell delay from .sdf")
    p = re.compile(r'\(CELLTYPE "(\w+)"\)\s+\(INSTANCE ([\w\.\[\]\\\/]*?)\)|IOPATH (\w+) (\w+) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\) \(([-+]?[0-9]*\.?[0-9]+)\:\:([-+]?[0-9]*\.?[0-9]+)\)')
    res = p.findall(sdf_file_content)
    cell = pin_src = pin_src = None
    ans = defaultdict(lambda: [])
    for r in res:
        if r[1] != '':
            cell = r[1]
        else:
            pin_src = cell + CELL_PIN_SEP + r[2]
            pin_dst = cell + CELL_PIN_SEP + r[3]
            ans[(pin_src + CONNECTION_SEP + pin_dst).replace('\\', '')].append([float(i) for i in list(r[4:])])
    for k in ans.keys():
        ans[k] = np.stack(ans[k], axis=0).mean(axis=0).tolist()
    return dict(ans)