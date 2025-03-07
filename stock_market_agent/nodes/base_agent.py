from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def process(self, state):
        pass