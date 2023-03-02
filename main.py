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
from src.utils import check_graph_data_range, display_graph, merge_pin_loc
from src import extract_unit
from src import filterate_invalid_data
from src import check_topo
from src import extract_connections_from_sdf
from os.path import join
from glob import glob

import argparse
import dgl
import utils
import torch

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", default=False)
    args = parser.parse_args()
    return args


def main(primary_input_file, primary_output_file, path_summary_file, sdf_file, def_file, liberty_files, res_dir):
    utils.mkdir(res_dir, rm=True)

    at_rat_slew, net_delay, cell_delay = extract_timing.extract_timing(sdf_file)
    utils.save_json(at_rat_slew, join(res_dir, 'at_rat_slew.json'))
    utils.save_json(net_delay, join(res_dir, 'net_delay.json'))
    utils.save_json(cell_delay, join(res_dir, 'cell_delay.json'))

    inter_connections, inner_connections = extract_connections_from_sdf.extract_connections_from_sdf(sdf_file)
    utils.save_json(inter_connections, join(res_dir, 'inter_connections.json'))
    utils.save_json(inner_connections, join(res_dir, 'inner_connections.json'))


    print("Constructing mapping from cell name to cell type")
    cell_name_to_cell_class = {}
    for item in inner_connections:
        cell_name_to_cell_class[item["cell_name"]] = item["cell_type"]
    utils.save_json(cell_name_to_cell_class, join(res_dir, 'cell_name_to_cell_class.json'))
    


    pipos = get_PIPO.get_PIPO(primary_input_file, primary_output_file)
    utils.save_json(pipos, join(res_dir, 'pipos.json'))


    pin2index = get_pin2index.get_pin2index(net_delay, cell_delay)
    index2pin = {i:p for p,i in pin2index.items()}
    utils.save_json(pin2index, join(res_dir, 'pin2index.json'))
    utils.save_json(index2pin, join(res_dir, 'index2pin.json'))


    lut_info = extract_lut.extract_lut(liberty_files)
    utils.save_json(lut_info, join(res_dir, 'lut_info.json'))


    unit = extract_unit.extract_unit(def_file)
    utils.save_json({"unit":unit}, join(res_dir, 'unit.json'))


    pipo_loc = extract_pipo_loc.extract_pipo_loc(def_file)
    utils.save_json(pipo_loc, join(res_dir, 'pipo_loc.json'))

    cell_locs = extract_cell_loc.extract_cell_loc(def_file)
    utils.save_json(cell_locs, join(res_dir, 'cell_locs.json'))

    all_pin_loc = merge_pin_loc(pipo_loc, cell_locs, pin2index)
    utils.save_json(all_pin_loc, join(res_dir, 'all_pin_loc.json'))
    

    timing_endpoint = get_timing_endpoint.get_timing_endpoint_from_STA_report(path_summary_file)
    utils.save_json(timing_endpoint, join(res_dir, 'timing_endpoint.json'))


    chip_area = extract_chip_area.extract_chip_area(def_file)
    utils.save_json(chip_area, join(res_dir, 'chip_area.json'))

    
    graph = construct_graph.construct_graph(cell_delay.keys(), net_delay.keys(), pin2index)
    graph = add_graph_feature.add_graph_feature(
        graph,
        pin2index,
        net_delay,
        cell_delay,
        cell_name_to_cell_class,
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
    display_graph(graph)
    check_graph_data_range(graph)
    check_topo.check_topo(graph)
    dgl.save_graphs(join(res_dir,'graph.bin'),[graph])



if __name__ == "__main__":
    # settings
    data_dir = 'data'
    primary_input_file = join(data_dir, 'primary_input')
    primary_output_file = join(data_dir, 'primary_output')
    STA_path_summary_file = join(data_dir, 'path_summary.log')
    sdf_file = join(data_dir, '6_final.sdf')
    def_file = join(data_dir, '6_final.def')
    liberty_files = glob(join(data_dir, '*.lib'))
    res_dir = 'res'

    main(primary_input_file, primary_output_file, STA_path_summary_file, sdf_file, def_file, liberty_files, res_dir)
    
    