import dgl
import torch
import tqdm
from config.config import LUT

def add_graph_feature(
    g: dgl.DGLHeteroGraph,
    pin2index,
    net_delay,
    cell_delay,
    cells,
    lut_info,
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


    # add feature for net_out, net_in
    print('Adding feature: net_in, net_out')
    for k, delay in (net_delay.items()):
        pin_src, pin_dst = k.split('->')
        pin_src = pin2index[pin_src]
        pin_dst = pin2index[pin_dst]
        g.edges['net_out'].data['ef'][g.edge_ids(pin_src, pin_dst, etype='net_out')] = torch.Tensor(delay[0:2])
        g.edges['net_in'].data['ef'][g.edge_ids(pin_dst, pin_src, etype='net_in')] = torch.Tensor(delay[2:4])


    # add feature for cell_out (e_cell_delays)
    print('Adding feature: cell_out (e_cell_delays)')
    for k,delay in cell_delay.items():
        fanin, fanout = k.split('->')
        fanin = pin2index[fanin]
        fanout = pin2index[fanout]
        g.edges['cell_out'].data['e_cell_delays'][g.edge_ids(fanin, fanout, etype='cell_out')] = torch.Tensor(delay[0:4])
    

    # add feature for cell_out (LUT, ef)
    print('Adding feature: cell_out (ef)')
    index2pin = {i:p for p,i in pin2index.items()}
    for u,v in zip(*g.edges(etype='cell_out')):
        u,v = u.item(), v.item()
        edge_id = g.edge_ids(u,v,etype='cell_out')
        u,v = index2pin[u], index2pin[v]
        cell_name, fanout_name = v.split('.')
        fanin_name = u.split('.')[-1]
        cell_class = cells[cell_name]['cell_class']
        luts = lut_info[cell_class][fanout_name]['luts'][fanin_name]

        s = 0
        g.edges['cell_out'].data['ef'][edge_id][s:s+LUT.num_luts] = torch.ones(LUT.num_luts)
        s += LUT.num_luts
        for i in range(LUT.num_luts):
            lut = luts[i%len(luts)]

            index1 = torch.Tensor(lut['index1'])
            if index1.shape[0] < LUT.lut_size:
                index1 = torch.cat([index1, torch.zeros(LUT.lut_size - index1.shape[0])])
            g.edges['cell_out'].data['ef'][edge_id][s:s+LUT.lut_size] = index1[0:LUT.lut_size]
            s += LUT.lut_size

            index2 = torch.Tensor(lut['index2'])
            if index2.shape[0] < LUT.lut_size:
                index2 = torch.cat([index2, torch.zeros(LUT.lut_size - index2.shape[0])])
            g.edges['cell_out'].data['ef'][edge_id][s:s+LUT.lut_size] = index2[0:LUT.lut_size]
            s += LUT.lut_size

        for i in range(LUT.num_luts):
            lut = luts[i%len(luts)]

            values = torch.Tensor(lut['values'])
            if values.shape[0] < LUT.lut_size**2:
                values = torch.cat([values, torch.zeros(LUT.lut_size**2 - values.shape[0])])
            g.edges['cell_out'].data['ef'][edge_id][s:s+LUT.lut_size**2] = values[0:LUT.lut_size**2]
            s += LUT.lut_size**2


    return g