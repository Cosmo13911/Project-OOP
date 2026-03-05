from datetime import datetime
from enum import Enum
from resources import Caddy, GolfCart

class BookingStatus(Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED_PAID = "CONFIRMED_PAID"   
    CANCELLED = "CANCELLED"

class Booking:
    def __init__(self, booking_id, requester, slot):
        self.__booking_id = booking_id
        self.__requester = requester
        self.__slot = slot
        self.__orders = []
        self.__created_at = datetime.now()
        self.__golfers = [requester]
        self.__status = BookingStatus.PENDING_PAYMENT
        self.__caddy_assignments = {}
        self.__carts = []

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
    
    @property
    def status(self): 
        return self.__status
    
    @property
    def caddy_assignments(self): 
        return self.__caddy_assignments
    
    @property
    def carts(self): 
        return self.__carts
    
    def add_order(self, order):
        self.__orders.append(order)

    # add เป็น list
    # def add_golfers(self, golfers_list):
    #         for g in golfers_list:
    #             if g not in self.__golfers:
    #                 self.__golfers.append(g)
    
    # add ทีละคน
    def add_golfer(self, golfer):
        if golfer not in self.__golfers:
            self.__golfers.append(golfer)
            return True
        return False
                    
    def set_status(self, status: BookingStatus):
        self.__status = status
        
    def assign_caddy(self, user_id, caddy: Caddy):
        self.__caddy_assignments[user_id] = caddy

    def assign_cart(self, cart: GolfCart):
        self.__carts.append(cart)
        
    def clear_addons(self):
        for caddy in self.__caddy_assignments.values():
            caddy.remove_from_schedule(self)
        for cart in self.__carts:
            cart.remove_from_schedule(self)
        self.__caddy_assignments.clear()
        self.__carts.clear()