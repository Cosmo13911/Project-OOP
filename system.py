from datetime import datetime, timedelta
from models.users import Member, Tier
from models.course import Course, TeeTimeSlot, SlotStatus
from models.booking import Booking
from models.order import Order, OrderItem, Product

class GreenValleySystem:
    def __init__(self):
        self.__users = []
        self.__courses = []
        self.__bookings = []
        self.__products = []

    @property
    def users(self):
        return self.__users
    # แก้ หาวิธีเก็บ obj product ในระบบ
    @property
    def bookings(self):
        return self.__bookings
    
    @property
    def courses(self):
        return self.__courses
    
    @property
    def products(self):
        return self.__products

    def add_member(self, name, phone, tier_type, handicap=0.0):
        new_id = f"M-{len(self.__users) + 1:03d}"
        new_member = Member(new_id, name, phone, tier_type, handicap)
        self.__users.append(new_member)
        return new_member

    def create_data(self):
        print("--- [System] Initializing Modular Data ---")
        # สร้างสนาม
        c1 = Course("Green Valley Championship", 3500)

        # สร้างสินค้าในร้านอาหาร (Menu)
        menu_items = [
            Product("P001", "Fried Rice with Shrimp", 120),
            Product("P002", "Iced Americano", 65),
            Product("P003", "Club Sandwich", 150),
            Product("P004", "Singha Beer (Can)", 90),
            Product("P005", "Mineral Water", 20)
        ]

        for menu in menu_items:
            self.__products.append(menu)
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        c1.slots.append(TeeTimeSlot(f"{tomorrow} 08:00", c1))
        c1.slots.append(TeeTimeSlot(f"{tomorrow} 09:00", c1))
        self.__courses.append(c1)
        
        # สร้างสมาชิก
        self.add_member("John Doe", "081-222-3333", Tier.PLATINUM, 12.5)
        self.add_member("Mary Jane", "085-444-5555", Tier.GOLD, 24.0)

        # 2. เรียกใช้เมธอดเดิมที่มีอยู่แล้ว
        # สั่งให้ John (0) จองสนามแรก (0) เวลาแรก (0)
        self.create_booking(0, 0, 0)

        print(f"System Ready: {len(self.__courses)} Course(s) and {len(self.__users)} Member(s) loaded.")
        
    def create_booking(self, member_index, course_index, slot_index):
        try:
            member = self.__users[member_index]
            slot = self.__courses[course_index].slots[slot_index]

            if slot.status == SlotStatus.AVAILABLE:
                b_id = f"BK-{len(self.__bookings) + 1:03d}"
                new_booking = Booking(b_id, member, slot)
                slot.status = SlotStatus.RESERVED
                self.__bookings.append(new_booking)
                print(f"Success: Booking {b_id} for {member.name}")
                return new_booking
            else:
                print("Error: Slot already reserved.")
                return None
        except IndexError:
            print("Error: Data index out of range.")
            return None
        
    def find_booking_by_id(self, booking_id):
        for b in self.__bookings:
            if b.booking_id == booking_id:
                return b
        return None
    
    def find_user_by_id(self, user_id):
        for u in self.__users:
            if u.user_id == user_id:
                return u
        return None
    
    # ------------------- order ----------------------- #
    def create_order(self, product, quantity):
        order = Order()
        item = self.create_item(product, quantity)
        order.add_item(item)
        return order

    def create_item(self, product, quantity):
        item = OrderItem(product, quantity)
        return item
    
    def place_order(self, booking_id, product, quantity):
        print(f"[System] Placing order for Booking ID: {booking_id} | Product: {product.name} | Price: {product.price} | Quantity: {quantity}")
        booking = self.find_booking_by_id(booking_id)

        if not booking:
            return "Error: You have to booking first."

        order = self.create_order(product, quantity)
        order.calculate_total()

        booking = self.find_booking_by_id(booking_id)
        booking.add_order(order)

        self.create_notification(booking.requester, f"Your order for {quantity} x {product.name} has been placed successfully.")
        return "Order placed successfully."
    
    def find_product_by_id(self, product_id):
        for p in self.__products:
            if p.id == product_id:
                return p
        return None
    
    # -------------- notification ------------------ #
    def create_notification(self, member, message):
        member.add_notification(message)    
        

