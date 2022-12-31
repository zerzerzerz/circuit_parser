import re

def extract_unit(def_file_path):
    with open(def_file_path) as f:
        c = f.read()

    # UNITS DISTANCE MICRONS 2000 ;
    p = re.compile(r'UNITS\s*DISTANCE\s*MICRONS\s*\"?([+-]?\d*\.?\d+)\"?\s*;')
    unit = p.search(c)
    if unit is None:
        raise RuntimeError(f'{def_file_path} does not have unit')
    else:
        res = float(unit.group(1))
    return res
