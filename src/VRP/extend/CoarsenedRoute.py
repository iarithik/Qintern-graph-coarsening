from pygsp import graphs

from ..utils import *
from ..Route import Route
from ..Coarsening import coarsening_quality, Simple_Coarsening, Loukas_Coarsening

from typing import Union, Dict

class CoarsenedRoute(Route):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def routine(self, reduction=0.2, method='nearest'):
        pass
    
    def compare_with(self, coarsened_route, mapping):
        pass

    def optimize_route(self, route):
        pass

    # Coarsens the graph and return a Route object based on the coarsened graph
    def coarsen(self, coarsening_ration=0.2, kmax=4, method='variation_neighborhoods') -> Union[Route, Dict]:
        """_summary_

        Args:
            coarsening_ration (float, optional): The size of the graph we are interested in preserving. Defaults to 0.2.
            kmax (float, optional): The size of the subspace we are interested in preserving. Defaults to 0.2.
            method (str, optional): The method of coarsening. Defaults to 'nearest'.

        Returns:
            Route: The route object with the coarsened graph
            Dict: The metrics representing the coarsening quality
        """
        _graph = self.pygsp_graph()
        parent_edl = edge_list2dict(_graph.get_edge_list())

        # Coarsen the graph
        C, Gc, Call, Gall, g_iC, g_coarsening_list = Simple_Coarsening(_graph)(coarsening_ration)
        # C, Gc, Call, Gall, g_iC, g_coarsening_list = Loukas_Coarsening(_graph)(coarsening_ration)
        metrics = coarsening_quality(_graph, C, kmax=kmax)

        assert len(Gall) > 1 # Check if coarsening was successful

        mapping  = g_iC[0]

        coarsened_adjacency = Gall[1].W.toarray()
        coarsened_adjacency_distance_norm = get_coarsen_distance_norm(coarsened_adjacency, mapping, parent_edl)
        coarsened_adjacency_coordinates = reframe_coordinates(coarsened_adjacency, _graph, mapping)

        coarsened_graph = graphs.Graph(coarsened_adjacency_distance_norm)
        coarsened_graph.set_coordinates(coarsened_adjacency_coordinates)


        _child_route = Route(Gall[1], self.depot, self.vehicles)
        # Ensure that the pygsp sets coords properly
        _child_route.pygsp_graph().set_coordinates(coarsened_adjacency_coordinates)
        _child_route.coords = coarsened_adjacency_coordinates

        self._context['original.graph'] = self._context['graph']
        self._context['graph'] = coarsened_graph
        self._context['mapping'] = mapping
        self._context['coarsened.coordinates'] = coarsened_adjacency_coordinates
        
        return _child_route, metrics
    
    # Returns the mapping of the coarsening to the original graph
    def coarsen_mapping(self, ):
        return self._context('mapping', None)

    # Inflate a coarsened graph with respect to parent graph
    def inflate_route(self, coarsen_map, child_edl, vehicle = 0):
        pass

    # Normalize an inflated graph
    def normalize(self, inflated_route, parent_edl):
        pass