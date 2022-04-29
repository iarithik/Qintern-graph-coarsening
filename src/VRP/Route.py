from .utils import *
from .ClassicalSolvers import ClassicalOptimizer

from .Coarsening import loukas_coarsen

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

    def routine(self, coarsened_route, coarsening_ration=0.2, solver="cplex_solution"):
        route = []
        cost = []

        coarsening = coarsened_route.coarsen(coarsening_ration=coarsening_ration)
        mapping  = coarsened_route._context['mapping']
        child_graph = coarsened_route._context['graph']

        coarsened_route, metrices = coarsening

        # Optimize the route path
        x, _ = coarsened_route.solve('cplex_solution')
        coarsened_routes = coarsened_route.load_routes(x)

        # Edge Lists        
        parent_edl = edge_list2dict(self._context['graph'].get_edge_list())
        child_edl  = edge_list2dict(child_graph.get_edge_list())

        # x, cost = self.solve(solver)
        # self.load_routes(x) # Initializing self.routes
        for vehicle in range(self.vehicles):
            inflated_route = self.inflate_route(mapping, child_edl, coarsened_routes, vehicle)
            normalized_route = self.normalize(inflated_route, parent_edl)
            route_cost = self.cost(normalized_route, parent_edl)

            route += [normalized_route]
            cost += [route_cost]
        return route, cost
    
    def compare_with(self, coarsened_route, mapping):
        pass

    def optimize_route(self, route):
        pass

    # Coarsens the graph and return a Route object based on the coarsened graph
    def coarsen(self, coarsening_ration=0.2, method='nearest') -> object:
        _graph = self.pygsp_graph()
        parent_edl = edge_list2dict(_graph.get_edge_list())

        # Coarsen the graph
        C, Gc, Call, Gall, g_iC, g_coarsening_list = coarsen(_graph, K=self.vehicles, r=coarsening_ration, method=method, max_levels=1) 
        metrics = coarsening_quality(_graph, C, kmax=kmax)

        assert len(Gall) > 1 # Check if coarsening was successful
        mapping  = g_iC[0]
        coarsened_adjacency = Gall[1].W.toarray()
        coarsened_adjacency_distance_norm = get_coarsen_distance_norm(coarsened_adjacency, mapping, parent_edl)
        coarsened_graph = graphs.Graph(coarsened_adjacency_distance_norm)

        _child_route = Route(Gall[1], self.depot, self.vehicles)

        self._context['coarsened_graph'] = self._context.get('coarsened_graph', {})
        self._context['coarsened_graph'][str(id(_child_route))] = _child_route
        
        return metrics, _child_route, mapping
        # raise NotImplementedError()
    
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
    def inflate_route(self, mapping, child_edl, coarsened_routes, vehicle = 0):
        route = coarsened_routes[vehicle]

        # Child to Parent Mapping
        c, r = np.where((mapping.todense() > 0) )
        coarsen_map = { i: [] for i in range(mapping.shape[0]) }

        for (_c, _r) in zip(c, r):
            coarsen_map[_c] += [_r]

        # Replace single element arrays with the element itself
        for key, value in coarsen_map.items():
            if len(value) == 1:
                coarsen_map[key] = int(value[0]) # int as it denotes the node id

        # Expansion
        for i in range(len(route)):
            (_from, _to) = route[i]
            if _from != 0:
                _from = coarsen_map[_from]
            if _to != 0:
                _to = coarsen_map[_to]
            route[i] = (_from, _to)
        return route

    # Normalize an inflated graph
    def normalize(self, inflated_route, parent_edl):
        partial_normalized_route = []
        normalized_route = []

        # Reduce [2, 2] to 2
        for (_from, _to) in inflated_route:
            if type(_from) not in [int, str]:
                _x, _y = _from
                if _x == _y:
                    _from = _x
            if type(_to) not in [int, str]:
                _x, _y = _to
                if _x == _y:
                    _to = _x
            partial_normalized_route += [(_from, _to)]

        # Reduce [ (2, array([14,  8])), (array([14,  8]), 3) ]
        # to     [ (2, 14), (14, 8), (8, 3) ]
        # or     [ (2, 8), (8, 14), (14, 3) ]

        need_reverse = False # For optimization purpose
        for i in range(len(partial_normalized_route)):

            (_from, _to) = partial_normalized_route[i]

            if type(_from) in [list, tuple, np.ndarray]:
                if need_reverse == True:
                    need_reverse = False
                    _from = (_from[1], _from[0])
                if tuple(list(_from)) in normalized_route:
                    _from = _from[1]
                else:
                    normalized_route += [tuple(list(_from))]
                    _from  = _from[1]
            if type(_to) in [list, tuple, np.ndarray]:
                _i = 1
                look_ahead_from = partial_normalized_route[i+_i][1]
                while type(look_ahead_from) in [list, tuple, np.ndarray]:
                    look_ahead_from = partial_normalized_route[i+_i][1]
                    _i += 1
                if  (
                        get_distance(_from, _to[0], parent_edl) +
                        get_distance(_to[0], _to[1], parent_edl) +
                        get_distance(_to[1], look_ahead_from, parent_edl) 
                    ) > (
                        get_distance(_from, _to[1], parent_edl) +
                        get_distance(_to[1], _to[0], parent_edl) +
                        get_distance(_to[1], look_ahead_from, parent_edl)
                    ):
                    need_reverse = True
                    _to = (_to[1], _to[0])
                normalized_route += [(_from, _to[0]), tuple(list(_to))]
            else:
                normalized_route += [(_from, _to)]

        return normalized_route

    def cost(self, route, edl=None):
        if not edl:
            _graph = self.pygsp_graph()
            edl = edge_list2dict(_graph.get_edge_list())

        cost = 0
        for (_from, _to) in route:
            cost += edl.get((_from, _to), edl.get((_to, _from)) )
        return cost