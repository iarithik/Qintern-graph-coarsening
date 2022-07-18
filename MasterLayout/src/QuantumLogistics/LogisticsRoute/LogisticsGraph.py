from pygsp import graphs
import networkx as nx
import numpy as np

from typing import Tuple, List

class logisticsGraph:
    """Generate the coordinates of 'n' instances (nodes)"""
    
    def __init__(self, n, seed = 1543, graph_type = "fully_connected"):
        self.n = n
        self.seed = seed
        self.graph_type = graph_type
        self.set_seed()


    def set_seed(self, seed=None):
        np.random.seed(seed if seed else self.seed )
    


    def generate_graph(self) -> graphs.Graph:
        xc, yc, instance = self.generateGraphPoints()

        # Define a Graph
        graph = graphs.Graph(instance)

        coords = np.array([c for c in zip(xc, yc)])
        graph.set_coordinates(coords)

        self.graph = graph

        return graph



    def generateGraphPoints(self) -> Tuple[List, List, np.array]:
        xy = np.random.rand(2, self.n) +  + np.ones((2, self.n)) #What is the ones offset for??
        xc = xy[0]
        yc = xy[1]
        xy = xy.T

        # Creating NetworkX Graph
        graphCreationFunctions = {"fully_connected" : nx.complete_graph(self.n),
                                  "random"          : nx.fast_gnp_random_graph(self.n, 0.75),
                                  "small_world"     : nx.newman_watts_strogatz_graph(self.n, 3, 0.75)}

        G = graphCreationFunctions[self.graph_type]

        # Populate NetworkX Graph with appropiate Weight
        for (u, v) in G.edges():
            uc = xy[u]
            vc = xy[v]
            G.edges[u,v]['weight'] = np.linalg.norm( uc - vc )

        # Fetch NewtorkX Graph Adjacency Matrix
        W = nx.adjacency_matrix(G).todense()

        return xc, yc, W


    def loadGraphPointsFromFile(self):

        raise NotImplementedError


    def loadGraphFromFile(self):


        raise NotImplementedError