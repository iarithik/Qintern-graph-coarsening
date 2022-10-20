from abc import ABC, abstractmethod
import numpy as np


class BaseInitializer(ABC):
    def __init__(self, n, a, b):
        self.n = n
        self.a = a
        self.b = b

    @abstractmethod
    def _get_cities_coordinates(self):
        pass

    @abstractmethod
    def _get_distance_matrix(self, x, y):
        pass

    @abstractmethod
    def _get_time_windows(self):
        pass

    @abstractmethod
    def _get_travel_times(self, distance_matrix):
        pass

    def generate_nodes_weight_matrix_time_windows(self):
        np.random.seed(100 * self.a + self.b)

        x, y = self._get_cities_coordinates()
        distance_matrix = self._get_distance_matrix(x, y)
        time_windows = self._get_time_windows()
        travel_times = self._get_travel_times(distance_matrix)

        return x, y, distance_matrix, travel_times, time_windows


class SimpleInitializer(BaseInitializer):
    def __init__(self, n, a, b):
        super().__init__(n, a, b)
        self.MIN_TIME_WINDOW = 5    # lower bound for time window
        self.MAX_TIME_WINDOW = 30   # upper bound for time window
        self.MIN_SERVICE_TIME = 1   # lower bound for service time
        self.MAX_SERVICE_TIME = 20  # upper bound for service time

    def _get_cities_coordinates(self):
        x = (np.random.rand(self.n) - 0.5) * 20
        y = (np.random.rand(self.n) - 0.5) * 20
        return x, y

    def _get_distance_matrix(self, x, y):
        distance_matrix = np.zeros([self.n, self.n])
        for i in range(self.n):
            for j in range(i + 1, self.n):
                distance_matrix[i, j] = np.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2)
                distance_matrix[j, i] = distance_matrix[i, j]
        return distance_matrix

    def _get_time_windows(self):
        time_windows = []
        for _ in range(self.n):
            earliest_time = round(np.random.rand() * self.MIN_TIME_WINDOW)
            latest_time = round(np.random.rand() * self.MAX_TIME_WINDOW + earliest_time)
            time_windows.append([earliest_time, latest_time])
        time_windows[0][0] = 0
        # TODO check whether the following line will be necessary in the case
        # of implementation in accordance with the Adam and Ozlem draft
        # time_windows = np.insert(time_windows, 0, [0, 0], axis=0)  # depot time window
        return np.array(time_windows)

    def _get_travel_times(self, distance_matrix):
        travel_times = np.random.randint(
            self.MIN_SERVICE_TIME, self.MAX_SERVICE_TIME, size=(self.n, self.n)
        )
        np.fill_diagonal(travel_times, 0)
        travel_times = ((travel_times + travel_times.T) / 2).astype(int)
        return travel_times

