from ctypes import util
import src.extract_cell as extract_cell
import src.extract_inter_connection as extract_inter_connection
import src.get_PIPO as get_PIPO
import utils.utils as utils

if __name__ == "__main__":
    verilog_file = 'data\\6_final.v'


    cells = extract_cell.extract_cell(verilog_file)
    inter_connections = extract_inter_connection.extract_inter_connection(cells)
    pipos = get_PIPO.get_PIPO(verilog_file)


    pins = []
    pins.extend(pipos['PI'])
    pins.extend(pipos['PO'])
    for cell in cells:
        cell_name = cell['cell_name']
        for pin in cell['pins']:
            pin_name = f'{cell_name}.{pin[0]}'
            pins.append(pin_name)
    pin2index = {k:v for v,k in enumerate(pins)}


    utils.save_json(pins, 'pins.json')
    utils.save_json(pin2index, 'pin2index.json')


