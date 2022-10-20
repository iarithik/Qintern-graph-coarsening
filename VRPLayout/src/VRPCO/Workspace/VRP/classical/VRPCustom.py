from ortools.sat.python import cp_model
import numpy as np

from classical.VRPSolution import Route, VRPSolution

"""
Solving a custom (designed by Adam and Ozlem) formulation of VRP using CP-SAT solver.
"""


class VRPCustom:
    """Solver for Vehicle Routing Problem - classical implementation"""

    def __init__(self, n, m, cost):
        self.cities_num = n  # number of cities
        self.N = self.cities_num - 1
        self.K = m  # number of vehicles
        self.d = cost  # cost/weight matrix (distances between cities)
        self.sol = None  # solution of VRPTW problem
        self.model = cp_model.CpModel()
        self.cp_model_variables = None

        self.V = set(range(self.N + 1))
        self.V_prim = self.V.union(set(range(self.N + 1, self.N + self.K)))

        self.d = np.zeros((self.N + self.K, self.N + self.K))
        self.d[: self.N + 1, : self.N + 1] = cost

        self.formulate()

    def formulate(self):
        """--------------------- Variables definition: ---------------------"""
        x = [[None] * (self.N + self.K) for _ in range(self.N + self.K)]
        for i in range(self.N + self.K):
            for j in range(self.N + self.K):
                if i != j:
                    x[i][j] = self.model.NewBoolVar(f"x.{i}.{j}")

        # for linearization of objective function
        z = {}
        for t in range(len(self.V_prim) - 1):
            for v in self.V_prim:
                for w in self.V_prim:
                    if t != v and t + 1 != w:
                        z[(t, v, w)] = self.model.NewBoolVar(f"z.{t}.{v}.{w}")
        
        self.cp_model_variables = x + list(z.values())

        """-------------------------- Constraints: -------------------------"""

        # (1) exactly one outgoing edge in each vertex
        for v in self.V_prim:
            self.model.Add(sum(x[t][v] for t in range(len(self.V_prim)) if t != v) == 1)

        # (2) exactly one incoming edge in each vertex
        for t in range(len(self.V_prim)):
            self.model.Add(sum(x[t][v] for v in self.V_prim if t != v) == 1)

        # (3) we cannot go from depot to depot (including port copies)
        for t in range(len(self.V_prim) - 1):
            sum1 = sum((x[t][v]) for v in range(self.N, self.N + self.K) if t != v)
            sum2 = sum((x[t + 1][v]) for v in range(self.N, self.N + self.K) if t + 1 != v)
            sum3 = sum1 + sum2
            self.model.Add(sum3 <= 1)

        # for linearization of objective function
        for t in range(len(self.V_prim) - 1):
            for v in self.V_prim:
                for w in self.V_prim:
                    if t != v and t + 1 != w:
                        self.model.Add(z[(t, v, w)] <= x[t][v])
                        self.model.Add(z[(t, v, w)] <= x[t + 1][w])
                        self.model.Add(z[(t, v, w)] >= x[t][v] + x[t + 1][w] - 1)
        
        """--------------------------- Objective: --------------------------"""
        self.model.Minimize(
            sum(
                self.d[v][w] * z[(t, v, w)]
                for t in range(len(self.V_prim) - 1)
                for v in self.V_prim
                for w in self.V_prim
                if v != w and t != v and t + 1 != w
            )
        )

    def preplllare_solution(self, solver) -> VRPSolution:
        objective = 0
        routes = []
        for v in self.cp_model_variables:
            route = Route()  # 'vehicle cities distance'
            routes.append(route)
        return VRPSolution(objective, routes)
    
    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self.prepare_solution(solver)

        return None

