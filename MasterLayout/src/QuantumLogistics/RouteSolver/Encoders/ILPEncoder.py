import numpy as np
import pandas as pd
import math
import pulp as pl
import cplex

#Custom Imports
from QuantumLogistics import Route
from .StandardEncoder import Encoder


class ILPPulpEncoder(Encoder):
    """
        Converts VRP problem into a PuLP ILP problem.
        This is used for classical solvers.
    """
    def __init__(self):

        return


    def encode(self, route:Route) -> pl.LpProblem:
        """Uses pulp to return the definition of ILP problem"""
        # to remember the route characteristics
        self.route = route
        n = route.n
        K = route.vehicles
        graphAdjMatr = route.graph.W.toarray() 

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
        my_obj = list(graphAdjMatr.reshape(1, n ** 2)[0]) + [0.0 for x in range(0, n - 1)]
        weight_opt = dict(zip(dec_vars, my_obj))

        # Define the Objective function
        prob += pl.lpSum([weight_opt[i]*dec_vars[i] for i in dec_total])
        
        # Define the Constrains      
        Q = 10
        # create the array with all the right hand size contrainst values
        my_rhs = (
            2 * ([K] + [1 for x in range(0, n - 1)])
            + [Q - 0.1 for x in range(0, (n - 1) ** 2 - (n - 1))]
            + [0 for x in range(0, n)]
        )

        # subject to the node-visiting and the depot-visiting constraints:
        count = 0
        #Q: is ii NODEIDX???
        for ii in range(0, n):
            # summing by row - paths leaving city
            col = [x for x in range(0 + n * ii, n + n * ii)]
            #print("For ii = {0}, col = {1}".format(ii, col))
            prob += pl.lpSum([dec_vars[k] for k in col]) == my_rhs[count]
            #print([dec_vars[k] for k in col])
            #print(my_rhs[count])
            #print("\n")
            count += 1

        #print("\n New ONE ")
        for ii in range(0, n):
            # Summing across column - paths into city
            col = [x for x in range(0 + ii, n ** 2, n)]
            #print("For ii = {0}, col = {1}".format(ii, col))

            prob += pl.lpSum([dec_vars[k] for k in col]) == my_rhs[count]
            #print([dec_vars[k] for k in col])
            #print(my_rhs[count])
            #print("\n")
            count += 1


        # and the sub-tour elimination constraints:
        for ii in range(0, n):
            for jj in range(0, n):
                if (ii != jj) and (ii * jj > 0): # if i or j not 0
                    #print(ii,jj)
                    col = [ii + (jj * n), n ** 2 + ii - 1, n ** 2 + jj - 1]
                    coef = [Q, 1, -1]
                    prob += pl.lpSum([co*dec_vars[k] for co, k in zip(coef,col)]) <= my_rhs[count]
                    #print([co*dec_vars[k] for co, k in zip(coef,col)])
                    #print(my_rhs[count])
                    #print("\n")
                    count += 1
        
        # set the diagonal elements to zero , i=j
        for ii in range(0, n):
            col = [(ii) * (n + 1)]
            prob += pl.lpSum([dec_vars[k] for k in col]) == my_rhs[count]
            count += 1   
        
        return prob


    def addCapacityConstraints(self):
        raise NotImplementedError

    def addTWConstraints(self):
        raise NotImplementedError




    def extract(self, solution, verbose = False):
        """
            Returns the route lists from the PULP ILP in the correct format
        """
        # convert to route solution format
        #route information
        n = self.route.n
        _k = n*n
        depotIdx = self.route.depot
        vehicleNumber = self.route.vehicles

        # After solving the Linear Program, it is needed to extract the routes from the solution
        routes = []
        _chain = []

        travel_metrices = solution[0:_k].reshape((n, n))

        for ix in range(0, n):
            for iy in range(0, n):
                if travel_metrices[ix][iy] > 0:
                    if (ix, iy) not in _chain and ix != iy:
                        _chain += [(ix, iy)]
        
        for vehicle in range(vehicleNumber):
            cur = depotIdx
            route = []
            travel = True
            if verbose: print(f"{cur}", end='  ')
            while travel:
                element = [(_from, _to) for (_from, _to) in _chain if _from == cur]
                (_from, _to) = element[vehicle] if len(element) > 1 else element[0]
                cur = _to
                route += [(_from, _to)]
                if verbose: print(f"->  {_to}", end='  ')
                if cur == depotIdx:
                    travel = False
            routes += [route]
            if verbose: print()

        # Check if all vehicles are accounted for, while calcultaing the routes
        assert len(routes) == vehicleNumber

        return routes












class ILPCPLEXEncoder(ILPPulpEncoder):
    """
        Converts the route into an ILP problem
        Inherits the extract() method from the ILPPulpEncoder Class (they have equivalent answers)
    """

    def encode(self,route) -> cplex.Cplex:
        # to remember the route characteristics
        self.route = route
        n = route.n
        K = route.vehicles
        graphAdjMatr = route.graph.W.toarray() 

        Q = 10
        
        my_obj = list(graphAdjMatr.reshape(1, n ** 2)[0]) + [0.0 for x in range(0, n - 1)]
        my_ub = [1 for x in range(0, n ** 2 + n - 1)]
        my_lb = [0 for x in range(0, n ** 2)] + [0.1 for x in range(0, n - 1)]
        my_ctype = "".join(["I" for x in range(0, n ** 2)]) + "".join(
            ["C" for x in range(0, n - 1)]
        )

        my_rhs = (
            2 * ([K] + [1 for x in range(0, n - 1)])
            + [Q - 0.1 for x in range(0, (n - 1) ** 2 - (n - 1))]
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
        except cplex.CplexError as exc:
            print(exc)
            return

        return my_prob


    def populatebyrow(self, prob, my_obj, my_ub, my_lb, my_ctype, my_sense, my_rhs):

        Q = 10 #THIS NEEDS TO BE PROVED AND INTEGRATED BETTER

        n = self.route.n

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
                    coef = [Q, 1, -1]

                    rows.append([col, coef])

        for ii in range(0, n):
            col = [(ii) * (n + 1)]
            coef = [1]
            rows.append([col, coef])

        prob.linear_constraints.add(lin_expr=rows, senses=my_sense, rhs=my_rhs)







