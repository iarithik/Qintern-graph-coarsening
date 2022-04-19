from pygsp import graphs
import networkx as nx
import numpy as np

import random

from typing import Tuple, List

class Initializer:
    """Generate the coordenates of 'n' instances (nodes)"""
    
    def __init__(self, n, fully_connected=True):
        self.n = n
        self.fully_connected = fully_connected
    
    def generate_graph(self) -> graphs.Graph:
        xc, yc, instance = self.generate_instance()
        # Define a Graph
        graph = graphs.Graph(instance)

        coords = np.array([c for c in zip(xc, yc)])
        graph.set_coordinates(coords)

        return graph

    def generate_instance(self) -> Tuple[List, List, np.array]:
        xy = np.random.rand(2, self.n)
        xc = xy[0]
        yc = xy[1]
        xy = xy.T

        # Create NetworkX Graph
        if self.fully_connected:
            G = nx.complete_graph(self.n)
        else:
            G = nx.fast_gnp_random_graph(self.n, 0.75)

        # Populate NetworkX Graph with appropiate Weight
        for (u, v) in G.edges():
            uc = xy[u]
            vc = xy[v]
            G.edges[u,v]['weight'] = np.linalg.norm( uc - vc )

        # Fetch NewtorkX Graph Adjacency Matrix
        W = nx.adjacency_matrix(G).todense()

        return xc, yc, W