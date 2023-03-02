'''
Extract PIPO from verilog file.
PI PO are ports of top level module.
'''

import re

def get_PIPO(primary_input_file, primary_output_file) -> dict:
    def read_from_file(file) -> list:
        p = re.compile(r"\s")
        ans = []
        with open(file) as f:
            for line in f.readlines():
                line = p.sub('', line)
                if line != "":
                    ans.append(line)
        return sorted(ans)
    
    ans = {}
    ans['PI'] = read_from_file(primary_input_file)
    ans['PO'] = read_from_file(primary_output_file)
    return ans


def get_PIPO_from_verilog(verilog_file_path) -> dict:
    '''
    extract PIPO from verilog file
    PI PO are ports of top level module
    '''
    print("Extracting which pins are PIPO from .v")
    with open(verilog_file_path) as f:
        circuit = f.read()

    circuit = circuit.replace('\n', '')
    pi_pattern = re.compile(r'(input\s.*?);')
    po_pattern = re.compile(r'(output\s.*?);')
    res = {}

    pis = pi_pattern.findall(circuit)
    pos = po_pattern.findall(circuit)

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
    return res
    
