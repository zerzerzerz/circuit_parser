from copy import deepcopy
import dgl
from config.config import CONNECTION_SEP

def construct_cell_graph(cell_delay:dict, pin2index:dict):
    '''
    construct cell graph from cell_delay.
    src is fanin of cell.
    dst is fanout of cell.
    '''
    src = []
    dst = []
    for k in cell_delay.keys():
        p1,p2 = k.split(CONNECTION_SEP)
        src.append(pin2index[p1])
        dst.append(pin2index[p2])
    return src, dst


def construct_net_graph(net_delay:dict, pin2index:dict):
    '''
    construct net graph through net_delay (net_out).
    src is driver of net.
    dst is sink of net.
    '''
    src = []
    dst = []
    for k in net_delay.keys():
        p1,p2 = k.split(CONNECTION_SEP)
        src.append(pin2index[p1])
        dst.append(pin2index[p2])
    return src, dst


def construct_graph(
    cell_delay: dict,
    net_delay: dict,
    pin2index: dict
) -> dgl.DGLHeteroGraph:
    raise NotImplementedError
    print("Constructing graph")
    res = {}
    res[('node','cell_out','node')] = construct_cell_graph(cell_delay, pin2index)
    res[('node','net_out','node')] = construct_net_graph(net_delay, pin2index)
    res[('node','net_in','node')] = deepcopy(res[('node','net_out','node')])[::-1]
    return dgl.heterograph(res)


def construct_graph2(cell_out, net_out, pin2index) -> dgl.heterograph:
    print("Constructing graph")
    res = {}

    # cell_out
    print("Constructing graph (cell_out)")
    src_cell_out = []
    dst_cell_out = []
    for k in cell_out:
        s,d = k.split(CONNECTION_SEP)
        ss,dd = s,d
        try:
            s = pin2index[s]
            d = pin2index[d]
        except KeyError:
            print(f'cell_out: {ss} or {dd} are not registered in pin2index')
            continue
        src_cell_out.append(s)
        dst_cell_out.append(d)
    res[('node', 'cell_out', 'node')] = (src_cell_out, dst_cell_out)

    # net_out
    print("Constructing graph (net_out)")
    src_net_out = []
    dst_net_out = []
    for k in net_out:
        s,d = k.split(CONNECTION_SEP)
        ss,dd = s,d
        try:
            s = pin2index[s]
            d = pin2index[d]
        except KeyError:
            print(f'net_out: {ss} or {dd} are not registered in pin2index')
            continue
        src_net_out.append(s)
        dst_net_out.append(d)
    res[('node', 'net_out', 'node')] = (src_net_out, dst_net_out)
    
    print("Constructing graph (net_in)")
    res[('node', 'net_in', 'node')] = (dst_net_out, src_net_out)

    g = dgl.heterograph(res).int()
    return g
    
