import src
import dgl
import utils
import torch
from os.path import join
from glob import glob
from config import TOPO



def main(primary_input_file, primary_output_file, path_summary_file, sdf_file, def_file, liberty_files, res_dir):
    utils.mkdir(res_dir, rm=True)

    at_rat_slew, net_delay, cell_delay, cell_name_to_cell_class = src.extract_timing(sdf_file)
    utils.save_json(at_rat_slew, join(res_dir, 'at_rat_slew.json'))
    utils.save_json(net_delay, join(res_dir, 'net_delay.json'))
    utils.save_json(cell_delay, join(res_dir, 'cell_delay.json'))
    utils.save_json(cell_name_to_cell_class, join(res_dir, 'cell_name_to_cell_class.json'))


    pipos = src.get_PIPO(primary_input_file, primary_output_file)
    utils.save_json(pipos, join(res_dir, 'pipos.json'))


    pin2index = src.get_pin2index(net_delay, cell_delay)
    index2pin = src.get_index2pin(pin2index)
    utils.save_json(pin2index, join(res_dir, 'pin2index.json'))
    utils.save_json(index2pin, join(res_dir, 'index2pin.json'))


    lut_info = src.extract_lut(liberty_files)
    utils.save_json(lut_info, join(res_dir, 'lut_info.json'))


    unit = src.extract_unit(def_file)
    utils.save_json({"unit":unit}, join(res_dir, 'unit.json'))


    pipo_loc = src.extract_pipo_loc(def_file)
    utils.save_json(pipo_loc, join(res_dir, 'pipo_loc.json'))


    cell_locs = src.extract_cell_loc(def_file)
    utils.save_json(cell_locs, join(res_dir, 'cell_locs.json'))


    all_pin_loc = src.merge_pin_loc(pipo_loc, cell_locs, pin2index)
    utils.save_json(all_pin_loc, join(res_dir, 'all_pin_loc.json'))
    

    timing_endpoint = src.get_timing_endpoint_from_STA_report(path_summary_file)
    utils.save_json(timing_endpoint, join(res_dir, 'timing_endpoint.json'))


    chip_area = src.extract_chip_area(def_file)
    utils.save_json(chip_area, join(res_dir, 'chip_area.json'))

    
    graph = src.construct_graph(cell_delay.keys(), net_delay.keys(), pin2index)
    graph = src.add_graph_feature(
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


    graph = src.filterate_invalid_data(graph)
    src.display_graph(graph)
    src.check_graph_data_range(graph)
    dgl.save_graphs(join(res_dir,'graph.bin'),[graph])
    src.display_extracted_information(
        at_rat_slew = at_rat_slew,
        net_delay = net_delay,
        cell_delay = cell_delay,
        cell_name_to_cell_class = cell_name_to_cell_class,
        pi = pipos["PI"],
        po = pipos["PO"],
        pin2index = pin2index,
        index2pin = index2pin,
        lut_info = lut_info,
        unit = unit,
        pipo_loc = pipo_loc,
        cell_locs = cell_locs,
        all_pin_loc = all_pin_loc,
        timing_endpoint = timing_endpoint,
        chip_area = chip_area,
    )

    g_homo = src.topo.create_homo_graph(graph)
    topo_flag = src.check_topo(g_homo)
    if topo_flag == TOPO.success:
        print(f'topo sort success')
    elif topo_flag == TOPO.has_loop:
        for loop in src.FindAllLoop(g_homo).run():
            print(loop)
    elif topo_flag == TOPO.odd_level:
        print('odd level')



if __name__ == "__main__":
    # settings
    data_dir = 'data'
    res_dir = 'res'

    primary_input_file = join(data_dir, 'primary_input')
    primary_output_file = join(data_dir, 'primary_output')
    STA_path_summary_file = join(data_dir, 'path_summary.log')
    sdf_file = join(data_dir, '6_final.sdf')
    def_file = join(data_dir, '6_final.def')
    liberty_files = glob(join(data_dir, '*.lib'))

    main(primary_input_file, primary_output_file, STA_path_summary_file, sdf_file, def_file, liberty_files, res_dir)
    
    