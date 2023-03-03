'''
Check whether there exists a loop in circuit graph
pin - cell_out - pin
pin - net_out - pin
'''
import dgl
import torch
from config import TOPO
from typing import List
import networkx as nx

def create_homo_graph(graph:dgl.heterograph) -> dgl.graph:
    n_src, n_dst = graph.edges(etype='net_out')
    c_src, c_dst = graph.edges(etype='cell_out')
    g_homo = dgl.graph((
        torch.cat([n_src, c_src]),
        torch.cat([n_dst, c_dst]),
    ))
    return g_homo


def check_topo(g_homo:dgl.DGLGraph) -> int:
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


class FindAllLoop:
    WHITE = 0
    GRAY = 1
    BLACK = 2
    SEP = '*' * 50

    def __init__(self, g_hetero:dgl.heterograph) -> None:
        self.g = create_homo_graph(g_hetero)
        self.color = [FindAllLoop.WHITE] * self.g.num_nodes()
        self.pre = [None] * self.g.num_nodes()
        self.loops = []
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

    
    def find_all_loop(self) -> List[List]:
        for i in self.g.nodes():
            i = i.item()
            if self.color[i] == FindAllLoop.WHITE:
                self.dfs(i)

        for i in self.loops:
            print(i)
        return self.loops


def find_all_loops_johnson(g:dgl.heterograph):
    """
    https://stackoverflow.com/questions/546655/finding-all-cycles-in-a-directed-graph
    """
    g_homo = create_homo_graph(g)
    g_nx = nx.DiGraph([(src.item(), dst.item()) for src, dst in zip(*g_homo.edges())])
    loops = list(nx.simple_cycles(g_nx))
    for i in range(len(loops)):
        loops[i].append(loops[i][0])
    return loops


class RemoveAllLoops:
    def __init__(self, g:dgl.heterograph) -> None:
        self.g = g
    
    def remove_loop(self, loops):
        for loop in loops:
            src = loop[-2]
            dst = loop[-1]
            for etype in ['cell_out', 'net_out']:
                try:
                    edge_ids = self.g.edge_ids(src, dst, etype=etype)
                    self.g = dgl.remove_edges(self.g, edge_ids, etype=etype)
                    if etype == 'net_out':
                        edge_ids = self.g.edge_ids(dst, src, etype='net_in')
                        self.g = dgl.remove_edges(self.g, edge_ids, etype='net_in')
                except dgl.DGLError as e:
                    # print(repr(e))
                    continue

    def run(self,):
        loops = [1]
        while len(loops) > 0:
            # loops = FindAllLoop(self.g).run()
            loops = find_all_loops_johnson(self.g)
            if len(loops) > 0:
                self.remove_loop(loops)
                # print(f"Remove {len(loops)} loop(s)")
        return self.g