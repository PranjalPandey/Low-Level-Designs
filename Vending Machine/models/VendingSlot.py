from _collections import deque


class VendingSlot:

    def __init__(self, slot_id, slot_price):
        self.slot_id = slot_id
        self.product_list = deque()
        self.slot_price = slot_price


    def addProductToSlot(self, product):
        self.product_list.append(product)

