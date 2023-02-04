"""
Extract location of each cell from .def file
"""
import re

def extract_cell_loc(def_path):
    """
    Extract location of each cell from .def file
    """
    print("Extracting cell location to replace pin location")
    with open(def_path) as f:
        content = f.read()

        pattern = re.compile(r'- (\w+) (\w+)[\s\S]*? (PLACED|FIXED|COVER) \( (\d+) (\d+) \) \w+ ;')
        # pattern = re.compile(r'\-\s*(\w+)\s*(\w+)[\s\S]*?(PLACED|FIXED|COVER)\s*\(\s*(\d+)\s*(\d+)\s*\)\s*\w+\s*;')
        content = pattern.findall(content)
        # content = [[c[0], c[1], c[2], float(c[3]), float(c[4])] for c in content]
        content = {
            c[0]:{
                "cell_class": c[1],
                "location_type": c[2],
                "location": [float(c[3]), float(c[4])]
            } for c in content
        }
        return content

if __name__ == "__main__":
    print(extract_cell_loc('data\\6_final.def'))