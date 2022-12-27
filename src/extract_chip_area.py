import re
from config.config import CONNECTION_SEP

def extract_chip_area(def_file):
    print("Extracting chip area")
    with open(def_file) as f:
        c = f.read()
    p = re.compile(r'DIEAREA \( (\d+) (\d+) \) \( (\d+) (\d+) \) ;')
    res = p.search(c)
    ans = []
    for i in range(1,1+4):
        ans.append(float(res.group(i)))
    return ans