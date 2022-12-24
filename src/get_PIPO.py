import re
from utils.utils import save_json

def get_PIPO(verilog_file_path) -> dict:
    with open(verilog_file_path) as f:
        circuit = f.read()

    circuit = circuit.replace('\n', '')
    pi_pattern = re.compile(r'(input\s.*?);')
    po_pattern = re.compile(r'(output\s.*?);')
    res = {}

    pis = pi_pattern.findall(circuit)
    pos = po_pattern.findall(circuit)
    # print(pis)
    # print(pos)

    def func(io):
        res = []
        for item in io:
            tmp = item.split(' ')
            if len(tmp) == 2:
                res.append(tmp[-1])
            elif len(tmp) == 3:
                tmp2 = tmp[1].split(':')
                a = int(tmp2[0][1:])
                b = int(tmp2[1][:-1])
                if a>b:
                    r = range(b,a+1)
                else:
                    r = range(a,b+1)
                for i in r:
                    res.append(f'{tmp[-1]}[{i}]')
            else:
                raise RuntimeError
        return res
    
    res['PI'] = func(pis)
    res['PO'] = func(pos)
    save_json(res, 'PIPO.json')
    return res
    
