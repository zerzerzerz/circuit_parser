import re

def extract_cell(verilog_file_path:str) -> list:
    '''extract all cells from verilog file'''

    print("Extracting basic cell information")

    PIPO = ['input', 'output']
    OTHERS = ['module', 'endmodule']

    with open(verilog_file_path) as f:
        circuit = f.read().replace('\n','')

    cell_pattern = re.compile(r'(\w+)\s+(\w+)\s+\(([\s\S]*?)\)\s*;')
    cells = cell_pattern.findall(circuit)
    res = {}
    for cell in cells:
        header = cell[0]
        if header in OTHERS + PIPO:
            continue
        cell_class = cell[0]
        cell_name = cell[1]
        if '{' in cell[2]:
            print("Ignore macro")
            continue
        pins = []
        if len(cell[-1]) > 0:
            for pin in cell[-1].split(','):
                pin = pin.strip('\n\t ')
                tmp = pin.split('(')
                pin_name = tmp[0][1:].strip('\n\t ')
                connected_wire = tmp[1][0:-1].strip('\n\t ')
                pins.append({
                    "pin_name": pin_name,
                    "connected_wire": connected_wire,
                })
            res[cell_name] = {
                "cell_class": cell_class,
                "pins": pins
            }
    return res