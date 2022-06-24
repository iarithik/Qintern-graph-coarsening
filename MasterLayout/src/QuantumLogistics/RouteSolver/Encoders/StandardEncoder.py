from abc import ABC, abstractclassmethod


class Encoder(ABC):

    def __init__(self):

        return


    def encode(self,route):
        # to remember the route characteristics
        self.route = route

        # Must be output to a standard problem format
        raise NotImplementedError


    def extract(self,solution):
        # convert to route solution format
        raise NotImplementedError


    def addCapacityConstraints(self):

        raise NotImplementedError


    def addTWConstraints(self):

        raise NotImplementedError
