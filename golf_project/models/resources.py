from enum import Enum
from datetime import datetime, timedelta
from resources import BookingStatus

class CartType(str, Enum):
    STANDARD = "STANDARD"
    COUPLE = "COUPLE"
    VIP = "VIP"

class CaddyLevel(str, Enum):
    TRAINEE = "TRAINEE"
    REGULAR = "REGULAR"
    PRO = "PRO"
    VIP = "VIP"
    
class Caddy:
    def __init__(self, caddy_id, name, level: CaddyLevel, price):
        self.__id = caddy_id
        self.__name = name
        self.__level = level
        self.__price = price
        self.__mySchedule = [] 

    @property
    def id(self): 
        return self.__id
    
    @property
    def name(self): 
        return self.__name
    
    @property
    def level(self): 
        return self.__level
    
    @property
    def price(self): 
        return self.__price

    def is_available(self, target_date: str, target_time: str) -> bool:
        target_dt = datetime.strptime(f"{target_date} {target_time}", "%d-%m-%Y %H:%M")
        for b in self.__mySchedule:
            if b.status == BookingStatus.CANCELLED: continue
            existing_dt = datetime.strptime(f"{b.slot.play_date} {b.slot.time}", "%d-%m-%Y %H:%M")
            time_diff = abs((target_dt - existing_dt).total_seconds()) / 3600
            if time_diff < 5: 
                return False 
        return True

    def assign_to_schedule(self, booking):
        self.__mySchedule.append(booking)
        
    def remove_from_schedule(self, booking):
        if booking in self.__mySchedule:
            self.__mySchedule.remove(booking)

class GolfCart:
    def __init__(self, cart_id, cart_type: CartType, price):
        self.__id = cart_id
        self.__type = cart_type
        self.__price = price
        self.__mySchedule = [] 

    @property
    def id(self): return self.__id
    @property
    def type(self): return self.__type
    @property
    def price(self): return self.__price

    def is_available(self, target_date: str, target_time: str) -> bool:
        target_dt = datetime.strptime(f"{target_date} {target_time}", "%d-%m-%Y %H:%M")
        for b in self.__mySchedule:
            if b.status == BookingStatus.CANCELLED: continue
            existing_dt = datetime.strptime(f"{b.slot.play_date} {b.slot.time}", "%d-%m-%Y %H:%M")
            time_diff = abs((target_dt - existing_dt).total_seconds()) / 3600
            if time_diff < 5:
                return False 
        return True

    def assign_to_schedule(self, booking):
        self.__mySchedule.append(booking)

    def remove_from_schedule(self, booking):
        if booking in self.__mySchedule:
            self.__mySchedule.remove(booking)