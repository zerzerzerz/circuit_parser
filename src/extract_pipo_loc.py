'''extract PIPO locations from .def file'''
import re
from config.config import CONNECTION_SEP

def extract_pipo_loc(def_file_path):
    '''extract PIPO locations from .def file'''
    print("Extracting locations of PIPO")
    with open(def_file_path) as f:
        c = f.read()
    
    p1 = re.compile(r'PINS\s*?\d+\s*?;([\s\S]*?)END PINS')
    c = p1.search(c).group(1)
    # print(c)
    p2 = re.compile(r'([\w\[\]]+)[\s\S]*?PLACED\s*?\(\s*?(\d+)\s*?(\d+)\s*?\)\s*?\w+\s*?;')
    res = p2.findall(c)
    # return res
    res = [[i[0], float(i[1]), float(i[2])] for i in res]
    # return res

    res = {
        i[0]:[i[1], i[2]] for i in res
    }

    return res
    