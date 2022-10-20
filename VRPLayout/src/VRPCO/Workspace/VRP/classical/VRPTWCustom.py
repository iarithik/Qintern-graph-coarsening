from VRPCustom import PureVRPCustom

"""
Solving a custom (designed by Adam and Ozlem) formulation of VRPTW using CP-SAT solver.
"""

MAX_EARLIEST_TIME = 5       # max. "earliest arrival time" (lower bound for time window)
MAX_TIME_WINDOW_RANGE = 30  # the largest possible time window size


class VRPTWCustom(PureVRPCustom):
    """Full Qubo Solver for Vehicle Routing Problem with Time Windows - classical implementation"""

    def __init__(self, n, m, cost, xc, yc, tw):
        super.__init__(n, m, cost, xc, yc)

        self.tw = tw         # list of time windows (for each client/city)
        self.A_max = 30      # TODO wyliczyć na podstawie tw
        self.W_max = 30      # TODO wyliczyć na podstawie tw

        self.formulate()

    def formulate(self):
        """Formulate the problem"""
        pass
