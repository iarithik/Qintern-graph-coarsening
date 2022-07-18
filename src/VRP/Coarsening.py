from pygsp import *
from pygsp import graphs

import networkx as nx
import math
import numpy as np
from .Instance import Initializer

from graph_coarsening import coarsening_utils
from graph_coarsening.coarsening_utils import *
import graph_coarsening.graph_utils

def coarsening_quality(*args, **kwargs):
    return coarsening_utils.coarsening_quality(*args, **kwargs)

class Coarsening:
    def __init__(self, G, depot=[0]):

        self.pygsp = G
        self.depot = depot
        self.G = nx.from_numpy_matrix(G.W.todense())
        self.edl = { e:self.G.get_edge_data(*e)['weight'] for e in self.G.edges }
    
    def call(self, partition = 0.2):
        raise NotImplementedError()

    def __call__(self, partition = 0.2, **kwargs):
        collapse = self.call(partition=partition, **kwargs)
        return self.prepare(collapse)

    def prepare(self, collapse):
        """
            C : np.array of size n x N
                The coarsening matrix.
            Gc : pygsp Graph
                The smaller graph.
            Call : list of np.arrays
                Coarsening matrices for each level
            Gall : list of (n_levels+1) pygsp Graphs
                All graphs involved in the multilevel coarsening
        """
        # Prepare the return Objects

        #### RETURN OBJECTS ####

        # G         - the original graph
        # C -       - Loukases Coarsening Vector - weighted by sqrt(1/N) where N is the size of the sub partition - the current FULL coarsening vector after multiple steps
        # Gc        - coarsened graph with generalised coordinates as weighted by the coarsening vector
        # Call      - list of coarsening matrices through the steps
        # Gall      - list of graphs through coarsening steps
        # [iC]      - coarsening matrix in a list
        # collapse  - list of nodes to collapse

        # The original Graph
        G = self.pygsp 
        Call = [] # Some Variable
        Gall = [ G ] # Some Variable

        # get_coarsening_matrix - builds the coarsening matrix C
        #       accepts a graph to be coarsened and a list of subgraphs to be contracted
        iC = get_coarsening_matrix(G, collapse)                     # Coarsening Matrix

        # Getting coarsened adjacency matrix
        #       coarsen_matrix returns 
        Wc = graph_utils.zero_diag(coarsen_matrix(G.W, iC))                 # Coarsened Adjacency Matrix - where is it referenced in paper?
        Wc = (Wc + Wc.T) / 2                                                # this is only needed to avoid pygsp complaining for tiny errors
        Gc = gsp.graphs.Graph(Wc, coords=coarsen_vector(G.coords, iC))      # This is the 'Coarse Graph'

        # Define complete coarsening matrix- only used in multi level coarsening
        # C is a G.N x G.N identity matrix (where G.N is # nodes in matrix). Is saved in a compressed format for faster calc
        C = sp.sparse.eye(G.N, format="csc") # Some Variable
        C = iC.dot(C)                                                       # This is uncessary in a single level - only used in multiple levels

        Call.append(iC)  # Some Variable
        Gall.append(Gc) # Some Variable

        return C, Gc, Call, Gall, [iC], collapse

class Loukas_Coarsening(Coarsening):
    def __init__(self, G, depot=[0]):
        super().__init__(G, depot)

    def call(self, partition=0.2, K=10, method="variation", algorithm="greedy"):
        max_levels=1
        Uk=None
        lk=None
        max_level_r=0.99
        r = np.clip(partition, 0, 0.999)

        G0 = self.pygsp
        N = G0.N

        # current and target graph sizes
        n, n_target = N, np.ceil((1 - r) * N)

        G = G0

        # how much more we need to reduce the current graph
        r_cur = np.clip(1 - n_target / n, 0.0, max_level_r)
        
        if "variation" in method:

            if (Uk is not None) and (lk is not None) and (len(lk) >= K):
                mask = lk < 1e-10
                lk[mask] = 1
                lsinv = lk ** (-0.5)
                lsinv[mask] = 0
                B = Uk[:, :K] @ np.diag(lsinv[:K])
            else:
                offset = 2 * max(G.dw)
                T = offset * sp.sparse.eye(G.N, format="csc") - G.L
                lk, Uk = sp.sparse.linalg.eigsh(T, k=K, which="LM", tol=1e-5)
                lk = (offset - lk)[::-1]
                Uk = Uk[:, ::-1]
                mask = lk < 1e-10
                lk[mask] = 1
                lsinv = lk ** (-0.5)
                lsinv[mask] = 0
                B = Uk @ np.diag(lsinv)
            A = B

            if method == "variation_edges":
                coarsening_list = contract_variation_edges(
                    G, K=K, A=A, r=r_cur, algorithm=algorithm
                )
            else:
                coarsening_list = contract_variation_linear(
                    G, K=K, A=A, r=r_cur, mode=method
                )

        else:
            weights = get_proximity_measure(G, method, K=K)

            if algorithm == "optimal":
                # the edge-weight should be light at proximal edges
                weights = -weights
                if "rss" not in method:
                    weights -= min(weights)
                coarsening_list = matching_optimal(G, weights=weights, r=r_cur)

            elif algorithm == "greedy":
                coarsening_list = matching_greedy(G, weights=weights, r=r_cur)

        return coarsening_list

class Simple_Coarsening(Coarsening):
    def __init__(self, G, depot=[0]):
        super().__init__(G, depot)

        self.visited = []
        self.collapse = []

        self.coarsening_radius = 0




    def partition_weights(self, partition=0.2):
        # Used to generate a 'partition radius' under which nodes will be collapsed
        
        # TODO : FIXIT
        '''
        (1,2): 2.1,
        (2,1): 5.1,
        '''
        w = list(self.edl.values())
        w = list(sorted(w))

        size = self.G.number_of_nodes() # 20
        part = math.floor(size * partition) # 4

        return (w[part] + w[part+1]) / 2, size, part





    def check_collapsable(self, curr, edl, debug = True):

        # TODO : Avoid 2 neghbourin... colla..
        # curr - current node being tested
        # edl - edl length dictionary {(node i, node j) : length}

        # print("Checking collapsable with current: ")

        if curr in self.visited:
            return

        self.visited += [ curr ]

        # generate list of unvisited neighbour connections
        neighbour_data = { k:v for k, v in edl.items() if (curr in k) and (k[k[0] == curr] not in self.visited)
            # where k is (a, curr) or (curr, a), `k[k[0] == curr]` will return a
        }
        
        # sorted on value
        neighbours = dict(sorted(neighbour_data.items(), key=lambda item: item[1]))

        # evaluating edges in neighbourhood to see if nodes can go together
        for nodes, weight in neighbours.items():
            a,b = nodes
            if weight < self.coarsening_radius and ( a not in self.depot and b not in self.depot ):
                print(nodes)
                self.collapse += [ nodes ]
                self.visited += [ *nodes ]
                if debug:
                    print( f"[+] curr : {curr}", neighbours )
                return

        if debug:
            print( f"[ ] curr : {curr}", neighbours )


        nodesInNeighbourhood = set([ i for n in list(neighbours.keys()) for i in n ])

        # depth first search????
        for nodes in nodesInNeighbourhood:
            self.check_collapsable(nodes, edl, debug = debug)









    def coarsening_matrix(self, node_lst, debug = True):
        N = self.G.number_of_nodes()
        _N = N - len(node_lst)
        M = np.zeros([N, N])

        # print(M.shape)
        
        remove = []
        for nodes in node_lst:
            share = math.pow(1/len(nodes), 1/2)
            
            for twins in zip(nodes[::2], nodes[1::2]):
                a, b = twins
                if debug:
                    print( f"( {a}, {b} )" )
                M[a, a] = share
                M[a, b] = share
                remove += [b]

        for i, rm in enumerate(remove):
            M = np.delete(M, rm - i, axis=0)

        return M

    def call(self, partition = 0.2):
        # Get the min/max distance to coarsen, i.e. the coarsening radius
        self.coarsening_radius, _, _ = self.partition_weights(partition = partition)

        # Check for the coarsening criteria,
        # The variable `self.collapse` gets populated
        for n in self.G.nodes:
            self.check_collapsable(n, self.edl, debug = False)



        return self.collapse




