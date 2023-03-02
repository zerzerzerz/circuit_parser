'''extract PIPO locations from .def file'''
import re
from config import CONNECTION_SEP

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

    return res
    