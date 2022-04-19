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
    if hasattr(mapping, 'toarray'):
        mapping = mapping.toarray()
    layout_data_c, layout_data_o = np.where(mapping > 0)
    return [ o for c, o in zip(layout_data_c, layout_data_o) if ix == c ]


def get_coarsen_distance_norm(coarsened_adjacency, mapping, parent_edl):
    adjacency = coarsened_adjacency.copy()
    shape = coarsened_adjacency.shape
    node_n = shape[0]
    for ix in range(node_n):
        for iy in range(node_n):
            # this is ix node to iy node
            n_x = node_from_mapping(ix, mapping)[0]
            n_y = node_from_mapping(iy, mapping)[0]
            distance = get_distance(n_x, n_y, parent_edl)
            adjacency[ix, iy] = distance
    return adjacency