import dgl
import torch
import tqdm

def add_graph_feature(
    g,
    pin2index,
    net_delay,
):
    '''
    node:
        n_rats: 4x
        n_ats: 4x
        n_slews: 4x
        nf: 10x
            primary or not: 1x
            fanin or fanout: 1x
            location: 4x
            capacitance: 4x
        n_net_delays: 4x
        n_is_timing_endpt: 1x
    
    cell_out:
        ef: 512x
        e_cell_delays: 4x
    net_in:
        ef: 2x
    net_out:
        ef: 2x
    '''
    # node
    g.nodes['node'].data['n_rats'] = torch.zeros(g.num_nodes('node'), 4)
    g.nodes['node'].data['n_ats'] = torch.zeros(g.num_nodes('node'), 4)
    g.nodes['node'].data['n_slews'] = torch.zeros(g.num_nodes('node'), 4)
    g.nodes['node'].data['nf'] = torch.zeros(g.num_nodes('node'), 10)
    g.nodes['node'].data['n_net_delays'] = torch.zeros(g.num_nodes('node'), 4)
    g.nodes['node'].data['n_is_timing_endpt'] = torch.zeros(g.num_nodes('node'),)

    # cell_out
    g.edges['cell_out'].data['ef'] = torch.zeros(g.num_edges('cell_out'), 512)
    g.edges['cell_out'].data['e_cell_delays'] = torch.zeros(g.num_edges('cell_out'), 4)

    # net_in
    g.edges['net_in'].data['ef'] = torch.zeros(g.num_edges('net_in'), 2)

    # net_out
    g.edges['net_out'].data['ef'] = torch.zeros(g.num_edges('net_in'), 2)


    # add feature for net_out and net_in
    success = fail = 0
    for k, delay in (net_delay.items()):
        try:
            pin_src, pin_dst = k.split('->')
            pin_src = pin2index[pin_src]
            pin_dst = pin2index[pin_dst]
            g.edges['net_out'].data['ef'][g.edge_ids(pin_src, pin_dst, etype='net_out')] = torch.Tensor(delay[0:2])
            g.edges['net_in'].data['ef'][g.edge_ids(pin_dst, pin_src, etype='net_in')] = torch.Tensor(delay[2:4])
            success += 1

        except dgl._ffi.base.DGLError:
            fail += 1
    return g