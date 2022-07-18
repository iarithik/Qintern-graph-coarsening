import numpy as np
from time import time

from QuantumLogistics import logisticsGraph, Route, StandardRouteSolver, ILPPulpEncoder, GurobiSolver, CBCSolver, DeltaCoarseningEngine

if __name__ == "__main__":
    # experimental design for graph coarsening
    # If using random number generators will need to do statistical (repeatable) experiments for each type
    # This code serves as a 'guiding light' to design the new code for this experiment.

    # 1. Graphs types
    graphTypes = ["fully_connected"] #, "random", "small_world"]
    numberOfNodes = 15

    # Define route configuration
    config = {  'vehicles' : 2,
                'depot' : 0,  # must be a list
                'capacity': -1,
                'demand': -1  }

    # Define solver - using ILP encoder with Gurobi Solver
    solver = StandardRouteSolver(ILPPulpEncoder(), CBCSolver())
    #solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver())
    solverConfig = {"testVar":1}

    ##############################################################
    ##############################################################
    ##############################################################

    # Define Coarsening Object/methods
    coarsenConfig = {'coarsenRate' : 0.5,
                     'radiusCoefficient': 0.2}
    coarseningEngine = DeltaCoarseningEngine(coarsenConfig)

    ##############################################################
    ##############################################################
    ##############################################################

    # statistical analysis
    numberofGraphSamples = 30

    #generate a list of seeds used in run (for future reference)
    #np.savetxt("seedFiles.txt",np.random.randint(50000, size = numberofGraphSamples))

    #Loading Seeds
    #seeds = np.loadtxt("seedFiles.txt").astype(np.int32)
    seeds = [1000]

    SolutionList = []

    for graphType in graphTypes:
        for runNumber in range(numberofGraphSamples):
            
            #Define the network
            LogisticsNetwork = logisticsGraph(numberOfNodes, seed = seeds[runNumber], graph_type = graphType)
            LogisticsNetwork.generate_graph()

            #Create the route object
            route = Route(LogisticsNetwork, config, coarseningEngine = coarseningEngine)

            # solve route with FULL graph
            fullTimeInitial = time()
            solvedRoute = solver.solve(route, config = solverConfig)
            print(solvedRoute)
            print(time() - fullTimeInitial)

            route.visualiseSolution(solvedRoute)
            fineCost = route.calculateCost(solvedRoute)

            # solve route with COARSENED graph
            route.coarsen = True # indicates coarsening is required
            coarsenedTimeInitial = time()
            solvedCoarseRoute = solver.solve(route, config)
            print(solvedCoarseRoute)
            print(time() - coarsenedTimeInitial)
        
            route.visualiseSolution(solvedCoarseRoute)
            coarseCost = route.calculateCost(solvedCoarseRoute)

            print(fineCost)
            print(coarseCost)

            print("Loss of optimality: ", coarseCost/fineCost - 1)

            print(n)

            # add solved route to list for post-processing
            #SolutionList.append([route, solvedRoute, solvedCoarseRoute, timeToSolveFull, timeToSolveCoarse])

    # complete data analytics Solutions:
    for result in SolutionList:
        coarseningMetrics = result[0].generateCoarseningMetrics()
        #results = solvedRoute.evaluateKPIs()


        
        # 



        # for vehicle in range(self.vehicles):
        #     inflated_route = self.inflate_route(mapping, child_edl, coarsened_routes, vehicle)
        #     normalized_route = self.normalize(inflated_route, parent_edl)
        #     route_cost = self.cost(normalized_route, parent_edl)

        #     route += [normalized_route]
        #     cost += [route_cost]
        # #return route, cost

        # visualize_route(uncoarsened_graph, recreated_route, colormap='hsv').savefig('recreated-foo.png')
        # recreated_route_cost = sum([route.cost(vehicle) for vehicle in recreated_route])
        # assert np.round(recreated_route_cost, 8) == np.round(sum(recreated_cost), 8)

        # are_route_same = (original_routes == recreated_route)
        # cost_difference = recreated_route_cost - original_routes_cost
