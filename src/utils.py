from config.config import CELL_PIN_SEP
import torch
import dgl

def merge_pin_loc(pipo_loc, cell_locs, pin2index):
    '''merge all locations of PI, PO and pins'''
    res = {}
    for pipo, loc_xy in pipo_loc.items():
        res[pipo] = loc_xy
    
    for pin_name in pin2index.keys():
        # this is a pin of cell
        if CELL_PIN_SEP in pin_name:
            cell_name, _ = pin_name.split(CELL_PIN_SEP)
            cell_loc_xy = cell_locs[cell_name]["location"]
            res[pin_name] = cell_loc_xy
    return res


def check_graph_is_invalid(g:dgl.DGLHeteroGraph):
    for t in g.ntypes:
        for k in g.node_attr_schemes(t).keys():
            data = g.nodes[t].data[k]

            invalid = torch.isinf(data)
            invalid = torch.logical_or(invalid, torch.isnan(data))
            invalid = torch.logical_or(invalid, data.abs()>1e20)
            
            if invalid.any():
                print("{:<20} {:<20} {:<.6f}".format(t,k,(invalid.sum()/invalid.nelement()).item()))
    
    for t in g.etypes:
        for k in g.edge_attr_schemes(t).keys():
            data = g.edges[t].data[k]

            invalid = torch.isinf(data)
            invalid = torch.logical_or(invalid, torch.isnan(data))
            invalid = torch.logical_or(invalid, data.abs()>1e20)
            
            if invalid.any():
                print("{:<20} {:<20} {:<.6f}".format(t,k,(invalid.sum()/invalid.nelement()).item()))