from Cache.src.Algorithms.DoublyLinkedListNode import DoublyLinkedListNode
from Cache.src.Algorithms.Exceptions.InvalidElementException import InvalidElementException


class DoublyLinkedList:

    def __init__(self):
        self.dummyHead = DoublyLinkedListNode()
        self.dummyTail = DoublyLinkedListNode()
        self.dummyHead.next = self.dummyTail
        self.dummyTail.prev = self.dummyHead

    def detachNode(self,node):

        if node is not None:
            node.prev.next = node.next
            node.next.prev = node.prev

    def addNodeAtLast(self, node):
        tailPrev = self.dummyTail.prev
        tailPrev.next = node
        node.next = self.dummyTail
        self.dummyTail.prev = node
        node.prev = tailPrev

    def addElementAtLast(self, element):
        if element is None:
            raise InvalidElementException()
        newNode = DoublyLinkedListNode(element)
        self.addNodeAtLast(newNode)
        return newNode

    def isItemPresent(self):
        return self.dummyHead.next != self.dummyTail

    def getFirstNode(self):
        item=None
        if not self.isItemPresent():
            raise NoSuchElementException()

        return self.dummyHead.next

    def getLastNode(self):
        item=None
        if not self.isItemPresent():
            raise NoSuchElementException()

        return self.dummyTail.prev





