'''
Extract one micron is how many units
Extract this from .def file
'''
import re

def extract_unit(def_file_path):
    '''
    Extract one micron is how many units
    Extract this from .def file
    '''
    print("Extracting units (one micron is how many units)")
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
