from dimod import ConstrainedQuadraticModel, Binary, Integer, SampleSet
from dwave.system import LeapHybridCQMSampler

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import time

class CVRPTW():
    '''Vehicle routing problem with time-window constraints (node-based formulation)'''
    def __init__(self, n, k, cost, xc, yc, tw):
        '''
        Initializer for Full Qubo Solver with Time Windows
            n: number of cleints (excluding the depot)
            m: number of vehicles
            cost: (n+1) x (n+1) cost matrix 
            xc: a list of (n+1) x-coordinates
            yc: a list of (n+1) y-coordinates
            tw: a list of time windows for each node
        '''
        self.n = n
        self.k = k
        self.cost = cost
        self.xc = xc
        self.yc = yc
        self.tw = tw

        self.sampleset = None
        self.feasible_sampleset = None
        self.sol = None

        self.model = ConstrainedQuadraticModel()
        self.timing = {}

        self.clock = time.time() # Begin stopwatch
        self.formulate() # formulate problem
        self.timing['formulation_time'] = (time.time() - self.clock) * 1e6 # Record build time

    def formulate(self):
        '''
        Formulates the objective function and constraints for the given problem instance.
        Notation:
            d.{v}.{w} is the cost of moving from city v to city w
            x.{t}.{v} = 1 if node v is visited at timestep t
            v is from the set of nodes V_prime = {0, ..., n, n+1, ..., n+k-1},
                where n, n+1, ..., n+k-1 are copies of the depot.
            t is from the set of timesteps {0, ..., |V_prime|-1}
        FIXME: All for loops iterating over time might need to be changed to range(self.n+self.k-1)
        '''
        x = [[Binary(f'x.{t}.{v}') for v in range(self.n+self.k)] for t in range(self.n+self.k)]

        self.model.set_objective(
            sum(self.cost[v][w] * x[t][v] * x[t+1][w] for t in range(self.n+self.k) for v in range(self.n+self.k) for w in range(self.n+self.k) if v != w)
        )

        # --------------- CONSTRAINTS ---------------

        # Ensure that x_{t,v} forms a permutation, which is equivalent to route passing k times through the depot.
        for v in range(self.n+self.k):
            self.model.add_constraint(
                sum(x[t][v] for t in range(self.n+self.k)) == 1
            )

        for t in range(self.n+self.k):
            self.model.add_constraint(
                sum(x[t][v] for v in range(self.n+self.k)) == 1
            )

        # Certify that we can’t go from depot to depot, which in essence forces having K vehicles exactly. 
        # In case we omit this condition, we would have at most K vehicles.
        for t in range(self.n+self.k):
            self.model.add_constraint(
                sum(x[t][v] + x[t+1][v] for v in range(self.n, self.n+self.k)) <= 1
            )

        # Ensure that the vehicle starts at the depot
        self.model.add_constraint(x[0][self.n] == 0)

        # --------------- CAPACITY CONSTRAINTS --------------- 
        '''
        Notation:
            load.{t} represents how much load a vehicle has when visiting a city at time t
            car.{t} identifies which vehicle is used at time t
        '''
        load = [Integer(f'load.{t}') for t in range(self.n+self.k)] 
        car = [Integer(f'load.{t}') for t in range(self.n+self.k)] 

        for t in range(self.n+self.k):
            self.model.add_constraint(
                load[t] <= max(load[t])*(1 - sum(x[t][v] for v in range(self.n, self.n+self.k)))
            )
        
        # TODO: Conditions 2 and 3



        # TODO:--------------- TIME WINDOW CONSTRAINTS ---------------
        '''
        w = [[Integer(f'w.{v}.{t}') for t in range(self.n+2)] for v in range(self.m)]

        # FIXME/TODO: Currently arrival "times" are actually arrival "distances". Need to implement vehicle velocity
        # NOTE for Avneesh: Recall conversation with Carlos
        arrival_times = [[None for t in range(self.n+2)] for v in range(self.m)]
        for v in range(self.m):
            for t in range(1,self.n+1):
                # Intermediate variables
                initial_arrival_time = sum(self.cost[0][i] * x[i][v][t] for i in range(1, self.n+1)) # Assumes x[i][v][t] = 1 for exactly one i for a given v and t
                sum_of_wait_times_at_previous_nodes = sum(w[v][tau] for tau in range(1, t))
                path_cost_sum = sum(self.cost[i][j] * x[i][v][tau-1] * x[j][v][tau] for j in range(1,self.n+1) for i in range(1,self.n+1) for tau in range(2,t+1))
                arrival_times[v][t] = initial_arrival_time + sum_of_wait_times_at_previous_nodes + path_cost_sum

                # Must arrive later than earliest allowed time
                self.model.add_constraint(
                    arrival_times[v][t] + w[v][t] - sum(x[i][v][t] * self.tw[i][0] for i in range(1,self.n+1)) >= 0
                )

                # Must arrive earlier than latest allowed time
                self.model.add_constraint(
                    arrival_times[v][t] + w[v][t] - sum(x[i][v][t] * self.tw[i][1] for i in range(1,self.n+1)) <= 0
                )
        '''


    def solve(self, time_limit = 60):
        sampler = LeapHybridCQMSampler()
        self.sampleset = sampler.sample_cqm(self.model, label=f"Vehicle Routing Problem ({self.n} Clients, {self.m} Vehicles) - FQS", time_limit=time_limit)
        try:
            self.feasible_sampleset = self.sampleset.filter(lambda row: row.is_feasible)
        except Exception as e:
            self.feasible_sampleset = None
        try:
            self.sol = self.feasible_sampleset.first
        except Exception as e:
            self.sol = None
        self.timing['qpu_access_time'] = self.sampleset.info["qpu_access_time"]

    def visualize(self):
        """Visualizes solution"""

        # Initialize figure
        plt.figure()
        ax = plt.gca()
        ax.set_title(f'Vehicle Routing Problem - {self.n} Clients & {self.m} Cars')
        cmap = plt.cm.get_cmap('Accent')

        # Build graph
        G = nx.MultiDiGraph()
        G.add_nodes_from(range(self.n + 1))

        # Plot nodes
        pos = {i: (self.xc[i], self.yc[i]) for i in range(self.n + 1)}
        labels = {i: str(i) for i in range(self.n + 1)}
        nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color='blue', node_size=500, alpha=0.8)
        nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=16)

        # Get routes
        routes = [[] for v in range(self.m)]
        for v in range(self.m):
            for t in range(1, self.n + 2):
                for i in range(self.n+1):
                    if self.sol.sample[f'x.{i}.{v}.{t}'] == 1:
                        routes[v].append(i)

        # Plot edges
        edgelist = []
        for route in routes:
            edgelist.append((0, route[0]))
            for node_num in range(1, len(route)):
                edgelist.append((route[node_num-1], route[node_num]))
        G.add_edges_from(edgelist)
        nx.draw_networkx_edges(G, pos=pos, edgelist=edgelist, width=2, edge_color=rgb2hex(cmap(i)))

        # Show plot
        plt.grid(True)
        plt.show()

