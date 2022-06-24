import numpy as np

from QuantumLogistics import logisticsGraph, Route, StandardRouteSolver, ILPPulpEncoder, GurobiSolver, CBCSolver

if __name__ == "__main__":
    # experimental design for graph coarsening
    # If using random number generators will need to do statistical (repeatable) experiments for each type
    # This code serves as a 'guiding light' to design the new code for this experiment.

    # 1. Graphs types
    graphTypes = ["fully_connected"] #, "random", "small_world"]
    numberOfNodes = 15

    # Define route configuration
    config = {  'vehicles' : 5,
                'depot' : 0,
                'capacity': -1,
                'demand': -1  }

    # Define solver - using ILP encoder with Gurobi Solver
    solver = StandardRouteSolver(ILPPulpEncoder(), CBCSolver())
    solverConfig = {"testVar":1}

    ##############################################################
    ##############################################################
    ##############################################################

    #COARSENING HAPPENS HERE
    # Define Coarsening Object/methods
    # coarseningObject = DeltaCoarsening()

    ##############################################################
    ##############################################################
    ##############################################################

    # statistical analysis
    numberofGraphSamples = 30

    #generate a list of seeds used in run (for future reference)
    #np.savetxt("seedFiles.txt",np.random.randint(50000, size = numberofGraphSamples))
    seeds = np.loadtxt("seedFiles.txt", dtype = np.int32)

    SolutionList = []

    for graphType in graphTypes:
        for runNumber in range(numberofGraphSamples):
            
            #Define the network
            LogisticsNetwork = logisticsGraph(numberOfNodes, seed = seeds[runNumber], graph_type = graphType)
            LogisticsNetwork.generate_graph()

            #Create the route object
            route = Route(LogisticsNetwork, config)

            # solve route with FULL graph
            solvedRoute = solver.solve(route, config = solverConfig)
            timeToSolveFull = 0

            route.visualiseSolution(solvedRoute)
            print(route.calculateCost(solvedRoute))

            # solve route with COARSENED graph
            route.coarsen = False # True # indicates coarsening is required
            solvedCoarseRoute = solver.solve(route, config)
            timeToSolveCoarse = 0

            # add solved route to list for post-processing
            SolutionList.append([route, solvedRoute, solvedCoarseRoute, timeToSolveFull, timeToSolveCoarse])

    # complete data analytics Solutions:
    for result in SolutionList:
        coarseningMetrics = result[0].generateCoarseningMetrics()
        results = solvedRoute.evaluateKPIs()


