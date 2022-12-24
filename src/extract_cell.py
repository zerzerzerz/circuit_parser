import re
import utils.utils as utils

def extract_cell(verilog_file_path:str) -> list:
    PIPO = ['input', 'output']
    OTHERS = ['module', 'endmodule']

    with open(verilog_file_path) as f:
        circuit = f.read().replace('\n','')

    cell_pattern = re.compile(r'(\w+)\s+(\w+)\s+\((.*?)\)\s*;')
    cells = cell_pattern.findall(circuit)
    res = []
    for cell in cells:
        header = cell[0]
        if header in OTHERS + PIPO:
            continue
        cell_class = cell[0]
        cell_name = cell[1]
        pins = []
        if len(cell[-1]) > 0:
            for pin in cell[-1].split(','):
                pin = pin.strip('\n\t ')
                tmp = pin.split('(')
                pin_name = tmp[0][1:].strip('\n\t ')
                pin_instance = tmp[1][0:-1].strip('\n\t ')
                pins.append([pin_name, pin_instance])
            res.append({
                "cell_class": cell_class,
                "cell_name": cell_name,
                "pins": pins
            })
    return res