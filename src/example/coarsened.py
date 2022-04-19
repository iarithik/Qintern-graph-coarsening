from VRP.Instance import Initializer
from VRP.Route import Route
from VRP.extend.CoarsenedRoute import CoarsenedRoute
from VRP.ClassicalSolvers import ClassicalOptimizer
from VRP.Visualization import visualize_route

import numpy as np

NODES = 20

def main():
    # Initialize a graph
    initializer = Initializer(NODES)
    initializer.set_seed()
    graph = initializer.generate_graph()

    # Initiate a route instance with vehicles
    route = Route(graph, 0, vehicles=2)

    '''
    Normal Route
    '''
    # Optimize the route path
    x, cost = route.solve('cplex_solution')
    routes = route.load_routes(x)
    routes_cost = sum([ route.cost(vehicle) for vehicle in routes ])
    assert np.round(cost, 8) == np.round(routes_cost, 8)

    # Visualize the routes
    visualize_route(route.pygsp_graph(), routes, colormap='hsv').savefig('foo.png')

    '''
    Coarsened Route
    '''
    # Coarsening
    coarsened_route = CoarsenedRoute(graph, 0, vehicles=2)
    coarsened_route, metrices = coarsened_route.coarsen(coarsening_ration=0.2)

    # print("Coarsening Quality")
    # print(metrices)

    # Optimize the route path
    x, cost = coarsened_route.solve('cplex_solution')
    coarsened_routes = coarsened_route.load_routes(x)
    coarsened_routes_cost = sum([ coarsened_route.cost(vehicle) for vehicle in coarsened_routes ])
    assert np.round(cost, 8) == np.round(coarsened_routes_cost, 8)

    # Visualize the routes
    visualize_route(coarsened_route.pygsp_graph(), coarsened_routes, colormap='hsv').savefig('coarsened-foo.png')




if __name__ == '__main__':
    main()
