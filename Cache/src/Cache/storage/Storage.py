from abc import ABC, abstractmethod


class Storage(ABC):

    @abstractmethod
    def add(self,key, value):
        pass

    @abstractmethod
    def remove(self, key):
        pass

    @abstractmethod
    def get(self, key):
        pass


