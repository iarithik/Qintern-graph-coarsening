from abc import ABC, abstractmethod
import numpy as np


class VRPBase(ABC):

    def __init__(
        self,
        n: int,
        m: int,
        dist: np.array,
        xc: np.array,
        yc: np.array,
    ):
        self.n = n  # number of cities
        self.m = m  # number of vehicles
        self.dist = dist  # distance matrix (distances between cities)
        self.xc = xc  # matrix of x coordinates for each city
        self.yc = yc  # matrix of y coordinates for each city

    def prepare_data(self):
        data = {}
        data["distance_matrix"] = self.dist.tolist()
        data["num_vehicles"] = self.m
        data["depot"] = 0

        return data

    @abstractmethod
    def convert_solution(self, manager, routing, solution):
        pass

    @abstractmethod
    def solve(self):
        pass
