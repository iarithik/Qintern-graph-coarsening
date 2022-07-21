import numpy as np
from VRP.Instance import Initializer

NODES = 15

def test_simple_instance():
    initializer = Initializer(NODES)
    xc, yc, instance = initializer.generate_instance()

    # TEST: matrix shape NxN
    assert instance.shape == (NODES, NODES)

    # TEST: coordinate length equal to number of nodes
    assert len(xc) == len(yc) == NODES

def test_instance_distance_coordinates():
    initializer = Initializer(NODES)
    xc, yc, instance = initializer.generate_instance()

    for i, (i_x, i_y) in enumerate(zip(xc, yc)):
        # Select nodes one by one
        for j in range(NODES):
            if i != j:
                # Cross check the weights with xy coords
                j_x, j_y = xc[j], yc[j]
                weight = instance[i, j]

                # TEST: Distance A <--> B and B <--> A should be same
                assert instance[i, j] == instance[j, i]

                # TEST: Distance between i and j should be correlated to the weights
                assert np.round((i_x - j_x)**2 + (i_y - j_y)**2, 8) == np.round(weight**2, 8)