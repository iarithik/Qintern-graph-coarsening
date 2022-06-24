import numpy as np
from VRPGraph import Route, Initializer

NODES = 15

def test_load_routes():
    # Initialize a graph
    initializer = Initializer(NODES)
    graph = initializer.generate_graph()

    # Initiate a route instance with vehicles
    route = Route(graph, 0, vehicles=2)

    # Optimize the route path
    x, cost = route.solve('cplex_solution')

    # Load the optimized paths as array of tuples.
    # The array [ (0, 4), (4, 2), (2, 3), (3, 1), (1, 0) ] describes 
    # the route 0 <--> 4 <--> 2 <--> 3 <--> 1 <--> 0
    routes = route.load_routes(x)
    routes_cost = sum([ route.cost(vehicle) for vehicle in routes ])

    assert np.round(cost, 8) == np.round(routes_cost, 8)