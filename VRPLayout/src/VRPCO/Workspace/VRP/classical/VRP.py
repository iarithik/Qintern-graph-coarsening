from ortools.constraint_solver import routing_enums_pb2, pywrapcp

from classical.VRPBase import VRPBase
from classical.VRPSolution import VRPSolution, Route

"""
Solving VRP problem using Google OR-Tools.
"""


class VRP(VRPBase):
    """Solver for Vehicle Routing Problem - classical implementation
       based on Google OR-Tools, for testing purposes (reference solution)."""

    def convert_solution(self, manager, routing, solution) -> VRPSolution:
        if not solution:
            return None

        routes = []
        for vehicle_id in range(self.m):
            index = routing.Start(vehicle_id)
            route_distance = 0
            nodes = []
            while not routing.IsEnd(index):
                nodes.append(manager.IndexToNode(index))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            nodes.append(manager.IndexToNode(index))
            routes.append(Route(vehicle_id, nodes, route_distance))

        return VRPSolution(solution.ObjectiveValue(), routes)

    def solve(self):
        data = self.prepare_data()
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Distance constraint.
        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)
        return self.convert_solution(manager, routing, solution)

