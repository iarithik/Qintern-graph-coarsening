import numpy as np
import pandas as pd
import xml.etree.ElementTree as ETree


def generate_vrp_instance(n, seed=None):

    """Generate a random VRP instance.
    Args:
        n: No. of nodes exclusing depot.
        seed: Seed value for random number generator. Defaults to None, which sets a random seed.
    Returns:
        A list of (n + 1) x coordinates, a list of (n + 1) y coordinates and an (n + 1) x (n + 1) numpy array as the
        cost matrix.
    """

    # Set seed
    if seed is not None:
        np.random.seed(seed)

    # Generate VRP instance
    xc = (np.random.rand(n + 1) - 0.5) * 10
    yc = (np.random.rand(n + 1) - 0.5) * 10
    instance = np.zeros((n + 1, n + 1))
    for ii in range(n + 1):
        for jj in range(ii + 1, n + 1):
            instance[ii, jj] = (xc[ii] - xc[jj]) ** 2 + (yc[ii] - yc[jj]) ** 2
            instance[jj, ii] = instance[ii, jj]

    # Return output
    return instance, xc, yc

# Time Window VRP Constants
# TODO: Adjust these based on experiments or real-world situations, or paramterize these based on problem size
MAX_EARLIEST_TIME = 5 # The maximum possible "earliest arrival time" (i.e, lower bound for time window)
MAX_TIME_WINDOW_RANGE = 100 # The largest possible time window size

def generate_time_window_instance(n, seed=None):

    """Generate a random VRP instance with time windows
    Args:
        n: No. of nodes exclusing depot.
        seed: Seed value for random number generator. Defaults to None, which sets a random seed.
    Returns:
        A list of (n + 1) x coordinates, 
        a list of (n + 1) y coordinates, 
        an (n + 1) x (n + 1) numpy array as the cost matrix, 
        a list of n time windows that the vehicle must arrive within for each node, not including the depot
    """

    if seed is not None:
        np.random.seed(seed)

    # Acquire VRP instance
    instance, xc, yc = generate_vrp_instance(n)

    # Add time windows
    # NOTE: Currently, it is possible for a time window to have an earliest arrival time of 0
    # NOTE: Currently, the depot does not have time windows. 
    # TODO: Add the option to add a time window that bounds the times for vehicles to return to the depot
    time_windows = [[None, None]] # Add none values to replace depot time window
    for node in range(n):
        earliest_time = round(np.random.rand() * MAX_EARLIEST_TIME)
        latest_time = round(np.random.rand() * MAX_TIME_WINDOW_RANGE + earliest_time)
        time_windows.append([earliest_time, latest_time])

    return instance, xc, yc, time_windows


def generate_cvrp_instance(n, m, seed=None):

    """Generate a random CVRP instance.
    Args:
        n: No. of nodes exclusing depot.
        m: No. of vehicles in the problem.
        seed: Seed value for random number generator. Defaults to None, which sets a random seed.
    Returns:
        A list of (n + 1) x coordinates, a list of (n + 1) y coordinates, an (n + 1) x (n + 1) numpy array as the
        cost matrix, a list of m capacities for the vehicles and a list of n demads for the nodes.
    """

    # Set seed
    if seed is not None:
        np.random.seed(seed)

    # Acquire vrp instance
    instance, xc, yc = generate_vrp_instance(n)

    # Generate capacity and demand
    demands = np.random.rand(n) * 10
    capacities = np.random.rand(m)
    capacities = 4 * capacities * sum(demands) / sum(capacities)

    # Floor data
    demands = np.floor(demands).astype(int)
    capacities = np.floor(capacities).astype(int)

    # Return output
    return instance, xc, yc, capacities, demands


def parse_xml(problem_class='MD', n=11, k=1):

    """Parse VRP xml file and return instance.
    Args:
        problem_class: Class of problem (LD/MD/SD/VLD).
        n: Number of nodes.
        k: Number of vehicles.
    Returns:
        A list of (n + 1) x coordinates, a list of (n + 1) y coordinates and an (n + 1) x (n + 1) numpy array as the
        cost matrix.
    """

    # Extract coordinates
    filename = f'datasets/{problem_class}{n}_{k}.xml'
    tree = ETree.parse(filename)
    root = tree.getroot()
    nodes = [x for x in root.findall('./network/nodes/node') if x.attrib['type'] == '1']
    xc = [0.0] + [float(x.find('cx').text) for x in nodes]
    yc = [0.0] + [float(x.find('cy').text) for x in nodes]

    # Build instance
    instance = np.zeros((n, n))
    for ii in range(n):
        for jj in range(ii + 1, n):
            instance[ii, jj] = (xc[ii] - xc[jj]) ** 2 + (yc[ii] - yc[jj]) ** 2
            instance[jj, ii] = instance[ii, jj]

    # Return output
    return instance, xc, yc


def parse_csv(n=2, k=0):

    """Parse VRP csv file and return instance.
    Args:
        n: Number of nodes.
        k: instance number.
    Returns:
        A list of x coordinates, a list of y coordinates and an n x n numpy array as the
        cost matrix.
    """

    # Load dataset
    nrows = 3*n
    skiprows = sum(range(70, (30*n - 19), 30)) + (3*n + 1)*k + 1
    data = pd.read_csv('datasets/dataset.csv', nrows=nrows, skiprows=skiprows, header=None)

    # Extract relevant data
    xc = data[:n][2].to_numpy()
    yc = data[n:2*n][2].to_numpy()
    instance = data[2*n:3*n][range(2, 2 + n)].to_numpy()

    # Return output
    return instance, xc, yc
