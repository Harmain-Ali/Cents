from abc import ABC, abstractmethod


class BaseScorer(ABC):

    def __init__(self, data):

        self.data = data

    @abstractmethod
    def calculate(self):

        pass