from datetime import datetime

class Booking:
    def __init__(self, booking_id, requester, slot):
        self.__booking_id = booking_id
        self.__requester = requester
        self.__slot = slot
        self.__orders = []
        self.__created_at = datetime.now()
        self.__golfers = [requester]

    @property
    def requester(self):
        return self.__requester
    
    @property
    def booking_id(self):
        return self.__booking_id
    
    @property
    def slot(self):
        return self.__slot
    
    @property
    def golfers(self):
        return self.__golfers
    
    @property
    def view_orders(self):
        return self.__orders
    
    def add_order(self, order):
        self.__orders.append(order)