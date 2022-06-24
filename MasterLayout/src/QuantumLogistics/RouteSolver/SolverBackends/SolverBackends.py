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
    def solve(encoder):

        raise NotImplementedError


class PulpSolver(solver):
    def __init__(self, gap_rel = 0.01, time_lim = 300):
        self.gap_rel = gap_rel
        self.time_lim = time_lim
        self.solver = self.defineSolver()
        return

    def defineSolver(self):
        """
        """
        raise NotImplementedError("Use either Gurobi or CBC solvers")

    def solve(self, problem: pl.LpProblem):
        prob = problem
        solver = self.solver
        prob.solve(solver)

        print(f'"Status:", {pl.LpStatus[prob.status]}')

        if prob.status ==0:
            print(f'Not possible to find a solution with the tolerance {self.gap_rel} in {self.time_lim}s' )
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
    def defineSolver(self):
        return pl.GUROBI_CMD(msg=1, gapRel=self.gap_rel, timeLimit=self.time_lim)


class CBCSolver(PulpSolver):
    def defineSolver(self):
        return pl.PULP_CBC_CMD(msg=1, gapRel=self.gap_rel, timeLimit=self.time_lim)
    

class CPLEXSolver(PulpSolver):
    def defineSolver(self):
        return pl.CPLEX_PY(msg=1, gapRel=self.gap_rel, timeLimit=self.time_lim)




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



