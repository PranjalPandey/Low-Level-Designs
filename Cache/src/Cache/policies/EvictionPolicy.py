from abc import ABC, abstractmethod


class EvictionPolicy(ABC):

    @abstractmethod
    def keyAccessed(self,key):
        pass

    @abstractmethod
    def evictKey(self):
        pass