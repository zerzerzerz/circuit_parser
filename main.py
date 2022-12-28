import src.extract_cell as extract_cell
import src.get_PIPO as get_PIPO
import src.construct_graph as construct_graph
import src.get_timing_endpoint as get_timing_endpoint
import src.extract_cell_loc as extract_cell_loc
import src.extract_timing as extract_timing
import src.extract_lut2 as extract_lut
import src.extract_pipo_loc as extract_pipo_loc
import src.add_graph_feature as add_graph_feature
import src.get_pin2index as get_pin2index
import src.extract_chip_area as extract_chip_area
import src.check_fanin_or_fanout as check_fanin_or_fanout
import src.extract_net_connection as extract_net_connection
import src.extract_cell_connection as extract_cell_connection
import utils.utils as utils
from os.path import join
import dgl

def main(verilog_file, sdc_file, sdf_file, def_file, liberty_files, res_dir):
    utils.mkdir(res_dir, rm=False)

    # extract information
    cells = extract_cell.extract_cell(verilog_file)
    utils.save_json(cells, join(res_dir, 'cells.json'))

    lut_info = extract_lut.extract_lut(liberty_files)
    utils.save_json(lut_info, join(res_dir, 'lut_info.json'))

    fanin_or_fanout = check_fanin_or_fanout.check_fanin_or_fanout(lut_info)
    utils.save_json(fanin_or_fanout, join(res_dir, 'fanin_or_fanout.json'))

    net_connections = extract_net_connection.extract_net_connection(cells, fanin_or_fanout)
    utils.save_json(net_connections, join(res_dir, 'net_connections.json'))

    pipos = get_PIPO.get_PIPO(verilog_file)
    utils.save_json(pipos, join(res_dir, 'pipos.json'))

    net_out = extract_net_connection.extract_net_out(net_connections, pipos)
    utils.save_json(net_out, join(res_dir, 'net_out.json'))

    cell_out = extract_cell_connection.extract_cell_connection(cells, lut_info)
    utils.save_json(cell_out, join(res_dir, 'cell_out.json'))


    exit()

    pin2index = get_pin2index.get_pin2index(cells, pipos)
    index2pin = {i:p for p,i in pin2index.items()}
    utils.save_json(pin2index, join(res_dir, 'pin2index.json'))
    utils.save_json(index2pin, join(res_dir, 'index2pin.json'))

    pipo_loc = extract_pipo_loc.extract_pipo_loc(def_file)
    utils.save_json(pipo_loc, join(res_dir, 'pipo_loc.json'))


    timing_endpoint = get_timing_endpoint.get_timing_endpoint(sdc_file)
    utils.save_json(timing_endpoint, join(res_dir, 'timing_endpoint.json'))

    cell_locs = extract_cell_loc.extract_cell_loc(def_file)
    utils.save_json(cell_locs, join(res_dir, 'cell_locs.json'))

    at_rat_slew, net_delay, cell_delay = extract_timing.extract_timing(sdf_file)
    utils.save_json(at_rat_slew, join(res_dir, 'at_rat_slew.json'))
    utils.save_json(net_delay, join(res_dir, 'net_delay.json'))
    utils.save_json(cell_delay, join(res_dir, 'cell_delay.json'))

    chip_area = extract_chip_area.extract_chip_area(def_file)
    utils.save_json(chip_area, join(res_dir, 'chip_area.json'))

    


    # construct graph and add feature
    graph = construct_graph.construct_graph(cell_delay, net_delay, pin2index)
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
        cell_locs
    )


    # display information
    sep = '*'*50
    print(sep)
    print(graph)
    for ntype in graph.ntypes:
        print(sep)
        print(ntype)
        for k,v in graph.node_attr_schemes(ntype).items():
            print(k,v)
    for etype in graph.etypes:
        print(sep)
        print(etype)
        for k,v in graph.edge_attr_schemes(etype).items():
            print(k,v)
    print(sep)
    dgl.save_graphs(join(res_dir,'graph.bin'),[graph])


if __name__ == "__main__":
    # settings
    verilog_file = 'data\\6_final.v'
    sdc_file = 'data\\6_final.sdc'
    sdf_file = 'data\\6_final.sdf'
    def_file = 'data\\6_final.def'
    liberty_file = 'data\\NangateOpenCellLibrary_typical.lib'
    res_dir = 'res'

    main(verilog_file, sdc_file, sdf_file, def_file, [liberty_file], res_dir)
    
    