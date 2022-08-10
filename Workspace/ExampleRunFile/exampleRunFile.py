# Standard Imports
import numpy as np
from time import time

# Custom Imports
from QuantumLogistics import logisticsGraph, Route, StandardRouteSolver, CompositeRouteSolver, ILPPulpEncoder, GurobiSolver, CBCSolver, DeltaCoarseningEngine

#################################################
#################################################
# GO TO THE BOTTOM OF THE FILE TO PUT YOUR CODE IN
#################################################
#################################################

def solveRoutingProblem(testSolver: CompositeRouteSolver, testSolverConfig: dict, numberTrucks = 2, numberOfNodes = 15, verbose = False):
    """
        Example run file to test Quantum Optimisation Algorithm on the Vehicle Routing Problem
    """
    ############################################################################################################################
    # 1. Graph Definition
    ############################################################################################################################
    # This defines the primary features of the graph to be studied
    #   This is in the CVRP problem - with 'node demand'. Leave at 0.1 for general work
    graphTypes = ["fully_connected"]
    singleNodeCapacity = 0.1
    nodeCapacityDefinition = numberOfNodes * [singleNodeCapacity]  # A list of nodes 

    #+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+
    ############################################################################################################################
    # 2. Route Object Definiton
    ############################################################################################################################
    # This defines the operating details for the route (i.e number of trucks, truck capacity (how many nodes can a truck go to))
    #   For even distribution of trucks set routeConfig['truckCapacity'] == -1
    routeConfig = {     'vehicles' : numberTrucks,
                        'depot' : 0, 
                        'truckCapacity': -1}  # Set to -1 for auto (will evenly distribute trucks)

    ## Modifying truck capacity if set to auto
    if routeConfig['truckCapacity'] == -1:        
        Q = singleNodeCapacity * np.ceil((numberOfNodes+1) / routeConfig['vehicles'])
        routeConfig['truckCapacity'] = Q

    # Define Coarsening Object/methods 
    # This is if coarsening is set to true (i.e the optimiser coarsens the graph before solving)
    coarsenConfig = {'coarsenRate' : 0.5,
                     'radiusCoefficient': 0.2}

    coarseningEngine = DeltaCoarseningEngine(coarsenConfig)

    #+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+
    ############################################################################################################################
    # 3. Solver Definiton 
    ############################################################################################################################

    # Define solver - using ILP encoder with CBC Solver for example
    solver = testSolver
    solverConfig = testSolverConfig

    #+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+
    ############################################################################################################################
    # 4. Solving
    ############################################################################################################################

    # statistical analysis
    numberofGraphSamples = 20

    #generate a list of seeds used in run (for future reference)
    np.savetxt("seedFiles.txt",np.random.randint(50000, size = numberofGraphSamples))

    #Loading Seeds
    seeds = np.loadtxt("seedFiles.txt").astype(np.int32)

    #numberofGraphSamples = len(seeds)

    SolutionList = []

    for graphType in graphTypes:
        for runNumber in range(numberofGraphSamples):
            
            #Define the network object
            LogisticsNetwork = logisticsGraph(nodeCapacityDefinition, seed = seeds[runNumber], graph_type = graphType)

            LogisticsNetwork.generate_graph()

            # Plotting the network
            if verbose == True:
                LogisticsNetwork.plotGraph()

            #Create the route object
            route = Route(LogisticsNetwork, routeConfig, coarseningEngine = coarseningEngine)
            route.coarsen = False # indicates coarsening is required

            # Solving
            timeInitial = time()
            solvedRoute = solver.solve(route, config = solverConfig)
            routeTime = time() - timeInitial
            print(routeTime)

            if verbose == True:
                route.visualiseSolution(solvedRoute)
            coarseCost = route.calculateCost(solvedRoute)

            # add solved route to list for post-processing
            SolutionList.append([route, solvedRoute, routeTime])

    # ANALYTICS COMING SOON
    # # complete data analytics Solutions:
    # for result in SolutionList:
    #     coarseningMetrics = result[0].generateCoarseningMetrics()
    #     #results = solvedRoute.evaluateKPIs()

    return SolutionList



if __name__ == "__main__":

    #####################
    # YOUR CODE GOES HERE
    
    # See src\RouteSolver\RouteSolvers.py for details on solver interface

    # Make sure you have also imported your solver into the src\QuantumLogistics\__init__.py file
    #####################

    # General Problem Details:
    numberOfNodes = 15
    numberTrucks = 2

    plotOutputs = False

    # The classical baseline solver: Known to give optimal results through an ILP formulation
    #solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver())

    # YOUR SOLVER HERE
    solver = StandardRouteSolver(ILPPulpEncoder(), CBCSolver())

    solverConfig = {"testVar": 1,
                    "gapRel" : 0.01,
                    "timeLimit" : 300}

    # solve Problem: (30 optimisation runs)
    solutionList = solveRoutingProblem(solver, solverConfig, numberTrucks = numberTrucks, numberOfNodes = numberOfNodes, verbose = plotOutputs)
    