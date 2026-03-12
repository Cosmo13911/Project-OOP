from datetime import datetime, timedelta
from models.enum import BookingStatus, CaddyLevel, CartType, TournamentStatus

class Product:
    def __init__(self, p_id, name, price, stock):
        self.__id = p_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def price(self): return self.__price
    @property
    def stock(self): return self.__stock
    
    def check_stock(self, qty):
        return self.__stock >= qty
    
    def reduce_stock(self, qty):
        if self.check_stock(qty):
            self.__stock -= qty

class OrderItem:
    def __init__(self, product, qty: int):
        self.__product = product
        self.__quantity = qty

    @property
    def total_price(self):
        return float(self.__product.price) * int(self.__quantity)

class Order:
    def __init__(self, order_id, buyer):
        self.__order_id = order_id
        self.__buyer = buyer
        self.__items = []

    @property
    def items(self): return self.__items
    @property
    def price(self):
        # มี Logic การคำนวณส่วนลด จึงคงไว้เป็น Method
        sub_total = sum(item.total_price for item in self.__items)
        discount = self.__buyer.calculate_discount(sub_total)
        return sub_total - discount

    def add_item(self, item): 
        self.__items.append(item)
    
class Caddy:
    def __init__(self, caddy_id, name, level: CaddyLevel, price):
        self.__id = caddy_id
        self.__name = name
        self.__level = level
        self.__price = price
        self.__my_schedule = [] 

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
        for b in self.__my_schedule:
            if b.status == BookingStatus.CANCELLED: continue
            existing_dt = datetime.strptime(f"{b.slot.play_date} {b.slot.time}", "%d-%m-%Y %H:%M")
            time_diff = abs((target_dt - existing_dt).total_seconds()) / 3600
            if time_diff < 5: 
                return False 
        return True

    def assign_to_schedule(self, booking):
        self.__my_schedule.append(booking)
        
    def remove_from_schedule(self, booking):
        if booking in self.__my_schedule:
            self.__my_schedule.remove(booking)

class GolfCart:
    def __init__(self, cart_id, cart_type: CartType, price):
        self.__id = cart_id
        self.__type = cart_type
        self.__price = price
        self.__my_schedule = [] 

    @property
    def id(self): return self.__id
    @property
    def type(self): return self.__type
    @property
    def price(self): return self.__price

    def is_available(self, target_date: str, target_time: str) -> bool:
        target_dt = datetime.strptime(f"{target_date} {target_time}", "%d-%m-%Y %H:%M")
        for b in self.__my_schedule:
            if b.status == BookingStatus.CANCELLED: continue
            existing_dt = datetime.strptime(f"{b.slot.play_date} {b.slot.time}", "%d-%m-%Y %H:%M")
            time_diff = abs((target_dt - existing_dt).total_seconds()) / 3600
            if time_diff < 5:
                return False 
        return True

    def assign_to_schedule(self, booking):
        self.__my_schedule.append(booking)

    def remove_from_schedule(self, booking):
        if booking in self.__my_schedule:
            self.__my_schedule.remove(booking)