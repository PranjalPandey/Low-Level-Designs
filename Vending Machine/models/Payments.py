from abc import ABCMeta,ABC


class Payment(ABCMeta=ABC):
    pass

class CashPayment(Payment):

    def __init__(self,amount, denomination: list):
        self.amount = amount
        self.denomination = denomination



class OnlinePayment(Payment):

    def __init__(self, amount, vendor):
        self.amount = amount
        self.vendor = vendor