"""
Add node features and edge features to dgl.DGLHeteroGraph
"""
import dgl
import torch
from config import LUT
from config import CELL_PIN_SEP
from config import CONNECTION_SEP
def add_graph_feature(
    g: dgl.DGLHeteroGraph,
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
    cell_loc,
    unit:float,
    all_pin_loc
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
    g.edges['cell_out'].data['ef'] = torch.zeros(g.num_edges('cell_out'), 512, dtype=torch.float32)
    g.edges['cell_out'].data['e_cell_delays'] = torch.zeros(g.num_edges('cell_out'), 4, dtype=torch.float32)

    # net_in
    g.edges['net_in'].data['ef'] = torch.zeros(g.num_edges('net_in'), 2)

    # net_out
    g.edges['net_out'].data['ef'] = torch.zeros(g.num_edges('net_in'), 2)


    # add feature for net_out, net_in
    print('Adding feature: net_in, net_out')
    for k in net_delay.keys():
        pin_src_name, pin_dst_name = k.split(CONNECTION_SEP)
        
        pin_src_index = pin2index.get(pin_src_name)
        pin_dst_index = pin2index.get(pin_dst_name)
        
        if pin_src_index is None or pin_dst_index is None:
            print(f'Adding feature: net_in, net_out, {pin_src_name} or {pin_dst_name} is not registered in pin2index')
            continue

        src_loc = all_pin_loc.get(pin_src_name)
        dst_loc = all_pin_loc.get(pin_dst_name)

        if src_loc is None or dst_loc is None:
            print(f'Adding feature: net_in, net_out, {pin_src_name} or {pin_dst_name} does not have locations in all_pin_loc.json')
            continue

        src_loc = torch.Tensor(src_loc) / unit
        dst_loc = torch.Tensor(dst_loc) / unit

        
        g.edges['net_out'].data['ef'][g.edge_ids(pin_src_index, pin_dst_index, etype='net_out')] = dst_loc - src_loc
        g.edges['net_in'].data['ef'][g.edge_ids(pin_dst_index, pin_src_index, etype='net_in')] = src_loc - dst_loc


    # add feature for cell_out (e_cell_delays)
    print('Adding feature: cell_out (e_cell_delays)')
    for k,delay in cell_delay.items():
        fanin, fanout = k.split(CONNECTION_SEP)
        f1, f2 = fanin, fanout
        fanin = pin2index.get(fanin)
        fanout = pin2index.get(fanout)
        if fanin is None or fanout is None:
            print(f'Adding feature: cell_out (e_cell_delays), {f1} or {f2} is not registered in pin2index')
            continue
        g.edges['cell_out'].data['e_cell_delays'][g.edge_ids(fanin, fanout, etype='cell_out')] = torch.Tensor(delay[0:4])
    

    # add feature for cell_out (LUT, ef)
    print('Adding feature: cell_out (ef)')
    index2pin = {i:p for p,i in pin2index.items()}
    for u,v in zip(*g.edges(etype='cell_out')):
        u,v = u.item(), v.item()
        edge_id = g.edge_ids(u,v,etype='cell_out')
        u,v = index2pin[u], index2pin[v]
        cell_name, fanout_name = v.split(CELL_PIN_SEP)
        fanin_name = u.split(CELL_PIN_SEP)[-1]
        cell_class = cell_name_to_cell_class[cell_name]
        try:
            luts = lut_info[cell_class][fanout_name]['luts'][fanin_name]
        except KeyError:
            print(f'Adding feature: cell_out (ef), {cell_class}{CELL_PIN_SEP}{fanout_name} does not have lut relative to {fanin_name}')
            continue


        s = 0
        for i in range(LUT.num_luts):
            lut = luts[i%len(luts)]

            # add valid bit, which indicates whether this lut is valid or not
            g.edges['cell_out'].data['ef'][edge_id][s] = 1.0
            s += 1

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

        # add values
        for i in range(LUT.num_luts):
            lut = luts[i%len(luts)]

            values = torch.Tensor(lut['values'])
            if values.shape[0] < LUT.lut_size**2:
                values = torch.cat([values, torch.zeros(LUT.lut_size**2 - values.shape[0])])
            g.edges['cell_out'].data['ef'][edge_id][s:s+LUT.lut_size**2] = values[0:LUT.lut_size**2]
            s += LUT.lut_size**2


    # adding feature for AT, RAT and slew
    print('Adding feature: node (AT, RAT, slew)')
    n = g.nodes['node'].data['n_ats'].shape[0]
    for pin_name, timing in at_rat_slew.items():
        pin_index = pin2index.get(pin_name)
        if pin_index is None:
            # print(f'Adding feature: node (AT, RAT, slew), {pin_name} is not registered in pin2index')
            continue
        at = torch.Tensor(timing['AT'])
        rat = torch.Tensor(timing['RAT'])
        slew = torch.Tensor(timing['SLEW'])
        if pin_index >= n:
            print(f'Adding feature: node (AT, RAT, slew), {pin_name} is not included in graph')
            continue
        else:
            g.nodes['node'].data['n_ats'][pin_index] = at[0:4]
            g.nodes['node'].data['n_rats'][pin_index] = rat[0:4]
            g.nodes['node'].data['n_slews'][pin_index] = slew[0:4]


    print('Adding feature: node (n_net_delays)')
    for k,delay in net_delay.items():
        pin_src, pin_dst = k.split(CONNECTION_SEP)
        pin_index = pin2index.get(pin_dst)
        if pin_index is None:
            print(f'Adding feature: node (n_net_delays), {pin_dst} is not registered in pin2index')
            continue
        delay = torch.Tensor(delay)
        g.nodes['node'].data['n_net_delays'][pin_index] = delay[0:4]


    print('Adding feature: node (n_is_timing_endpt)')
    n = g.nodes['node'].data['n_is_timing_endpt'].shape[0]
    for pin in timing_endpoint:
        pin_index = pin2index.get(pin)
        if pin_index is None or pin_index >= n:
            print(f'Adding feature: node (n_is_timing_endpt), {pin} is not registered in pin2index or not included in graph')
            continue
        g.nodes['node'].data['n_is_timing_endpt'][pin_index] = 1.0


    print('Adding feature: node (nf, is primary or not)')
    n = g.nodes['node'].data['nf'].shape[0]
    for pi in pipos['PI']:
        pi_index = pin2index.get(pi)
        if pi_index is None or pi_index >= n:
            print(f'Adding feature: node (nf, is primary or not), {pi} is not registered in pin2index or not included in graph')
            continue
        g.nodes['node'].data['nf'][pi_index, 0] = 1.0
        g.nodes['node'].data['nf'][pi_index, 1] = 1.0
    for po in pipos['PO']:
        po_index = pin2index.get(po)
        if po_index is None or po_index >= n:
            print(f'Adding feature: node (nf, is primary or not), {po} is not registered in pin2index or not included in graph')
            continue
        g.nodes['node'].data['nf'][po_index, 0] = 1.0
        g.nodes['node'].data['nf'][po_index, 1] = 0.0
    

    print('Adding feature: node (nf, location for PIPO)')
    n = g.nodes['node'].data['nf'].shape[0]
    for pin_name,loc_xy in pipo_loc.items():
        x,y = loc_xy[0], loc_xy[1]
        pin_index = pin2index.get(pin_name)
        if pin_index is None or pin_index >= n:
            print(f'Adding feature: node (nf, location for PIPO), {pin_name} is not registered in pin2index or not included in graph')
            continue
        loc = torch.Tensor([
            x - chip_area[0],
            chip_area[2] - x,
            y - chip_area[1],
            chip_area[3] - y
        ]).abs()
        loc /= unit
        g.nodes['node'].data['nf'][pin_index, 2:6] = loc


    print('Adding feature: node (nf)')
    n = g.nodes['node'].data['nf'].shape[0]
    cell_names_1 = set(cell_loc.keys())
    cell_names_2 = set(cell_name_to_cell_class.keys())
    cell_names_common = cell_names_1.intersection(cell_names_2)

    for cell_name in cell_names_common:
        cell_class = cell_loc[cell_name]['cell_class']
        cell_location = cell_loc[cell_name]['location']
        
        for pin_name in lut_info[cell_class].keys():
            try:
                direction = lut_info[cell_class][pin_name]['direction']
            except KeyError:
                print(f'Adding feature: node (nf), {cell_class}{CELL_PIN_SEP}{pin_name} does not have direction, use `input` to replace')
                direction = 'input'
            direction = 0.0 if direction == 'input' else 1.0

            try:
                capacitance = lut_info[cell_class][pin_name]['capacitance']
            except KeyError:
                print(f'Adding feature: node (nf), {cell_class}{CELL_PIN_SEP}{pin_name} does not have capacitance, use `0.0` to replace')
                capacitance = 0.0
            
            pin_location = torch.Tensor([
                cell_location[0] - chip_area[0],
                cell_location[0] - chip_area[2],
                cell_location[1] - chip_area[1],
                cell_location[1] - chip_area[3],
            ]).abs()
            pin_location /= unit

            pin_index = pin2index.get(cell_name + CELL_PIN_SEP + pin_name)
            if pin_index is None or pin_index >= n:
                print(f'Adding feature: node (nf), {cell_name + CELL_PIN_SEP + pin_name} is not registered in pin2index or not included in graph')
                continue
            else:
                g.nodes['node'].data['nf'][pin_index, 1] = direction
                g.nodes['node'].data['nf'][pin_index, 2:6] = pin_location
                g.nodes['node'].data['nf'][pin_index, 6:10] = capacitance
        
        
    return g