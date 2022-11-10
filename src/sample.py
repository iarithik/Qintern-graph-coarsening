import numpy as np
from time import time
import csv, os


from QuantumLogistics import logisticsGraph, Route, StandardRouteSolver, ILPPulpEncoder, GurobiSolver, CBCSolver, DeltaCoarseningEngine, CompositeRouteSolver, GurobiSolver2
from QuantumLogistics.LogisticsRoute.VrpRepGraph import vrpRepGraph


if __name__ == "__main__":
    graphDir = "/workspace/21_solving-vehicle-routing-problem-and-its-variants-using-quantum-computing_b/dataset/"

    for root, dirs, files in os.walk(graphDir):
        for f in files:
            if "11.xml" in f: # Only runs the 02.xml file

                file = os.path.join(root, f)
                print(f'[i] Loading graph file {f}...')

                # Define the network object
                network = vrpRepGraph(file)

                network.generate_graph()


                print(f'[i] Setting graph configurations for {f}...')
                # General Problem Details:
                numberOfNodes = network.n
                numberTrucks = int(network.nodelist.vehicle['capacity']) # depot's capacity, i.e. no. of trucks
                truckCapacity = max(network.nodeCapacities)
                depot = network.nodelist.vehicle['arrival_node']

                verbose = False

                print(f'[i] Setting route solver for {f}...')
                # The classical baseline solver: Known to give optimal results through an ILP formulation
                solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver())
                # solver = StandardRouteSolver(ILPPulpEncoder(), CBCSolver())
                # solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver2())

                # Plotting the network
                if verbose == True:
                    print(f'[i] Plotting graph for {f}...')
                    network.plotGraph()

                print(f'[i] Setting coarsening engine for {f}...')
                coarseningRate = 0.3
                radiusCoefficient = 0.5

                coarseningEngine = DeltaCoarseningEngine(
                    coarsenRate = coarseningRate,           # 0.3
                    radiusCoefficient = radiusCoefficient   # 0.2
                )
                
                print(f'[i] Creating route solver for {f}...')
                # Create the route object 
                route = Route(network, 
                    vehicles = 1, # numberTrucks,    # 18
                    depot = depot, # network.nodelist.vehicle['arrival_node'],    # 76
                    truckCapacity = truckCapacity,     # 37
                    coarseningEngine = coarseningEngine 
                )

                # indicates coarsening is required
                route.coarsen = False 
                if coarseningRate < 1:
                    route.coarsen = True



                print(f'[i] Running graph solver for {f}...')
                # Solving Network
                solverConfig = {"testVar": 1, "gapRel" : 0.005, "timeLimit" : 600}
                solvedCoarseRoute, coarseSolveTime, coarseCost = solver.solve(route, config = solverConfig)
                coarseMIPGap = 0





                print(f'[i] Saving path image for {f}...')
                # Saving images
                rootFilePath = str(numberOfNodes) + '_' + str(numberTrucks) + '_' + str(coarseningRate) + "saveImage.png"
                fineFilePath = "fine_" + rootFilePath
                coarseFilePath = rootFilePath
                route.visualiseSolution(solvedCoarseRoute, saveImgFilepath=coarseFilePath)

                print(f'[i] Saving path data to csv for {f}...')
                #Output
                solutionList = [numberOfNodes, numberTrucks, coarseningRate, coarseCost, coarseSolveTime, coarseCost, coarseSolveTime]

                # Resetting csv File
                print("to csv")
                with open("csvOutputFile.csv", "a", newline = '') as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    writer.writerow(solutionList)