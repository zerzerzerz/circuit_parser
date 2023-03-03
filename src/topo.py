'''
Check whether there exists a loop in circuit graph
pin - cell_out - pin
pin - net_out - pin
'''
import dgl
from collections import Counter
import torch
from config import TOPO

def create_homo_graph(graph:dgl.heterograph):
    n_src, n_dst = graph.edges(etype='net_out')
    c_src, c_dst = graph.edges(etype='cell_out')
    g_homo = dgl.graph((
        torch.cat([n_src, c_src]),
        torch.cat([n_dst, c_dst]),
    ))
    return g_homo


def check_topo(g_homo:dgl.DGLGraph):
    try:
        topo_levels = dgl.topological_nodes_generator(g_homo)
        num_topo_levels = len(topo_levels)
        if num_topo_levels % 2 == 0:
            return TOPO.success
        else:
            # print(f"Number of topo levels is {num_topo_levels}, which must be even")
            return TOPO.odd_level
    except dgl.DGLError as e:
        # print("Loop detected")
        return TOPO.has_loop


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


class FindAllLoop:
    WHITE = 0
    GRAY = 1
    BLACK = 2
    SEP = '*' * 50

    def __init__(self, g:dgl.DGLGraph) -> None:
        self.g = g
        self.color = [FindAllLoop.WHITE] * self.g.num_nodes()
        self.pre = [None] * self.g.num_nodes()
        self.loops = []
        # self.find_all_loop()
        self.run = self.find_all_loop

    def build_loop(self, start, end):
        loop = [start]
        cur = end
        while cur != start:
            loop.append(cur)
            cur = self.pre[cur]
        loop.append(start)
        loop = list(reversed(loop))
        self.loops.append(loop)
        
    
    def display_color(self):
        print(FindAllLoop.SEP)
        for i, color in enumerate(self.color):
            print(i, color)


    def dfs(self, i):
        self.color[i] = FindAllLoop.GRAY
        for j in self.g.successors(i):
            j = j.item()
            if self.color[j] == FindAllLoop.WHITE:
                self.pre[j] = i
                self.dfs(j)
            elif self.color[j] == FindAllLoop.GRAY:
                self.build_loop(j,i)
        self.color[i] = FindAllLoop.BLACK

    
    def find_all_loop(self):
        for i in self.g.nodes():
            i = i.item()
            if self.color[i] == FindAllLoop.WHITE:
                self.dfs(i)

        for i in self.loops:
            print(i)
        return self.loops

