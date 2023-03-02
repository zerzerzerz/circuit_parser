'''
Check whether there exists a loop in circuit graph
pin - cell_out - pin
pin - net_out - pin
'''
import dgl
from collections import Counter
import torch

def check_topo(g:dgl.heterograph):
    n_src, n_dst = g.edges(etype='net_out')
    c_src, c_dst = g.edges(etype='cell_out')
    g_homo = dgl.graph((
        torch.cat([n_src, c_src]),
        torch.cat([n_dst, c_dst]),
    ))
    try:
        topo_levels = dgl.topological_nodes_generator(g_homo)
        num_topo_levels = len(topo_levels)
        if num_topo_levels % 2 == 0:
            return True
        else:
            print(f"Number of topo levels is {num_topo_levels}, which must be even")
            return False
    except dgl.DGLError as e:
        print(repr(e))
        return False


def check_loop(g:dgl.graph, index2pin):
    '''
    topological sort to check whether there exists a loop
    '''
    in_degrees = [0] * g.num_nodes()
    for i in range(g.num_nodes()):
        in_degrees[i] = len(g.predecessors(i))
    

    while True:
        flag = False
        for i in range(g.num_nodes()):
            if in_degrees[i] == 0:
                flag = True
                in_degrees[i] = -1
                for j in g.successors(i):
                    in_degrees[j] -= 1
        if not flag:
            break

    ans = []
    for i in range(g.num_nodes()):
        if in_degrees[i] != -1:
            ans.append(index2pin[i])
    return ans


def find_a_loop(g:dgl.graph, index2pin={}):
    start_points = []
    for i in g.nodes():
        if g.in_degrees(i) == 0:
            start_points.append(i)
    
    def func(i, g, loop, map, index2pin):
        # was not been visited
        if map[i] == False:
            loop.append(i.item())
            map[i] = True

        # was been visited, loop
        else:
            loop.append(i.item())
            c = Counter(loop)
            for k in loop:
                if c[k] > 1:
                    loop_flag = ' !!!'
                else:
                    loop_flag = ''
                print(index2pin.get(k,k) + loop_flag)
            return True
        
        for j in g.successors(i):
            has_loop = func(j, g, loop, map, index2pin)
            if has_loop:
                return True

        map[i] = False
        loop.pop()
    
    loop = []
    map = [False] * g.num_nodes()
    for i in start_points:
        has_loop = func(i,g,loop,map,index2pin)
        if has_loop:
            return True