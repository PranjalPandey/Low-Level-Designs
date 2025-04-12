class DoublyLinkedListNode:

    def __init__(self,element):
        self.element = element
        self.next = None
        self.prev = None

    @property
    def element(self):
        return self.element

    @element.setter
    def element(self,element):
        self.element = element


