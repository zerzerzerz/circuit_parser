import re
def extract_cell_loc(def_path):
    with open(def_path) as f:
        content = f.read()

        pattern = re.compile(r'- (\w+) (\w+)[\s\S]*? (PLACED|FIXED|COVER) \( (\d+) (\d+) \) \w+ ;')
        content = pattern.findall(content)

        return content

if __name__ == "__main__":
    print(extract_cell_loc('data\\6_final.def'))