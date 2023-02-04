"""
Extract all cells from verilog file (.v)
"""
import re

def extract_cell(verilog_file_path:str) -> list:
    '''extract all cells from verilog file'''

    print("Extracting basic cell information")

    # NAND2_X1 _507_ ( .A1 ( _125_ ) , .A2 ( \dpath.a_lt_b$in0[15] ) , .ZN ( _178_ ) ) ;
    PIPO = ['input', 'output']
    OTHERS = ['module', 'endmodule']

    with open(verilog_file_path) as f:
        circuit = f.read().replace('\n','')

    cell_pattern = re.compile(r'(\w+)\s+(\w+)\s*\(([\s\S]*?)\)\s*;')
    cells = cell_pattern.findall(circuit)

    res = {}

    for cell in cells:
        cell_class = cell[0]
        if cell_class in OTHERS:
            print("Matching top module, continue")
            continue
        if cell_class in PIPO:
            print("Matching IO statement, continue")
            continue

        argument_list = cell[2]
        if '{' in argument_list:
            print("{ is in argument list, I cannot process such case, ignore this cell")
            continue

        cell_name = cell[1]
        pins = []

        argument_list = re.sub(r'\s', '', argument_list)
        
        if len(argument_list) > 0:
            for pin in argument_list.split(','):
                # tmp splits .A1(_125_)
                tmp = pin.split('(')
                pin_name = tmp[0][1:]
                connected_wire = tmp[1][0:-1]
                if '\\' in connected_wire:
                    # print(f'\\ is in wire {connected_wire}, remove it')
                    connected_wire = connected_wire.replace('\\', '')
                pins.append({
                    "pin_name": pin_name,
                    "connected_wire": connected_wire,
                })
            res[cell_name] = {
                "cell_class": cell_class,
                "pins": pins
            }
    return res