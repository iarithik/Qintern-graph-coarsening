import matplotlib.pyplot as plt


class Route(object):
    def __init__(self, LogisticsGraph, config):
        
        graph = LogisticsGraph.graph

        # Keeping the raw data as well
        self._context = {
            'graph': graph
        }

        self.graph = graph                          # Logistics
        self.n = LogisticsGraph.n                   # Number of nodes
        self.depot = config["depot"]                # ID of the depot (default 0)
        self.cursor = config["depot"]               # Current location of the cursor vehicle
        self.vehicles = config["vehicles"]          # Number of vehicle
        self.coords = getattr(graph, 'coords', [])  # Coordinates of the nodes
        self.routes = None              # Calculated Routes
        self.solution = None
        self.coarsen = False

        #Must ADD Capacities and Time Windows

    def __call__(self, ):
        pass
    
    
    def visualiseSolution(self, routeSolution, colormap = "hsv"):
        routes = routeSolution
        [xc, yc] = self.graph.coords.T
        plt.figure()
        plt.scatter(xc, yc, s=200)
        # for i in range(len(xc)):
        #     plt.annotate(i, (xc[i] + 0.15, yc[i]), size=16, color="r")

        i = 0
        for x, y in zip(xc, yc):
            plt.annotate(i, (x + 0.075, y), size=16, color="r")
            i += 1
        
        plt.plot(xc[0], yc[0], "r*", ms=20)

        plt.grid()

        vehicle_cmap = self.get_cmap(len(routes) + 1, name=colormap)
        print('colors : ', len(routes))
        for vehicle in range(len(routes)):
            tour = routes[vehicle]
            color = vehicle_cmap(vehicle)
            for hop in tour:
                _from, _to = hop

                plt.arrow(
                    xc[_from],
                    yc[_from],
                    xc[_to] - xc[_from],
                    yc[_to] - yc[_from],
                    length_includes_head=True,
                    head_width=0.02,
                    color = color
                )

        plt.show()
        return


    def evalutateKPIS(self, solution):
        cost = self.calculateCost(solution)
        return


    def get_cmap(self, n, name='hsv'):
        '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
        RGB color; the keyword argument name must be a standard mpl colormap name.'''
        return plt.cm.get_cmap(name, n)

    def pygsp_graph(self):
        """
            Returns the source graph PyGSP object
        """
        return self._context['graph']

    def graphEdges2Dict(self, graph):
        edge_list = graph.get_edge_list()
        n1, n2, w = edge_list
        assert len(n1) == len(n2) == len(w)
        return { (n1[i], n2[i]):w[i] for i in range(len(n1)) }

    def calculateCost(self, solution):
        """
            Needs to be checked fundamentally
        """
        _graph = self.pygsp_graph()
        edl = self.graphEdges2Dict(_graph)

        cost = 0
        for route in solution:
            for (_from, _to) in route:
                cost += edl.get((_from, _to), edl.get((_to, _from)) )

        return cost





    def coarsenGraph(self, coarsenParams, coarsenEngine):
        """
            Coarsens the graph using the coarseningEngine (way of specifying how to coarsen)
        """
        print("NOT IMPLEMENTED YET")
        raise NotImplementedError


    def inflateGraph(self, solution):
        """
            Inflates solution from solver to coarsen engine
        """
        raise NotImplementedError


    def recordMetaData(self):
        """
            Add important details to self.metaData for later analysis
        """
        raise NotImplementedError


    def setSolution(self):
         #Solution to be in form:
        #  [  [list vehicle1 nodes],
        #     [list vehicle2 nodes],
        #     [list vehicle3 nodes],]

        raise NotImplementedError




