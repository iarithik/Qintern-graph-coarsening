from abc import ABC, abstractclassmethod

from QuantumLogistics import Route # solver #, Encoder, solver

class CompositeRouteSolver(ABC):
    """
        Abstract class to solve logistics problem on routes
        This is the most general type of solver that only required a solveAlgorithm and extractSolution definiton. 
        SOLVE() SHOULD *NOT* BE OVERWRITTEN. Only overwrite solveAlgorithm() and extractSolution()
    """

    def __init__(self):
        raise NotImplementedError

    
    def solve(self,route:Route, config = None):
        #Manages graph coarsening if needed. 

        # check if graph must be coarsened
        if route.coarsen:
            route.coarsenGraph()

        problemSol = self.solveAlgorithm(route)
        routeSol = self.extractSolution(problemSol)

        if route.coarsen:
            route.inflateGraph()

        return routeSol


    @abstractclassmethod
    def extractSolution(self):
        """
            Must output a standard solution list
        """
        raise NotImplementedError


    @abstractclassmethod
    def solveAlgorithm(self):
        """
            Returns raw output from solver in terms of decision vars
        """

        raise NotImplementedError







class StandardRouteSolver(CompositeRouteSolver):

    def __init__(self, encoder, solver):
        self.encoder = encoder
        self.solver = solver
        return


    def extractSolution(self,solverSolution):
        # must return standard solution
        return self.encoder.extract(solverSolution)


    def solveAlgorithm(self, route:Route):
        #Encode problem
        problem = self.encoder.encode(route)

        #solving problem
        problemSol = self.solver.solve(problem)

        return problemSol






# example of defining class:
# StandardQAOAQISKIT = StandardRouteSolver(baseQUBO, QiskitSolver)

