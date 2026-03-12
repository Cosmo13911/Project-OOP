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

    def calculate_total_price(self, rain_check_amount=None):
        """
        Method หลักในการคำนวณราคาสุทธิของทั้งการจอง
        """

        price_per_person = self.__slot.course.get_price_by_time(self.__slot.time)
    
        total_course_fee = 0.0
        details_msg = []

        # 2. วนลูปคำนวณราคาของนักกอล์ฟแต่ละคนตาม Tier ของเขา 
        for golfer in self.golfers:
            # คำนวณส่วนลดรายบุคคล (Polymorphism) 
            individual_discount = golfer.calculate_discount(price_per_person)
            net_person_price = price_per_person - individual_discount
            total_course_fee += net_person_price
            
            # เก็บรายละเอียดไว้แสดงใน Transaction 
            details_msg.append(f"{golfer.name} ({getattr(golfer, 'tier', 'GUEST')}): {net_person_price:,.2f} THB")
            
        # 3. รวมราคา Add-ons (Caddy, Cart, Orders)
        addons_price = sum(addon.price for addon in self.get_all_addons)
        
        # 4. ยอดสุทธิรวมที่ผู้จองต้องจ่าย
        total = total_course_fee + addons_price
        
        # หักลบ Rain Check (ถ้ามี)
        rc = float(rain_check_amount) if rain_check_amount is not None else 0.0
        total -= rc

        msg = {
                "base_price_per_person": round(price_per_person, 2),
                "individual_breakdown": details_msg,
                "total_course_fee": round(total_course_fee, 2),
                "addons_price": round(addons_price, 2),
                "rain_check_coupon": round(rc, 2),
                "total_net_to_pay": round(total, 2), # ผู้จองจ่ายยอดนี้ยอดเดียว
                "currency": "THB"
            }
    
        return round(total, 2), msg