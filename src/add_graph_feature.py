import dgl
import torch
from config.config import LUT

def add_graph_feature(
    g: dgl.DGLHeteroGraph,
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
    cell_loc,
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
        pin_src = pin2index.get(pin_src)
        pin_dst = pin2index.get(pin_dst)
        if pin_src is None or pin_dst is None:
            continue
        g.edges['net_out'].data['ef'][g.edge_ids(pin_src, pin_dst, etype='net_out')] = torch.Tensor(delay[0:2])
        g.edges['net_in'].data['ef'][g.edge_ids(pin_dst, pin_src, etype='net_in')] = torch.Tensor(delay[2:4])


    # add feature for cell_out (e_cell_delays)
    print('Adding feature: cell_out (e_cell_delays)')
    for k,delay in cell_delay.items():
        fanin, fanout = k.split('->')
        fanin = pin2index.get(fanin)
        fanout = pin2index.get(fanout)
        if fanin is None or fanout is None:
            continue
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
        try:
            luts = lut_info[cell_class][fanout_name]['luts'][fanin_name]
        except KeyError:
            continue
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


    print('Adding feature: node (AT, RAT, slew)')
    n = g.nodes['node'].data['n_ats'].shape[0]
    for pin_name, timing in at_rat_slew.items():
        pin_index = pin2index.get(pin_name)
        if pin_index is None:
            continue
        at = torch.Tensor(timing['AT'])
        rat = torch.Tensor(timing['RAT'])
        slew = torch.Tensor(timing['SLEW'])
        if pin_index >= n:
            continue
        else:
            g.nodes['node'].data['n_ats'][pin_index] = at[0:4]
            g.nodes['node'].data['n_rats'][pin_index] = rat[0:4]
            g.nodes['node'].data['n_slews'][pin_index] = slew[0:4]


    print('Adding feature: node (n_net_delays)')
    for k,delay in net_delay.items():
        pin_src, pin_dst = k.split('->')
        pin_index = pin2index.get(pin_dst)
        if pin_index is None:
            continue
        delay = torch.Tensor(delay)
        g.nodes['node'].data['n_net_delays'][pin_index] = delay[0:4]


    print('Adding feature: node (n_is_timing_endpt)')
    n = g.nodes['node'].data['n_is_timing_endpt'].shape[0]
    for pin in timing_endpoint:
        pin_index = pin2index.get(pin)
        if pin_index is None or pin_index >= n:
            continue
        g.nodes['node'].data['n_is_timing_endpt'][pin_index] = 1.0


    print('Adding feature: node (nf, is primary or not)')
    n = g.nodes['node'].data['nf'].shape[0]
    for pi in pipos['PI']:
        pi_index = pin2index.get(pi)
        if pi_index is None or pi_index >= n:
            continue
        g.nodes['node'].data['nf'][pi_index, 0] = 1.0
        g.nodes['node'].data['nf'][pi_index, 1] = 1.0
    for po in pipos['PO']:
        po_index = pin2index.get(po)
        if po_index is None or po_index >= n:
            continue
        g.nodes['node'].data['nf'][po_index, 0] = 1.0
        g.nodes['node'].data['nf'][po_index, 1] = 0.0
    

    print('Adding feature: node (nf, location for PIPO)')
    n = g.nodes['node'].data['nf'].shape[0]
    for item in pipo_loc:
        pin_name = item[0]
        x,y = item[1], item[2]
        pin_index = pin2index.get(pin_name)
        if pin_index is None or pin_index >= n:
            continue
        loc = torch.Tensor([
            x - chip_area[0],
            chip_area[2] - x,
            y - chip_area[1],
            chip_area[3] - y
        ]).abs()
        g.nodes['node'].data['nf'][pin_index, 2:6] = loc


    print('Adding feature: node (nf)')
    n = g.nodes['node'].data['nf'].shape[0]
    keys1 = set(cell_loc.keys())
    keys2 = set(cells.keys())
    keys_common = keys1.intersection(keys2)
    for cell_name in keys_common:
        cell_class = cell_loc[cell_name]['cell_class']
        cell_location = cell_loc[cell_name]['location']
        for tmp in cells[cell_name]['pins']:
            pin_name = tmp['pin_name']

            try:
                direction = lut_info[cell_class][pin_name]['direction']
            except KeyError:
                direction = 'input'
            direction = 0.0 if direction == 'input' else 1.0

            try:
                capacitance = lut_info[cell_class][pin_name]['capacitance']
            except KeyError:
                capacitance = 0.0
            
            pin_location = torch.Tensor([
                cell_location[0] - chip_area[0],
                cell_location[0] - chip_area[2],
                cell_location[1] - chip_area[1],
                cell_location[1] - chip_area[3],
            ]).abs()

            pin_index = pin2index.get(cell_name + '.' + pin_name)
            if pin_index is None or pin_index >= n:
                continue
            else:
                g.nodes['node'].data['nf'][pin_index, 1] = direction
                g.nodes['node'].data['nf'][pin_index, 2:6] = pin_location
                g.nodes['node'].data['nf'][pin_index, 6:10] = capacitance

        
    return g