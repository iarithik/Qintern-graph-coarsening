import numpy as np

def edge_list2dict(edge_list):
    n1, n2, w = edge_list
    assert len(n1) == len(n2) == len(w)
    return { (n1[i], n2[i]):w[i] for i in range(len(n1)) }

def flatten(lst):
    return [ n for nlist in lst for n in nlist]

def edl2w(edl):
    nodes = set(flatten(list(edl.keys())))
    X =  len(nodes)
    A = np.zeros((X,X))
    for key, value in edl.items():
        n1, n2 = key

        # Set to weight 1 for the matrix
        A[n1, n2] = value
        A[n2, n1] = value
    return A

def get_distance(_from, _to, edl):
    # edl = {
    # (1, 2): 1.1211 ,
    # (2, 3): 2.12242,
    # (4, 3): 1.2341
    # }

    # from -> 3, to -> 4 := (3, 4) or (4, 3)
    
    return edl.get((_from, _to), edl.get((_to, _from), 0) )

def print_deconstructed_route(routes):
    for vehicle_route in routes:
        assert vehicle_route[0][0] == 0
        print(vehicle_route[0][0], end=' ')
        for route in vehicle_route:
            _from, _to = route
            print('-->', _to, end=' ')
        print()


def node_from_mapping(ix, mapping):
    """
        Returns the attributed fine nodes to a given coarse node
    """

    if hasattr(mapping, 'toarray'):
        mapping = mapping.toarray()

    layout_data_c, layout_data_o = np.where(mapping > 0)

    return [ o for c, o in zip(layout_data_c, layout_data_o) if ix == c ]



def get_coarsen_distance_norm(coarsened_adjacency, mapping, parent_edl):
    """
        going from coarse mapping to fine mapping
    """
    adjacency = coarsened_adjacency.copy()
    shape = coarsened_adjacency.shape
    node_n = shape[0]

    for ix in range(node_n):
        for iy in range(node_n):
            # this is ix node to iy node

            n_x = node_from_mapping(ix, mapping)[0] # # only taking the first node of the contraction ??????    the first fine node mapped to coarse node
            n_y = node_from_mapping(iy, mapping)[0]

            distance = get_distance(n_x, n_y, parent_edl)
            adjacency[ix, iy] = distance
    
    return adjacency





def reframe_coordinates(coarsened_adjacency, original_graph, mapping):
    adjacency = coarsened_adjacency.copy()
    
    parent_edl = edge_list2dict(original_graph.get_edge_list())
    old_coords = np.asarray(original_graph.coords)
    new_coords = []

    mapping = np.asarray(mapping.todense())
    shape = mapping.shape

    # cn represents node on the coarsened graph
    for cn in range(shape[0]):
        coarsened_nodes = np.where(mapping[cn] > 0.)
        new_coords += [ get_midpoint_from_coarsened( old_coords, coarsened_nodes, mapping[cn]) ]

    return np.array(new_coords)

def get_midpoint_from_coarsened(old_coords, coarsened_nodes, coarsened_weights):
    # old_coords => (20, 2) Matrix
    # coarsened_nodes[0] => [ 0, 1 ]
    # coarsened_weights => 
    # [0.707, 0.707, 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   , 0.   ]
    total_coarsened_units = len(coarsened_nodes[0])

    if total_coarsened_units is 1:
        return old_coords[coarsened_nodes[0]].reshape(2, )

    x = np.array([ old_coords[node, 0] * coarsened_weights[node]**2 for i, node in enumerate(coarsened_nodes[0])]).flatten().sum()
    y = np.array([ old_coords[node, 1] * coarsened_weights[node]**2 for i, node in enumerate(coarsened_nodes[0])]).flatten().sum()

    return np.array([x, y]).reshape(2, )
