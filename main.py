import src.extract_cell as extract_cell
import src.extract_inter_connection as extract_inter_connection
import src.get_PIPO as get_PIPO
import src.construct_graph as construct_graph
import utils.utils as utils
from os.path import join
import dgl

if __name__ == "__main__":
    verilog_file = 'data\\6_final.v'
    res_dir = 'res'

    utils.mkdir(res_dir)
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
    graph = construct_graph.construct_graph(cells, inter_connections, pin2index)


    utils.save_json(pins, join(res_dir, 'pins.json'))
    # utils.save_json(graph, join(res_dir, 'graph.json'))
    utils.save_json(pipos, join(res_dir, 'pipos.json'))
    utils.save_json(cells, join(res_dir, 'cells.json'))
    utils.save_json(pin2index, join(res_dir, 'pin2index.json'))
    utils.save_json(inter_connections, join(res_dir, 'inter_connections.json'))

    graph = dgl.heterograph(graph)
    print(graph)