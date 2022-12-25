import src.extract_cell as extract_cell
import src.extract_inter_connection as extract_inter_connection
import src.get_PIPO as get_PIPO
import src.construct_graph as construct_graph
import src.get_timing_endpoint as get_timing_endpoint
import src.extract_cell_loc as extract_cell_loc
import src.extract_timing as extract_timing
import src.extract_lut as extract_lut
import src.pin_in_or_out as pin_in_or_out
import utils.utils as utils
from os.path import join
from collections import defaultdict
import dgl

if __name__ == "__main__":
    verilog_file = 'data\\6_final.v'
    sdc_file = 'data\\6_final.sdc'
    sdf_file = 'data\\6_final.sdf'
    def_file = 'data\\6_final.def'
    liberty_file = 'data\\NangateOpenCellLibrary_typical.lib'
    res_dir = 'res'

    utils.mkdir(res_dir)
    lut_info = extract_lut.extract_lut(liberty_file)

    pin_fanin_or_fanout = pin_in_or_out.get_pin_fanin_or_fanout(lut_info)

    cells = extract_cell.extract_cell(verilog_file)
    inter_connections = extract_inter_connection.extract_inter_connection(cells, pin_fanin_or_fanout)
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
    graph = construct_graph.construct_graph(cells, inter_connections, pin2index, pin_fanin_or_fanout)
    
    
    timing_endpoint = get_timing_endpoint.get_timing_endpoint(sdc_file)
    cell_locs = extract_cell_loc.extract_cell_loc(def_file)

    atslew, net_delay, cell_delay = extract_timing.extract_timing(sdf_file)



    utils.save_json(pin_fanin_or_fanout, join(res_dir, 'pin_fanin_or_fanout.json'))
    utils.save_json(atslew, join(res_dir, 'atslew.json'))
    utils.save_json(lut_info, join(res_dir, 'lut_info.json'))
    utils.save_json(net_delay, join(res_dir, 'net_delay.json'))
    utils.save_json(cell_delay, join(res_dir, 'cell_delay.json'))
    utils.save_json(pins, join(res_dir, 'pins.json'))
    utils.save_json(timing_endpoint, join(res_dir, 'timing_endpoint.json'))
    utils.save_json(pipos, join(res_dir, 'pipos.json'))
    utils.save_json(cells, join(res_dir, 'cells.json'))
    utils.save_json(pin2index, join(res_dir, 'pin2index.json'))
    utils.save_json(cell_locs, join(res_dir, 'cell_locs.json'))
    utils.save_json(inter_connections, join(res_dir, 'inter_connections.json'))

    graph = dgl.heterograph(graph)
    print(graph)