from .utils import *
from VRPCO.ClassicalSolvers import ClassicalOptimizer

class Route(object):
    def __init__(self, graph, depot=0, vehicles=2):

        # Keeping the raw data as well
        self._context = {
            'graph': graph
        }

        self.graph = graph.W.toarray()  # Adjacency Matrix
        self.n = self.graph.shape[0]    # Number of nodes
        self.depot = depot              # ID of the depot (default 0)
        self.cursor = depot             # Current location of the cursor vehicle
        self.vehicles = vehicles        # Number of vehicle
        
        self.coords = getattr(graph, 'coords', [])  # Coordinates of the nodes

        self.routes = None              # Calculated Routes

    def __call__(self, ):
        pass
    
    def solve(self, solver='cplex_solution'):
        classical_optimizer = ClassicalOptimizer(self.graph, self.n, self.vehicles)
        x, classical_cost, _ = getattr(classical_optimizer, solver)()
        return x, classical_cost

    def routine(self, reduction=0.2, method='nearest'):
        pass
    
    def compare_with(self, coarsened_route, mapping):
        pass

    def optimize_route(self, route):
        pass

    # Coarsens the graph and return a Route object based on the coarsened graph
    def coarsen(self, coarsening_ration=0.2, method='nearest') -> object:
        raise NotImplementedError()
    
    # Returns the source graph PyGSP object
    def pygsp_graph(self, ):
        return self._context['graph']

    # After solving the Linear Program, it is needed to extract the routes from the solution
    def load_routes(self, x, verbose=0):
        self.routes = []

        _chain = []
        _k = self.n*self.n
        travel_metrices = x[0:_k].reshape((self.n, self.n))

        for ix in range(0, self.n):
            for iy in range(0, self.n):
                if travel_metrices[ix][iy] > 0:
                    if (ix, iy) not in _chain and ix != iy:
                        _chain += [(ix, iy)]
        
        for vehicle in range(self.vehicles):
            cur = self.depot
            route = []
            travel = True
            if verbose: print(f"{cur}", end='  ')
            while travel:
                element = [(_from, _to) for (_from, _to) in _chain if _from == cur]
                (_from, _to) = element[vehicle] if len(element) > 1 else element[0]
                cur = _to
                route += [(_from, _to)]
                if verbose: print(f"->  {_to}", end='  ')
                if cur == self.depot:
                    travel = False
            self.routes += [route]
            if verbose: print()

        # Check if all vehicles are accounted for, while calcultaing the routes
        assert len(self.routes) == self.vehicles

        return self.routes
    
    # Inflate a coarsened graph with respect to parent graph
    def inflate_route(self, coarsen_map, child_edl, vehicle = 0):
        pass

    # Normalize an inflated graph
    def normalize(self, inflated_route, parent_edl):
        pass

    def cost(self, route):
        _graph = self.pygsp_graph()
        edl = edge_list2dict(_graph.get_edge_list())

        cost = 0
        for (_from, _to) in route:
            cost += edl.get((_from, _to), edl.get((_to, _from)) )
        return cost