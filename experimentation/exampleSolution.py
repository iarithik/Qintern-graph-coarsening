# Definitions
# VRP Graph - collection of (x,y) points representing locations. Assumes all locations are fully connected
# Route - a sequence (or combination of sequences) travelled by a vehicle to reach all (x,y) points in route
# VRPSolver - an object which 

if __name__ == "__main__":

    # example of comparing multiple types of solvers

    # 1. generate graph object - loading in from a saved file
    graphFileName = 'experimentalGraph.csv'
    LogNetwork = LogisticsGraph(loadFromeFile = True, filename = graphFileName)

    # 2. Define configuration for route:
    config = {  'vehicles' : 7,
                'depot' : 0,
                'capacity': -1,
                'demand': -1  }

    # 3. Define solvers to compare: (including all variations etc)
    solverList = [VRPClassicalSolver, VRPQAOASolver, VRPVQESolver, VRPQASolver]
    solutionList = []

    # 4. Iterate through solver list and solve for each tested
    for solver in solverList:
        # define route
        route = LogisticsRoute(LogNetwork, config, coarseningObject)

        route.coarsenGraphBool = True

        # solve route - coarsens graph within coarsen function
        solvedRoute = solver.solve(route, solverConfig)
        
        #set route solution
        route.solution = solvedRoute

        # add solved route to list for post-processing
        solutionList.append(solvedRoute)

        # Visualise Route
        route.visualiseSolution()

    # 5. Post Process - can also do it while solving stuff
    for solvedRoute in solutionList:
        results = solvedRoute.evaluateKPIs()