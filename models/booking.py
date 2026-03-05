from datetime import datetime
from enum import Enum

class BookingStatus(Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED_PAID = "CONFIRMED_PAID"   

class Booking:
    def __init__(self, booking_id, requester, slot):
        self.__booking_id = booking_id
        self.__requester = requester
        self.__slot = slot
        self.__order = None
        self.__created_at = datetime.now()
        self.__golfers = [requester]
        self.__status = BookingStatus.PENDING_PAYMENT
    def update_status(self, new_status):
        self.__status = new_status
    @property
    def status(self):
        return self.__status
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
        return self.__order
    
    def add_order(self, order):
        self.__order = order

    def add_golfers(self, golfers_list):
            for g in golfers_list:
                if g not in self.__golfers:
                    self.__golfers.append(g)