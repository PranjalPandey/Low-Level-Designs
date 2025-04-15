class Transaction:
    def __init__(self, payment_mode, amount):
        self.transaction_id = None
        self.payment_mode = payment_mode
        self. amount = amount
        self.isSuccess = False

    def makeTransaction(self):
        self.isSuccess = True
