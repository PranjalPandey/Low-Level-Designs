from Cache.src.Cache.Cache import Cache
from Cache.src.Cache.policies.LRUEvictionPolicy import LRUEvictionPolicy
from Cache.src.Cache.storage.HashMapBasedStorage import HashMapBasedStorage


class CacheFactory:
    def defaultCache(self,capacity):
        return Cache(LRUEvictionPolicy(),HashMapBasedStorage(capacity))