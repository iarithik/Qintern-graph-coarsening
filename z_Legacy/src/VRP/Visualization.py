import matplotlib.pyplot as plt

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def visualize_route(graph, routes, colormap='hsv'):
    [xc, yc] = graph.coords.T
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

    vehicle_cmap = get_cmap(len(routes) + 1, name=colormap)
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
    return plt

def compare_graphs(graph_1, graph_2, labels = [], colormap='hsv'):

    plt.figure()
    graph_cmap = get_cmap( 5, name=colormap )

    # Plotting Graph 1
    [xc, yc] = graph_1.coords.T
    plt.scatter(xc, yc, s=200, color=graph_cmap(1), alpha=0.5, label=labels[0])
    i = 0
    for x, y in zip(xc, yc):
        plt.annotate(i, (x + 0.075, y), size=16, color="r")
        i += 1


    # Plotting Graph 2
    [xc, yc] = graph_2.coords.T
    plt.scatter(xc, yc, s=100, color=graph_cmap(3), alpha=0.5, label=labels[1])

    plt.legend()
    plt.show()
    return plt