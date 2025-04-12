from Cache.src.Cache.storage.Storage import Storage
from Cache.src.Cache.Exceptions.NotFoundException import NotFoundException
from collections import defaultdict

class HashMapBasedStorage(Storage):

    def __init__(self,capacity):
        self.storage = []
        self.capacity = capacity

    def add(self,key, value):
        if self.isStorageFull():
            raise NotFoundException(key+" doesn't exist in the cache.")
        self.storage[key]=value

    def remove(self, key):
        if not self.storage[key]:
            raise NotFoundException(key+"doesn't exixt in the cache")
        self.storage.remove(key)

    def get(self, key):
        if not self.storage[key]:
            raise NotFoundException(key+"doesn't exixt in the cache")
        return self.storage[key]

    def isStorageFull(self):
        return len(self.storage) == self.capacity

