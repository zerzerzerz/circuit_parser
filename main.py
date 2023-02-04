from src import extract_cell
from src import get_PIPO
from src import construct_graph
from src import get_timing_endpoint
from src import extract_cell_loc
from src import extract_timing
from src import extract_lut
from src import extract_pipo_loc
from src import add_graph_feature
from src import get_pin2index 
from src import extract_chip_area
from src.utils import check_graph_data_range, merge_pin_loc
from src import extract_unit
from src import filterate_invalid_data
from src import check_loop
from os.path import join
from glob import glob

import dgl
import utils
import torch

def main(verilog_file, path_summary_file, sdf_file, def_file, liberty_files, res_dir):
    utils.mkdir(res_dir, rm=True)

    # extract information
    cells = extract_cell.extract_cell(verilog_file)
    utils.save_json(cells, join(res_dir, 'cells.json'))

    lut_info = extract_lut.extract_lut(liberty_files)
    utils.save_json(lut_info, join(res_dir, 'lut_info.json'))



    pipos = get_PIPO.get_PIPO(verilog_file)
    utils.save_json(pipos, join(res_dir, 'pipos.json'))

    unit = extract_unit.extract_unit(def_file)
    utils.save_json({"unit":unit}, join(res_dir, 'unit.json'))


    pin2index = get_pin2index.get_pin2index(cells, pipos)
    index2pin = {i:p for p,i in pin2index.items()}
    utils.save_json(pin2index, join(res_dir, 'pin2index.json'))
    utils.save_json(index2pin, join(res_dir, 'index2pin.json'))

    pipo_loc = extract_pipo_loc.extract_pipo_loc(def_file)
    utils.save_json(pipo_loc, join(res_dir, 'pipo_loc.json'))

    cell_locs = extract_cell_loc.extract_cell_loc(def_file)
    utils.save_json(cell_locs, join(res_dir, 'cell_locs.json'))

    all_pin_loc = merge_pin_loc(pipo_loc, cell_locs, pin2index)
    utils.save_json(all_pin_loc, join(res_dir, 'all_pin_loc.json'))
    

    timing_endpoint = get_timing_endpoint.get_timing_endpoint2(path_summary_file)
    utils.save_json(timing_endpoint, join(res_dir, 'timing_endpoint.json'))

    

    at_rat_slew, net_delay, cell_delay = extract_timing.extract_timing(sdf_file)
    utils.save_json(at_rat_slew, join(res_dir, 'at_rat_slew.json'))
    utils.save_json(net_delay, join(res_dir, 'net_delay.json'))
    utils.save_json(cell_delay, join(res_dir, 'cell_delay.json'))

    chip_area = extract_chip_area.extract_chip_area(def_file)
    utils.save_json(chip_area, join(res_dir, 'chip_area.json'))

    
    graph = construct_graph.construct_graph2(cell_delay.keys(), net_delay.keys(), pin2index)
    graph = add_graph_feature.add_graph_feature(
        graph,
        pin2index,
        net_delay,
        cell_delay,
        cells,
        lut_info,
        at_rat_slew,
        timing_endpoint,
        pipos,
        pipo_loc,
        chip_area,
        cell_locs,
        unit,
        all_pin_loc
    )

    graph = filterate_invalid_data.filterate_invalid_data(graph)


    # display information
    sep = '*'*100
    print(sep)
    print(graph)
    for ntype in graph.ntypes:
        print(sep)
        print(ntype)
        for k,v in graph.node_attr_schemes(ntype).items():
            print("{:<20} {}".format(k, str(v)))
    for etype in graph.etypes:
        print(sep)
        print(etype)
        for k,v in graph.edge_attr_schemes(etype).items():
            print("{:<20} {}".format(k, str(v)))
    print(sep)
    dgl.save_graphs(join(res_dir,'graph.bin'),[graph])

    n_src, n_dst = graph.edges(etype='net_out')
    c_src, c_dst = graph.edges(etype='cell_out')
    g_tmp = dgl.graph((
        torch.cat([n_src, c_src]),
        torch.cat([n_dst, c_dst]),
    ))
    # dgl.topological_nodes_generator(g_tmp)
    loop_point = check_loop.check_loop(g_tmp, index2pin)
    if len(loop_point) == 0:
        print("Topological sort OK! No loop!")
    else:
        print("Loop!")
        # print(loop_point)
        check_loop.find_a_loop(g_tmp, index2pin)
    

    check_graph_data_range(graph)


if __name__ == "__main__":
    # settings
    data_dir = 'data'
    verilog_file = join(data_dir, '6_final.v')
    path_summary_file = join(data_dir, 'path_summary.log')
    sdf_file = join(data_dir, '6_final.sdf')
    def_file = join(data_dir, '6_final.def')
    liberty_files = glob(join(data_dir, '*.lib'))
    res_dir = 'res'

    main(verilog_file, path_summary_file, sdf_file, def_file, liberty_files, res_dir)
    
    