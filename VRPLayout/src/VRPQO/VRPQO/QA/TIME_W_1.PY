from dimod import ConstrainedQuadraticModel, Binary, Integer, SampleSet
from dwave.system import LeapHybridCQMSampler

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import time

class FQSTW():
    '''Vehicle routing problem with time-window constraints (node-based formulation)'''
    def __init__(self, n, m, cost, xc, yc, tw):
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
        self.m = m
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
            x.{i}.{v}.{t} = 1 if node i is visited by vehicle v at timestep t
            i is from the set of nodes {0, ..., n}
            v is from the set of vehicles {0, ..., m-1}
            t is from the set of timesteps {0, ..., n+1}
        '''
        x = [[[Binary(f'x.{i}.{v}.{t}') for t in range(self.n+2)] for v in range(self.m)] for i in range(self.n+1)]

        self.model.set_objective(
            sum(self.cost[i][j] * x[i][v][t] * x[j][v][t] for j in range(self.n+1) for i in range(self.n+1) for t in range(self.n) for v in range(self.m))
            #+ sum(self.cost[0][i] * x[i][v][1] for i in range(1,self.n+1) for v in range(self.m))
            #+ sum(self.cost[i][0] * x[i][v][self.n] for i in range(1,self.n+1) for v in range(self.m))
        )

        # --------------- CONSTRAINTS ---------------

        # NOTE: Asish used this since he had extra time steps in his version. 
        """
        # 1. At any given time instant exactly one vehicle visits exactly one client.
        for t in range(1, self.n+1):
            self.model.add_constraint(
                sum(x[i][v][t] for i in range(1, self.n+1) for v in range(self.m)) == 1
            )
        """

        # Each vehicle starts at the depot
        for v in range(self.m):
            self.model.add_constraint(
                x[0][v][0] == 0
            )

        # Each vehicle visits one client at a time
        for v in range(self.m):
            for t in range(self.n+2):
                self.model.add_constraint(
                    sum(x[i][v][t] for i in range(self.n+1)) == 1
                )
        
        # 2. Each client is visited by exactly one vehicle throughout all the time steps.
        for i in range(1, self.n+1):
            self.model.add_constraint(
                sum(x[i][v][t] for t in range(1, self.n+1) for v in range(self.m)) == 1
            )
        
        # 3. Every vehicle returns to the depot at some time step after the initial starting step 
        for v in range(self.m):
            self.model.add_constraint(
                sum(x[0][v][t] for t in range(1,self.n+2)) >= 1
            )
        
        # 4. Each vehicle visits at least one client.
        for v in range(self.m):
            self.model.add_constraint(
                sum(x[i][v][t] for i in range(1,self.n+1) for t in range(1, self.n+1)) >= 1
            )
        
        # 5. If a vehicle has visited a client at the time step t, then it must visit another client or the depot in the next time step.
        for i in range(1, self.n+1):
            for v in range(self.m):
                for t in range(1, self.n+1):
                    self.model.add_constraint(
                        x[i][v][t] * (1 - sum(x[j][v][t+1] for j in range(self.n+1) if j != i)) == 0
                    )
        
        # 6. If a vehicle has visited the depot at the time step t_0, then the journey for that vehicle is over.
        for v in range(self.m):
            for t_0 in range(1, self.n+2):
                self.model.add_constraint(
                    x[0][v][t_0] * ( sum(x[i][v][t] for i in range(1, self.n+1) for t in range(t_0 + 1, self.n+2)) ) == 0
                )
        
        # --------------- TIME WINDOW CONSTRAINTS ---------------
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

