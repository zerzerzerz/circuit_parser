from config.config import CONNECTION_SEP
from collections import defaultdict

def check_fanin_or_fanout(lut_info):
    print("Extracting whether a pin is fanin or fanout")
    res = defaultdict(lambda : {})
    for cell_class in lut_info.keys():
        for pin in lut_info[cell_class].keys():
            res[cell_class][pin] = lut_info[cell_class][pin]['direction']
    return res
