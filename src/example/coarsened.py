from VRP.Instance import Initializer
from VRP.Route import Route
from VRP.extend.CoarsenedRoute import CoarsenedRoute
from VRP.ClassicalSolvers import ClassicalOptimizer
from VRP.Visualization import visualize_route, compare_graphs

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
    original_routes = route.load_routes(x)
    original_routes_cost = sum([ route.cost(vehicle) for vehicle in original_routes ])
    assert np.round(cost, 8) == np.round(original_routes_cost, 8)

    # Visualize the routes
    uncoarsened_graph = route.pygsp_graph()
    visualize_route(uncoarsened_graph, original_routes, colormap='hsv').savefig('foo.png')

    '''
    Coarsened Route
    '''
    # Coarsening
    coarsened_route_object = CoarsenedRoute(graph, 0, vehicles=2)
    coarsened_route, metrices = coarsened_route_object.coarsen(coarsening_ration=0.2)

    # Optimize the route path
    x, cost = coarsened_route.solve('cplex_solution')
    coarsened_routes = coarsened_route.load_routes(x)
    coarsened_routes_cost = sum([ coarsened_route.cost(vehicle) for vehicle in coarsened_routes ])
    assert np.round(cost, 8) == np.round(coarsened_routes_cost, 8)

    # Visualize the routes
    coarsened_graph = coarsened_route.pygsp_graph()
    visualize_route(coarsened_graph, coarsened_routes, colormap='hsv').savefig('coarsened-foo.png')

    # Visualize Coarsening
    compare_graphs(uncoarsened_graph, coarsened_graph, labels=['uncoarsened', 'coarsened']).savefig('comparison-coarsening-foo.png')

    '''
    Re-Construct Route
    '''
    # Run the main routine
    recreated_route, recreated_cost = route.routine(CoarsenedRoute(graph, 0, vehicles=2))
    visualize_route(uncoarsened_graph, recreated_route, colormap='hsv').savefig('recreated-foo.png')
    recreated_route_cost = sum([route.cost(vehicle) for vehicle in recreated_route])
    assert np.round(recreated_route_cost, 8) == np.round(sum(recreated_cost), 8)

    are_route_same = (original_routes == recreated_route)
    cost_difference = recreated_route_cost - original_routes_cost
    pass


if __name__ == '__main__':
    main()
