from config import CELL_PIN_SEP, VERBOSE
import torch
import dgl

def merge_pin_loc(pipo_loc, cell_locs, pin2index):
    '''merge all locations of PI, PO and pins'''
    print("Merging all locations of PI, PO and pins")
    res = {}
    for pipo, loc_xy in pipo_loc.items():
        res[pipo] = loc_xy
    
    for pin_name in pin2index.keys():
        # this is a pin of cell
        if CELL_PIN_SEP in pin_name:
            cell_name, _ = pin_name.split(CELL_PIN_SEP)
            try:
                cell_loc_xy = cell_locs[cell_name]["location"]
            except:
                cell_loc_xy = [.0, .0]
                if VERBOSE:
                    print(f"pin {pin_name} does not have location")
                    
            res[pin_name] = cell_loc_xy
    res = {
        k: res[k] for k in sorted(res.keys())
    }
    return res


def display_graph(graph:dgl.heterograph):
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


def check_graph_data_range(g:dgl.DGLHeteroGraph, n_dim=16, statistics:str='mean'):
    for t in sorted(g.ntypes):
        for k in sorted(g.node_attr_schemes(t)):
            data = g.nodes[t].data[k]
            if len(data.shape) == 1:
                data.unsqueeze_(-1)

            if statistics == 'mean':
                data = data[:,0:n_dim].mean(dim=0).tolist()
            elif statistics == 'max':
                data = data[:,0:n_dim].max(dim=0).tolist()
            elif statistics == 'min':
                data = data[:,0:n_dim].min(dim=0).tolist()
            else:
                raise NotImplementedError

            data = map(lambda x:round(x,3), data)
            data = str(list(data))
            print("{:<10} {:<18} {:<}".format(t,k,data))
    
    for t in sorted(g.etypes):
        for k in sorted(g.edge_attr_schemes(t)):
            data = g.edges[t].data[k]
            if len(data.shape) == 1:
                data.unsqueeze_(-1)

            if statistics == 'mean':
                data = data[:,0:n_dim].mean(dim=0).tolist()
            elif statistics == 'max':
                data = data[:,0:n_dim].max(dim=0).tolist()
            elif statistics == 'min':
                data = data[:,0:n_dim].min(dim=0).tolist()
            else:
                raise NotImplementedError

            data = map(lambda x:round(x,3), data)
            data = str(list(data))
            print("{:<10} {:<18} {:<}".format(t,k,data))
