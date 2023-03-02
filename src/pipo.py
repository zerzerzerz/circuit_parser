'''
Extract all PI/PO and their location
PI/PO are ports of top-level module
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


def extract_pipo_loc(def_file_path):
    '''extract PIPO locations from .def file'''
    print("Extracting locations of PIPO from .def")
    with open(def_file_path) as f:
        c = f.read()
    
    p1 = re.compile(r'PINS\s*?\d+\s*?;([\s\S]*?)END PINS')
    c = p1.search(c).group(1)

    # - resp_val + NET resp_val + DIRECTION OUTPUT + USE SIGNAL
    #   + PORT
    #     + LAYER metal6 ( -140 -140 ) ( 140 140 )
    #     + PLACED ( 76350 139860 ) N ;
    p2 = re.compile(r'([\w\[\]\\\/]+)[\s\S]*?PLACED\s*?\(\s*?(\d+)\s*?(\d+)\s*?\)\s*?\w+\s*?;')
    res = p2.findall(c)
    res = [[i[0], float(i[1]), float(i[2])] for i in res]

    res = {
        i[0]:[i[1], i[2]] for i in res
    }

    res = {
        k: res[k] for k in sorted(res.keys())
    }

    return res


def get_PIPO_from_verilog(verilog_file_path) -> dict:
    '''
    extract PIPO from verilog file
    PI PO are ports of top level module
    '''
    raise NotImplementedError
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
    
