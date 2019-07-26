class StockxOrder(object):
    def __init__(self, order_type, order_json):
        self.product_uuid = order_json['skuUuid']
        self.order_type = order_type
        self.order_price = order_json['amount']
        self.order_time = order_json['createdAt']
        self.order_date = order_json['createdAt'][:10]
        self.shoe_size = order_json['shoeSize']
        self.num_orders = order_json['frequency']

    def __repr__(self):
        return('Stockx Order with price={}'.format(self.order_price))

    def __str__(self):
        return(
            'UUID: {}\nOrder Type: {}\nOrder Price: {}\nOrder Time: {}\nOrder Date: {}\nShoe Size: {}\nNumber of Orders: {}'.format(
            self.product_uuid, 
            self.order_type, 
            self.order_price, 
            self.order_time, 
            self.order_date, 
            self.shoe_size, 
            self.num_orders))

    def __lt__(self, other):
        return self.order_price < other.order_price

    def __gt__(self, other):
        return self.order_price > other.order_price

    def __le__(self, other):
        return self.order_price <= other.order_price

    def __ge__(self, other):
        return self.order_price >= other.order_price

    def __eq__(self, other):
        return self.order_price == other.order_price

    def __ne__(self, other):
        return self.order_price != other.order_price