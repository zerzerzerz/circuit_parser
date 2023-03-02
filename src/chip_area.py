"""Extract chip area from .def file"""
import re

def extract_chip_area(def_file):
    """Extract chip area from .def file"""
    print("Extracting chip area from .def")
    with open(def_file) as f:
        c = f.read()
    p = re.compile(r'DIEAREA \( (\d+) (\d+) \) \( (\d+) (\d+) \) ;')
    res = p.search(c)
    ans = []
    for i in range(1,1+4):
        ans.append(float(res.group(i)))
    return ans