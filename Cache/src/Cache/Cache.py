from Cache.src.Cache.Exceptions.NotFoundException import NotFoundException
from Cache.src.Cache.Exceptions.StorageFullException import StorageFullException


class Cache:
    def __init__(self, evictionPolicy, storage):
        self.evictionPolicy = evictionPolicy
        self.storage = storage

    def put(self,key, value):
        try:
            self.storage.add(key,value)
            self.evictionPolicy.keyAccessed(key)
        except StorageFullException:
            print("Got Storage full. Will try to evict.")
            keyToRemove = evictionPolicy.evictKey()
            if keyToRemove is None:
                raise RuntimeError("Unexpected State. Storage full and no key to evict.")
            self.storage.remove(keyToRemove)
            print("Creating space by evicting item ..." + keyToRemove)
            self.put(key, value)

    def get(self, key):
        try:
            value=self.storage.get(key)
            self.evictionPolicy.keyAccessed(key)
            return value
        except NotFoundException:
            print("Tried to access non-exixting key.")
            return None