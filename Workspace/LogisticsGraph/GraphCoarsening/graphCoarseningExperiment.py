import numpy as np
from time import time

from QuantumLogistics import logisticsGraph, Route, StandardRouteSolver, ILPPulpEncoder, GurobiSolver, CBCSolver, DeltaCoarseningEngine

if __name__ == "__main__":
    # experimental design for graph coarsening
    # If using random number generators will need to do statistical (repeatable) experiments for each type
    # This code serves as a 'guiding light' to design the new code for this experiment.

    # 1. Graphs Definition
    graphTypes = ["fully_connected"] #, "random", "small_world"] ["random"] #
    numberOfNodes = 25
    singleNodeCapacity = 0.1
    nodeCapacityDefinition = numberOfNodes * [0.1]      # A list of nodes 

    ##############################################################
    ##############################################################
    ##############################################################

    # Define route configuration
    routeConfig = {     'vehicles' : 3,
                        'depot' : 0, 
                        'truckCapacity': 0.8}  # Set to -1 for auto (will evenly distribute trucks)

    # # Modifying truck capacity if set to auto
    if routeConfig['truckCapacity'] == -1:        
        Q = singleNodeCapacity * np.ceil((numberOfNodes+1) / routeConfig['vehicles'])
        routeConfig['truckCapacity'] = Q

    ##############################################################
    ##############################################################
    ##############################################################

    # Define solver - using ILP encoder with Gurobi Solver
    #solver = StandardRouteSolver(ILPPulpEncoder(), CBCSolver())
    solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver())
    solverConfig = {"testVar":1,
                    "gapRel" : 0.01,
                    "timeLimit" : 300}

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
    seeds = [1403]

    SolutionList = []

    for graphType in graphTypes:
        for runNumber in range(numberofGraphSamples):
            
            #Define the network
            LogisticsNetwork = logisticsGraph(nodeCapacityDefinition, seed = seeds[runNumber], graph_type = graphType)
            LogisticsNetwork.generate_graph()
            LogisticsNetwork.plotGraph()

            #Create the route object
            route = Route(LogisticsNetwork, routeConfig, coarseningEngine = coarseningEngine)

            # solve route with FULL graph
            fullTimeInitial = time()
            solvedRoute = solver.solve(route, config = solverConfig)
            print(solvedRoute)
            fullRouteTime = time() - fullTimeInitial
            print(fullRouteTime)

            route.visualiseSolution(solvedRoute)
            fineCost = route.calculateCost(solvedRoute)

            # solve route with COARSENED graph
            route.coarsen = True # indicates coarsening is required
            coarsenedTimeInitial = time()
            solvedCoarseRoute = solver.solve(route, config = solverConfig)
            print(solvedCoarseRoute)
            coarsenedRouteTime = time() - coarsenedTimeInitial
            print(coarsenedRouteTime)

            route.visualiseSolution(solvedCoarseRoute)
            coarseCost = route.calculateCost(solvedCoarseRoute)

            print(fineCost)
            print(coarseCost)
            print("Loss of optimality: ", coarseCost/fineCost - 1)
            print("solution Times : ", fullRouteTime, coarsenedRouteTime)
            print(n)



            # add solved route to list for post-processing
            #SolutionList.append([route, solvedRoute, solvedCoarseRoute, timeToSolveFull, timeToSolveCoarse])

    # complete data analytics Solutions:
    for result in SolutionList:
        coarseningMetrics = result[0].generateCoarseningMetrics()
        #results = solvedRoute.evaluateKPIs()
