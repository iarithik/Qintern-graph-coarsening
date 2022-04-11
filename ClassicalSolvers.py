import numpy as np
import pandas as pd
import math
import pulp as pl
import cplex


class ClassicalOptimizer:
    def __init__(self, instance, n, K):

        self.instance = instance
        self.n = n  # number of nodes
        self.K = K  # number of vehicles

    def compute_allowed_combinations(self):
        f = math.factorial
        return f(self.n) / f(self.K) / f(self.n - self.K)
    
    def ilp_model(self):
        """Uses pulp to return the definition of ILP problem"""
        #get the variable:
        n = self.n
        K = self.K
        instance = self.instance
        
        # Start the LP problem definition
        prob = pl.LpProblem("VRP", pl.LpMinimize)

        # define the decision variable
        dec_x = list(range(n ** 2))
        dec_u = list(range(dec_x[-1] + 1, dec_x[-1] + n))
        dec_total = dec_x + dec_u

        var_x = pl.LpVariable.dicts("x", dec_x, 0, 1, cat='Integer')
        var_u = pl.LpVariable.dicts("u", dec_u, 0.1, 1, cat="Continuous")

        # merge both dictionaries
        l = [var_x, var_u]
        dec_vars = {**l[0], **l[1]}

        # create the dictonary for the weights:
        my_obj = list(instance.reshape(1, n ** 2)[0]) + [0.0 for x in range(0, n - 1)]
        weight_opt = dict(zip(dec_vars, my_obj))

        # Define the Objective function
        prob += pl.lpSum([weight_opt[i]*dec_vars[i] for i in dec_total])
        
        # Define the Constrains      
        
        # create the array with all the right hand size contrainst values
        my_rhs = (
            2 * ([K] + [1 for x in range(0, n - 1)])
            + [1 - 0.1 for x in range(0, (n - 1) ** 2 - (n - 1))]
            + [0 for x in range(0, n)]
        )
        
        # subject to the node-visiting and the depot-visiting constraints:
        count = 0
        for ii in range(0, n):
            col = [x for x in range(0 + n * ii, n + n * ii)]
            prob += pl.lpSum([dec_vars[k] for k in col]) == my_rhs[count]
            count += 1

        for ii in range(0, n):
            col = [x for x in range(0 + ii, n ** 2, n)]
            prob += pl.lpSum([dec_vars[k] for k in col]) == my_rhs[count]
            count += 1

        # and the sub-tour elimination constraints:
        for ii in range(0, n):
            for jj in range(0, n):
                if (ii != jj) and (ii * jj > 0):
                    col = [ii + (jj * n), n ** 2 + ii - 1, n ** 2 + jj - 1]
                    coef = [1, 1, -1]
                    prob += pl.lpSum([co*dec_vars[k] for co, k in zip(coef,col)]) <= my_rhs[count]
                    count += 1
        
        # set the diagonal elements to zero , i=j
        for ii in range(0, n):
            col = [(ii) * (n + 1)]
            prob += pl.lpSum([dec_vars[k] for k in col]) == my_rhs[count]
            count += 1   
        
        return prob
    
    def gurobi_solution(self):
        n = self.n
        prob = self.ilp_model()
        gap_rel = 0.01
        time_lim = 300 # time in seconds
        solver = pl.GUROBI_CMD(msg=1, gapRel=gap_rel, timeLimit=time_lim) 
        prob.solve(solver)
        print(f'"Status:", {pl.LpStatus[prob.status]}')
        if prob.status ==0:
            print(f'Not possible to find a solution with the tolerance {gap_rel} in {time_lim}s' )
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
            return(x, obj, solution_name)
                
        else:
            print('Problem is infeasible')
            return
    
    def cbc_solution(self):
        n = self.n
        prob = self.ilp_model()
        gap_rel = 0.01
        time_lim = 300 # time in seconds
        solver = pl.PULP_CBC_CMD(msg=1, gapRel=gap_rel, timeLimit=time_lim) 
        prob.solve(solver)
        print(f'"Status:", {pl.LpStatus[prob.status]}')
        
        if prob.status ==0:
            print(f'Not possible to find a solution with the tolerance {gap_rel} in {time_lim}s' )
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
            temp = [(ii, jj,int(jj.split('_')[1])) for ii, jj in zip(solution, solution_name)]
            df = pd.DataFrame(temp, columns = ["Value", "Name", "position"])
            df = df.sort_values(by="position")
            x = df.Value.values
            return(x, obj, solution_name)
        
        else:
            print('Problem is infeasible')
            return
    
    def cplex_solution(self):

        # refactoring
        instance = self.instance
        n = self.n
        K = self.K

        my_obj = list(instance.reshape(1, n ** 2)[0]) + [0.0 for x in range(0, n - 1)]
        my_ub = [1 for x in range(0, n ** 2 + n - 1)]
        my_lb = [0 for x in range(0, n ** 2)] + [0.1 for x in range(0, n - 1)]
        my_ctype = "".join(["I" for x in range(0, n ** 2)]) + "".join(
            ["C" for x in range(0, n - 1)]
        )

        my_rhs = (
            2 * ([K] + [1 for x in range(0, n - 1)])
            + [1 - 0.1 for x in range(0, (n - 1) ** 2 - (n - 1))]
            + [0 for x in range(0, n)]
        )
        my_sense = (
            "".join(["E" for x in range(0, 2 * n)])
            + "".join(["L" for x in range(0, (n - 1) ** 2 - (n - 1))])
            + "".join(["E" for x in range(0, n)])
        )

        try:
            my_prob = cplex.Cplex()
            self.populatebyrow(my_prob, my_obj, my_ub, my_lb, my_ctype, my_sense, my_rhs)

            my_prob.solve()

        except CplexError as exc:
            print(exc)
            return

        x = my_prob.solution.get_values()
        x = np.array(x)
        cost = my_prob.solution.get_objective_value()

        return x, cost, my_sense


    def populatebyrow(self, prob, my_obj, my_ub, my_lb, my_ctype, my_sense, my_rhs):

        n = self.n

        prob.objective.set_sense(prob.objective.sense.minimize)
        prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype)

        prob.set_log_stream(None)
        prob.set_error_stream(None)
        prob.set_warning_stream(None)
        prob.set_results_stream(None)

        rows = []
        for ii in range(0, n):
            col = [x for x in range(0 + n * ii, n + n * ii)]
            coef = [1 for x in range(0, n)]
            rows.append([col, coef])

        for ii in range(0, n):
            col = [x for x in range(0 + ii, n ** 2, n)]
            coef = [1 for x in range(0, n)]

            rows.append([col, coef])

        # Sub-tour elimination constraints:
        for ii in range(0, n):
            for jj in range(0, n):
                if (ii != jj) and (ii * jj > 0):

                    col = [ii + (jj * n), n ** 2 + ii - 1, n ** 2 + jj - 1]
                    coef = [1, 1, -1]

                    rows.append([col, coef])

        for ii in range(0, n):
            col = [(ii) * (n + 1)]
            coef = [1]
            rows.append([col, coef])

        prob.linear_constraints.add(lin_expr=rows, senses=my_sense, rhs=my_rhs)