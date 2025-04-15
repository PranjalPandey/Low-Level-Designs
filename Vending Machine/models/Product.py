class Product:

    def __init__(self, mrp):
        self.product_id = None
        self.product_mrp = mrp
        self.discounted_price = mrp

    def set_discounted_price(self, discount):
        self.discounted_price = self.product_mrp-((discount*.01)*self.product_mrp)