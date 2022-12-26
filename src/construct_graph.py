from copy import deepcopy
import torch
import dgl

def construct_cell_graph(cell_delay:dict, pin2index:dict):
    '''
    construct cell graph from cell_delay.
    src is fanin of cell.
    dst is fanout of cell.
    '''
    src = []
    dst = []
    for k in cell_delay.keys():
        p1,p2 = k.split('->')
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
        p1,p2 = k.split('->')
        src.append(pin2index[p1])
        dst.append(pin2index[p2])
    return src, dst


def construct_graph(
    cell_delay: dict,
    net_delay: dict,
    pin2index: dict
):
    res = {}
    res[('node','cell_out','node')] = construct_cell_graph(cell_delay, pin2index)
    res[('node','net_out','node')] = construct_net_graph(net_delay, pin2index)
    res[('node','net_in','node')] = deepcopy(res[('node','net_out','node')])[::-1]
    return dgl.heterograph(res)
