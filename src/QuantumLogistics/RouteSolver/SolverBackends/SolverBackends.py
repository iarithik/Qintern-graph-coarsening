from abc import ABC, abstractclassmethod
import pulp as pl
import numpy as np
import cplex
import pandas as pd


#import encoder

class solver(ABC):

    def __init__(self):

        return

    @abstractclassmethod
    def solve(self, problemFormat, config):
        """
            This accepts a standardised problemFormat datatype (dependant on encoder) and runs the problem using a specified solver backend.

            This format should be as general as possible to cater to a wide range of solvers. 

            For example:
                ILP problems accepts a PULP problem which encodes the ILP problem
                Standard qubo problems will likely accept a standard 'QUBO' format that can be readily converted into DWAVE, QISKIT etc solver format.

        """

        raise NotImplementedError


class PulpSolver(solver):
    def __init__(self):
        return

    def defineSolver(self):
        """
        """
        raise NotImplementedError("Use either Gurobi or CBC solvers")

    def solve(self, problem: pl.LpProblem, config = None):
        # Define the solver - defaults if no config specified        
        if config:
            gap_rel = config['gapRel']
            timeLimit = config['timeLimit']
        else:
            gap_rel = 0.01
            timeLimit = 300
            print(f"No config specified, defaulting to gap_rel = {gap_rel} and timeLimit {timeLimit}")

        self.solver = self.defineSolver(gap_rel = gap_rel, time_lim = timeLimit)

        prob = problem
        solver = self.solver
        prob.solve(solver)

        print(f'"Status:", {pl.LpStatus[prob.status]}')

        if prob.status ==0:
            print(f'Not possible to find a solution with the tolerance {gap_rel} in {timeLimit}s' )
            return
        
        elif prob.status ==1:
            obj = pl.value(prob.objective)
            print(f'The Objective function Value is: {round(obj,3)}') 

            solution = []
            solution_name = []
            for v in prob.variables():
                solution.append(v.varValue)
                solution_name.append(v.name)
            
            #map the pulp solution format to matchs with CPLEX
            temp = [(ii, jj, int(jj.split('_')[1])) for ii, jj in zip(solution, solution_name)]
            df = pd.DataFrame(temp, columns = ["Value", "Name", "position"])
            df = df.sort_values(by="position")
            x = df.Value.values
            solution_name = df.Name.values
            return x
                
        else:
            print('Problem is infeasible')
            return


class GurobiSolver(PulpSolver):
    def defineSolver(self, gap_rel, time_lim):
        return pl.GUROBI_CMD(msg=1, gapRel=gap_rel, timeLimit=time_lim)


class CBCSolver(PulpSolver):
    def defineSolver(self, gap_rel, time_lim):
        return pl.PULP_CBC_CMD(msg=1, gapRel=gap_rel, timeLimit=time_lim)
    

class CPLEXSolver(PulpSolver):
    def defineSolver(self, gap_rel, time_lim):
        return pl.CPLEX_PY(msg=1, gapRel=gap_rel, timeLimit=time_lim)




class CPLEXNativeSolver(solver):

    def __init__(self):

        return



    def solve(self, my_prob:cplex.Cplex):

        try:
            my_prob.solve()
        except cplex.CplexError as exc:
            print(exc)
            return

        x = my_prob.solution.get_values()
        x = np.array(x)
        cost = my_prob.solution.get_objective_value()

        #needs a consistent return - 
        return x



