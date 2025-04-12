from Cache.src.Algorithms.DoublyLinkedList import DoublyLinkedList
from Cache.src.Cache.policies.EvictionPolicy import EvictionPolicy


class LRUEvictionPolicy(EvictionPolicy):

    def __init__(self):
        self.dll = DoublyLinkedList()
        self.mapper = dict()

    def keyAccessed(self,key):
        if self.mapper[key]:
            self.dll.detachNode(self.mapper[key])
            self.dll.addNodeAtLast(self.mapper[key])
        else:
            newNode = self.dll.addElementAtLast(key)
            self.mapper[key] = newNode

    def evictKey(self):
        first = self.dll.getFirstNode()
        if first is None:
            return None
        self.dll.detachNode(first)
        return first.getElement()
