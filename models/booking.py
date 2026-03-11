from datetime import datetime
from models.enum import BookingStatus, TournamentStatus
from models.resources import Caddy, GolfCart


class Booking:
    def __init__(self, booking_id, requester, slot):
        self.__booking_id = booking_id
        self.__requester = requester
        self.__slot = slot
        self.__orders = []
        self.__created_at = datetime.now()
        self.__golfers = [requester]
        self.__status = BookingStatus.PENDING_PAYMENT
        self.__caddy = []
        self.__carts = []
        
    @property
    def requester(self): return self.__requester
    @property
    def booking_id(self): return self.__booking_id
    @property
    def slot(self): return self.__slot
    @property
    def golfers(self): 
        for golfer in self.__golfers:
            if golfer == []:
                self.__golfers.remove(golfer)
        return self.__golfers
    @property
    def status(self): return self.__status
    @property
    def caddy (self): return self.__caddy
    @property
    def carts(self): return self.__carts
    @property
    def get_all_addons(self): return self.__caddy + self.__carts + self.__orders
    @property
    def orders(self): return self.__orders

    def add_order(self, order): 
        self.__orders.append(order)

    def add_golfer(self, golfer):
        if golfer not in self.__golfers:
            self.__golfers.append(golfer)
            return True
        return False
                    
    def set_status(self, status: BookingStatus):
        self.__status = status
        
    def assign_caddy(self, caddy: Caddy):
        self.__caddy.append(caddy)

    def assign_cart(self, cart: GolfCart):
        self.__carts.append(cart)
        
    def clear_addons(self):
        for caddy in self.__caddy:
            caddy.remove_from_schedule(self)
        for cart in self.__carts:
            cart.remove_from_schedule(self)
        self.__caddy.clear()
        self.__carts.clear()

    def calculate_total_price(self, rain_check = None) -> float:
        """
        Method หลักในการคำนวณราคาสุทธิของทั้งการจอง
        """
        # 1. ราคาฐานจากสนาม (คำนวณตามช่วงเวลา)
        base_price = self.__slot.course.get_price_by_time(self.__slot.time)
        
        # 2. คำนวณส่วนลด (Polymorphism: Member หรือ Guest จะคืนค่าต่างกัน)
        # โดยที่ Booking ไม่ต้องรู้ logic ข้างในของ user เลย
        discount = self.__requester.calculate_discount(base_price)
        
        # 3. รวมราคา Add-ons (เช่น Caddy, Cart, Orders)
        # สมมติว่าแต่ละ Add-on object มี method .get_price()
        addons_price = sum(addon.price for addon in self.get_all_addons)
        
        # ยอดสุทธิ
        total = (base_price - discount) + addons_price

        rc_value = rain_check.amount if rain_check is not None else 0
        
        total -= rc_value
        
        msg = {
            "base_price": round(base_price, 2),
            "discount": round(discount, 2),
            "addons_price": round(addons_price, 2),
            "rain_check_coupon": round(rc_value, 2),
            "total_net": round(total, 2),
            "currency": "THB"
        }

        
        return round(total, 2), msg