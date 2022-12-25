import re
import utils.utils as utils
import numpy as np
from einops import repeat

def extract_lut(liberty_file):
    with open(liberty_file) as f:
        c = f.read()
    p = re.compile(r'cell\s\((\w+)\)\s\{')
    ans = {}
    res = True
    while res is not None:
        res = p.search(c)
        if res is not None:
            cell_type = res.group(1)
            j = res.span()[1]
            s = 1
            while s != 0:
                if c[j] == '}':
                    s -= 1
                elif c[j] == '{':
                    s += 1
                else:
                    pass
                j += 1
            
            cell_info = extract_lut_sub(c[res.span()[0]:j], cell_type)
            ans[cell_type] = cell_info
            c = c[j+1:]
    return ans
    

def extract_lut_sub(cell_file, cell_type):
    c = cell_file
    p = re.compile(r'pin \((\w+)\) \{')
    res = True
    pins = []
    while res is not None:
        res = p.search(c)
        if res is None:
            break
        else:
            s = 1
            i = res.span()[1]
            while s != 0:
                if c[i] == '{':
                    s += 1
                elif c[i] == '}':
                    s -= 1
                else:
                    pass
                i += 1
            pin = c[res.span()[0]: i]
            c = c[i:]
            pins.append((res.group(1), pin))


    p_direction = re.compile(r'direction\s*\:\s*(\w+);')
    p_capacitance = re.compile(r'(max_capacitance|capacitance)\s*\:\s*([-+]?\d*\.?\d+);')

    ans = {}
    for pin_name, pin in pins:
        direction = p_direction.search(pin).group(1)
        if direction not in ['input', 'output']:
            continue
        cap = p_capacitance.search(pin)
        if cap is None:
            cap = 0.0
        else:
            cap = cap.group(2)
        # print(cap)
        ans[pin_name] = {
            "direction": direction,
            "capacitance": cap,
        }
        if direction == 'input':
            pass
        elif direction == 'output':
            ans[pin_name]['luts'] = {}
            res = True
            c = pin
            p_timing = re.compile(r'timing \(\) \{')
            while res is not None:
                res = p_timing.search(c)
                if res is None:
                    break
                else:
                    i = res.span()[1]
                    s = 1
                    while s != 0:
                        if c[i] == '{':
                            s += 1
                        elif c[i] == '}':
                            s -= 1
                        else:
                            pass
                        i += 1
                    timing = c[res.span()[0]: i]
                    c = c[i:]

                    related_pin = re.search(r'related_pin\s*?\:\s*?\"(\w+)\";', timing).group(1)
                    ans[pin_name]['luts'][related_pin] = []
                    luts = re.findall(r'\w+\s*\(\w+\)\s*\{([\s\S]*?)\}', timing)
                    for lut in luts:
                        lut = lut.replace(' ','')
                        lut = lut.replace('\n','')
                        lut = lut.replace('\t','')
                        lut = lut.replace('\\','')

                        lut_split = lut.split(';')
                        if len(lut_split) == 4:
                            index1, index2, values, _ = lut_split
                            index1 = [float(i) for i in index1.split('\"')[1].split(',')]
                            index2 = [float(i) for i in index2.split('\"')[1].split(',')]
                            values = np.array([float(i) for i in values.replace('\"','')[7:-2].split(',')]).reshape(len(index1), len(index2)).tolist()
                        elif len(lut_split) == 2:
                            values, _ = lut_split
                            index1 = [0.0 for i in range(7)]
                            index2 = [0.0 for i in range(7)]
                            tmp = float(re.search(r'[-+]?\d*\.?\d+',values).group())
                            values = np.array([tmp for i in range(7*7)]).reshape(len(index1), len(index2)).tolist()
                        elif len(lut_split) == 3:
                            index1, values, _ = lut_split
                            index1 = [float(i) for i in index1.split('\"')[1].split(',')]
                            index2 = [0.0 for i in range(len(index1))]
                            values = [float(i) for i in values.split('\"')[1].split(',')]
                            values = np.array([values]).reshape(-1,1)
                            values = repeat(values,'a 1 -> a b', b=len(index2))


                        else:
                            raise RuntimeError
                        ans[pin_name]['luts'][related_pin].append({
                            "index1": index1,
                            "index2": index2,
                            "values": values
                        })

        else:
            pass
    return ans
