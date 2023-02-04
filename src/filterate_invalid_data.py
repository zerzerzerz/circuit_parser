"""
Set the values which fall out of valid range to 0
"""
import dgl
import torch
from config.config import IGNORED_KEYS_FOR_FILTERATING_INVALID_DATA

def filterate_invalid_data(g:dgl.heterograph):
    print(f"Filterating invalid data")

    # process AT and slew
    is_too_large = torch.abs(g.ndata['n_ats']) > 1e20
    is_nan = torch.isnan(g.ndata['n_ats'])
    is_inf = torch.isinf(g.ndata['n_ats'])
    invalid_pins = torch.logical_or(is_too_large, is_nan)
    invalid_pins = torch.logical_or(invalid_pins, is_inf)
    g.ndata['n_ats'][invalid_pins] = 0.0
    g.ndata['n_slews'][invalid_pins] = 0.0

    # process node features
    for t in g.ntypes:
        for k in g.node_attr_schemes(t).keys():
            if k in IGNORED_KEYS_FOR_FILTERATING_INVALID_DATA:
                continue
            else:
                is_nan = torch.isnan(g.nodes[t].data[k])
                is_inf = torch.isinf(g.nodes[t].data[k])
                is_too_large = g.nodes[t].data[k].abs() > 1e20

                invalid = torch.logical_or(is_nan, is_inf)
                invalid = torch.logical_or(invalid, is_too_large)

                if invalid.any():
                    print("{:<20} {:<20} {:<20.6f}".format(str(t), str(k), (invalid.sum()/invalid.nelement()).item()))
                    g.nodes[t].data[k][invalid] = 0.0
                else:
                    pass
    
    # process edge features
    for t in g.etypes:
        for k in g.edge_attr_schemes(t).keys():
            if k in IGNORED_KEYS_FOR_FILTERATING_INVALID_DATA:
                continue
            else:
                is_nan = torch.isnan(g.edges[t].data[k])
                is_inf = torch.isinf(g.edges[t].data[k])
                is_too_large = g.edges[t].data[k].abs() > 1e20

                invalid = torch.logical_or(is_nan, is_inf)
                invalid = torch.logical_or(invalid, is_too_large)
                
                if invalid.any():
                    print("{:<20} {:<20} {:<20.6f}".format(str(t), str(k), (invalid.sum()/invalid.nelement()).item()))
                    g.edges[t].data[k][invalid] = 0.0
                else:
                    pass
    return g