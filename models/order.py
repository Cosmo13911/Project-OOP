class Product :
    def __init__(self, id, name, price):
        self.__id = id
        self.__name = name
        self.__price = price

    @property
    def price(self):
        return self.__price
    
    @property
    def id(self):
        return self.__id
    
    @property
    def name(self):
        return self.__name  

class OrderItem :
    def __init__(self, product, qty):
        self.__product = product
        self.__quantity = qty

    @property
    def product(self):
        return self.__product
    
    def calculate(self):
        price = self.__product.price
        return price * self.__quantity
        
    def get_detail(self):
        pass

class Order:
    def __init__(self):
        self.__items = []
        self.__total_price = 0
    
    @property
    def total_price(self):
        return self.__total_price

    def add_item(self, item):
        self.__items.append(item)

    def calculate_total(self):
        items = self.__items
        for item in items:
            self.__total_price += item.calculate()
        

