import numpy as np
from time import time
import csv, os


from QuantumLogistics import logisticsGraph, Route, StandardRouteSolver, ILPPulpEncoder, GurobiSolver, CBCSolver, DeltaCoarseningEngine, CompositeRouteSolver, GurobiSolver2
from QuantumLogistics.LogisticsRoute.VrpRepGraph import vrpRepGraph

def solveRoutingProblem(graphFile:str, testSolver: CompositeRouteSolver, testSolverConfig: dict, numberTrucks = 2, numberOfNodes = 15, coarseningRate = 0.5, verbose = False):
    """
        Example run file to test Quantum Optimisation Algorithm on the Vehicle Routing Problem
    """
    ############################################################################################################################
    # 1. Graph Definition
    ############################################################################################################################
    # This defines the primary features of the graph to be studied
    #   This is in the CVRP problem - with 'node demand'. Leave at 0.1 for general work
    graphType = "fully_connected"
    singleNodeCapacity = 0.1
    nodeCapacityDefinition = numberOfNodes * [singleNodeCapacity]  # A list of nodes 

    #+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+
    ############################################################################################################################
    # 2. Route Object Definiton
    ############################################################################################################################
    # This defines the operating details for the route (i.e number of trucks, truck capacity (how many nodes can a truck go to))
    #   For even distribution of trucks set routeConfig['truckCapacity'] == -1
    routeConfig = {     'vehicles' : numberTrucks,
                        'depot' : 76, 
                        'truckCapacity': 140}  # Set to -1 for auto (will evenly distribute trucks)

    ## Modifying truck capacity if set to auto
    if routeConfig['truckCapacity'] == -1:        
        Q = singleNodeCapacity * np.ceil((numberOfNodes+1) / routeConfig['vehicles'])
        routeConfig['truckCapacity'] = Q

    # Define Coarsening Object/methods 
    # This is if coarsening is set to true (i.e the optimiser coarsens the graph before solving)
    coarsenConfig = {'coarsenRate' : coarseningRate,
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

    SolutionList = []


    # Define the network object
    network = vrpRepGraph(graphFile)
    network.generate_graph()

    # Plotting the network
    if verbose == True:
        network.plotGraph()

    # Create the route object
    route = Route(network, routeConfig, coarseningEngine = coarseningEngine)

    # indicates coarsening is required
    route.coarsen = False 
    if coarseningRate < 1:
        route.coarsen = True

    # Solving Network
    solvedCoarseRoute, coarseSolveTime, coarseCost = solver.solve(route, config = solverConfig)
    coarseMIPGap = 0

    # Saving images
    rootFilePath = str(numberOfNodes) + '_' + str(numberTrucks) + '_' + str(coarsenConfig['coarsenRate']) + '_' + str(runNumber) + "saveImage.png"
    fineFilePath = "fine_" + rootFilePath
    coarseFilePath = rootFilePath
    route.visualiseSolution(solvedCoarseRoute, saveImgFilepath=coarseFilePath)

    #Output
    solutionList = [numberOfNodes, numberTrucks, coarsenConfig['coarsenRate'], runNumber, coarseCost, coarseSolveTime, coarseCost, coarseSolveTime]

    # Resetting csv File
    print("to csv")
    with open("csvOutputFile.csv", "a", newline = '') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(solutionList)

    return SolutionList



if __name__ == "__main__":

    # General Problem Details:
    numberOfNodes = 15
    numberTrucks = 1

    plotOutputs = False

    # The classical baseline solver: Known to give optimal results through an ILP formulation
    # solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver())
    solver = StandardRouteSolver(ILPPulpEncoder(), CBCSolver())
    #solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver2())

    solverConfig = {"testVar": 1,
                    "gapRel" : 0.005,
                    "timeLimit" : 600}

    graphSize = 76
    coarseningRate = 0.3

    # Resetting csv File
    with open("csvOutputFile.csv", "w", newline = '') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow([0])

    inputVect = {   "numberOfNodes" : graphSize, 
                    "numberTrucks": numberTrucks, 
                    "coarseningRate": coarseningRate, 
                    "verbose" : plotOutputs, 
                }

    # solve Problem: (30 optimisation runs)
    print("Testing with coarsening Rate ", coarseningRate)
    print("Testing with size: ", graphSize)

    graphDir = "/workspace/21_solving-vehicle-routing-problem-and-its-variants-using-quantum-computing_b/dataset/"

    for root, dirs, files in os.walk(graphDir):
        for f in files:
            if "02.xml" in f: # Only runs the 02.xml file
                file = os.path.join(root, f)
                print(f'Running graph file {file}...')
                solutionList = solveRoutingProblem(file, solver, solverConfig, **inputVect)
                print(solutionList)
    
    # Need to start from Run 12, 50 nodes, 0.5 coarsening