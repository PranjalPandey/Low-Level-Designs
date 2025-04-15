from threading import Lock
from .Services.VendingMachineService import *


class SingletonMeta(type):
    _isInstance = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._isInstance:
                cls._isInstance[cls] = cls
            return cls._isInstance[cls]


class VendingMachine(metaclass=SingletonMeta):

    def __init__(self, number_of_slots: int):
        self.number_of_slots = number_of_slots
        self.initiate()

    def initiate(self):
        service = VendingMachineService()
        print("Please enter the slot_id to buy the product")
        slot_id = service.takeInputFromUser()

        print("Enter the quantity you want to buy!")
        while True:
            quantity = service.takeInputFromUser()
            if not service.checkFeasibility(slot_id, quantity):
                print("Quantity requested is not available for requested slot. Please enter lower qty")
                continue
            else:
                break
        amount = service.calculateBill(slot_id, quantity)
        print(f"The total amount for selected items is: Rs {amount}.")





