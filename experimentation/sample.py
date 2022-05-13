from VRPGraph import Initializer, Route
from VRPGraph.Visualization import visualize_route
from VRPCO import ClassicalOptimizer

import numpy as np

NODES = 20

def main():
    # Initialize a graph
    initializer = Initializer(NODES)
    initializer.set_seed()

    graph = initializer.generate_graph()

    # Initiate a route instance with vehicles
    route = Route(graph, 0, vehicles=2)

    # Optimize the route path
    x, cost = route.solve('cplex_solution')

    # Load the optimized paths as array of tuples.
    # The array [ (0, 4), (4, 2), (2, 3), (3, 1), (1, 0) ] describes 
    # the route 0 <--> 4 <--> 2 <--> 3 <--> 1 <--> 0
    routes = route.load_routes(x)

    # Recalculating the route cost, to check if the the path
    # reconstruction has been done correctly or not  
    routes_cost = sum([ route.cost(vehicle) for vehicle in routes ])

    assert np.round(cost, 8) == np.round(routes_cost, 8)

    # Visualize the routes
    visualize_route(route.pygsp_graph(), routes, colormap='hsv').savefig('foo.png')

    return

if __name__ == '__main__':
    main()
