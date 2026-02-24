from datetime import datetime, timedelta
from models.users import Member, Tier
from models.course import Course, TeeTimeSlot, SlotStatus , Course1Reserve
from models.booking import Booking, BookingStatus
from models.order import Order, OrderItem, Product
from models.tournament import Tournament, TournamentStatus
from models.payment import Payment, PaymentType, PaymentStatus

class GreenValleySystem:
    def __init__(self):
        self.__users = []
        self.__courses = []
        self.__bookings = []
        self.__products = []
        self.__tournaments = [] # เพิ่มอันนี้
        self.__payments = []    # เพิ่มอันนี้

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

    @property
    def products(self):
        return self.__products

    # ----- เพิ่มโค้ดส่วนนี้ -----
    @property
    def tournaments(self):
        return self.__tournaments
    # -------------------------

    def add_member(self, name, phone, tier_type, handicap=0.0):
        new_id = f"M-{len(self.__users) + 1:03d}"
        new_member = Member(new_id, name, phone, tier_type, handicap)
        self.__users.append(new_member)
        return new_member

    def find_user_by_id(self, member_id):
        # วนลูปหาผู้ใช้ในระบบที่ ID ตรงกับที่กรอกเข้ามา
        for user in self.__users:
            if user.user_id == member_id:
                return user
        return None # ถ้าวนจนจบแล้วไม่เจอ คืนค่า None (ไม่มีตัวตน)

    def create_data(self):
        print("--- [System] Initializing Modular Data ---")
        # สร้างสนาม
        c1 = Course("Green Valley Championship", 3500)
        
# ==========================================
        # 🌟 ระบบสร้าง Slot อัตโนมัติ (Auto-Generate Slots)
        # ==========================================
        # 1. กำหนดเวลาเริ่ม และ เวลาจบ ของสนาม (เช่น 06:00 ถึง 18:00)
        start_time = datetime.strptime("2024-12-01 06:00", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime("2024-12-01 18:00", "%Y-%m-%d %H:%M")
        
        current_time = start_time
        
        # 2. ให้วนลูปสร้างไปเรื่อยๆ จนกว่าจะถึงเวลาปิดสนาม
        while current_time <= end_time:
            # แปลงเวลา datetime กลับเป็น String สวยๆ (เช่น "2024-12-01 06:15")
            time_str = current_time.strftime("%Y-%m-%d %H:%M")
            
            # สร้างสล็อตและยัดเข้าสนาม
            c1.slots.append(TeeTimeSlot(time_str, c1))
            c1.slots.append(Course1Reserve(time_str, c1))
            
            # 3. บวกเวลาเพิ่มทีละ 15 นาที สำหรับสล็อตถัดไป
            current_time += timedelta(minutes=15) 
            
        print(f"✅ Generated {len(c1.slots)} slots for {c1.name}")


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

        self.add_member("Arthit Chaiyasit", "089-111-2222", Tier.PLATINUM, 9.5)
        self.add_member("Somsak Prasert", "086-333-4444", Tier.GOLD, 14.0)

        self.add_member("Kanya Wong", "083-555-6666", Tier.PLATINUM, 11.0)
        self.add_member("Napat Siri", "082-777-8888", Tier.GOLD, 20.5)

        self.add_member("Phuwadon Meechai", "081-999-0000", Tier.PLATINUM, 13.0)
        self.add_member("Chanita Boonmee", "084-222-1111", Tier.SILVER, 25.0)


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
        
    # ==========================================
    # Tournament Flow (Phase 0, 1, 2)
    # ==========================================
    
    def create_tournament(self, name, date, fee):
        # Phase 0: Create Tournament
        t_id = f"T-{len(self.__tournaments) + 1:03d}"
        new_tour = Tournament(t_id, name, date, fee)
        self.__tournaments.append(new_tour)
        return t_id

    def find_tournament_by_id(self, tour_id):
        for t in self.__tournaments:
            if t.tournamentID == tour_id:
                return t
        return None

    def register_tournament_get_payment(self, member_id, tour_id):
        tour = self.find_tournament_by_id(tour_id)
        member = self.find_user_by_id(member_id)
        
        # ❌ ป้องกันที่ 1: ตรวจสอบว่ามีงานแข่งนี้ และ "มีผู้ใช้คนนี้ในระบบจริงๆ"
        if not tour:
            return {"error": "Tournament not found in the system."}
        if not member:
            return {"error": f"Invalid Member ID: '{member_id}' does not exist!"} # เตะกลับทันทีถ้า ID มั่ว
        # ❌ ป้องกันที่ 1: เช็คว่าคนนี้จ่ายเงินและอยู่ในรายชื่อแข่งไปแล้วหรือยัง
        if member in tour.registeredPlayers:
            return {"error": f"Member {member.name} is already registered for this tournament!"}
            
        # ❌ ป้องกันที่ 2: เช็คว่าเคยกดสมัครแล้วบิลยังค้างจ่ายอยู่ไหม (กันกดเบิ้ลเอาบิลใหม่)
        for p in self.__payments:
            if p.member == member and p.tournamentID == tour_id and p.status == PaymentStatus.PENDING:
                return {"error": f"You already have a pending payment ({p.paymentID}) for this tournament."}
        
        # ถ้าผ่านด่านเช็คด้านบนมาได้ ค่อยออกบิลให้ใหม่ครับ
        p_id = f"PAY-{len(self.__payments) + 1:03d}"
        new_payment = Payment(p_id, tour.entryFee, PaymentType.TOURNAMENT_FEE, member, tour_id)
        self.__payments.append(new_payment)
        
        return {"paymentID": p_id, "amount": tour.entryFee, "message": "Here is your Invoice/Payment QR"}


    def process_payment(self, payment_id):
        # Phase 1: validate & addPlayer
        payment = next((p for p in self.__payments if p.paymentID == payment_id), None)
        if not payment: 
            return {"error": "Payment not found"}

        if payment.validate() == PaymentStatus.SUCCESS:
            tour = self.find_tournament_by_id(payment.tournamentID)
            tour.addPlayer(payment.member)
            return {"status": "SUCCESS", "message": "Registration & Payment Confirmed"}
        
        return {"status": "FAILED"}

    def get_tournament_players(self, tour_id):
        # ค้นหา Tournament จาก ID
        tour = self.find_tournament_by_id(tour_id)
        if not tour:
            return {"error": "Tournament not found in the system."}
            
        # ดึงข้อมูลผู้เล่นที่อยู่ในลิสต์ registeredPlayers
        player_list = []
        for player in tour.registeredPlayers:
            player_list.append({
                "member_id": player.user_id,
                "name": player.name,
                "tier": player.tier.value if hasattr(player, 'tier') else "N/A",
                "handicap": player.current_handicap
            })
            
        # ส่งข้อมูลสรุปกลับไป
        return {
            "tournament_id": tour.tournamentID,
            "tournament_name": tour.name,
            "status": tour.status.value,
            "total_registered": len(tour.registeredPlayers),
            "players": player_list
        }

    def close_registration_and_pairing(self, tour_id):
        # Phase 2: Closing & Mass Booking
        tour = self.find_tournament_by_id(tour_id)
        if not tour: return "Tournament not found"

        tour.updateStatus(TournamentStatus.CLOSED)
        pairings = tour.generatePairing()
        
        if len(self.__courses) == 0:
            return "Error: No courses available"
        course = self.__courses[0] 
        
        # Loop Every 4 Players
        for group in pairings:
            # หาสล็อตที่ว่างถัดไป
            available_slot = next((s for s in course.slots if s.status == SlotStatus.AVAILABLE), None)
            
            if available_slot:
                b_id = f"BK-{len(self.__bookings) + 1:03d}"
                new_booking = Booking(b_id, group[0], available_slot) # คนแรกเป็น Requester
                new_booking.status = BookingStatus.CONFIRMED_PAID
                new_booking.add_golfers(group[1:]) # ยัดคนที่เหลือเข้าก๊วน
                
                available_slot.status = SlotStatus.RESERVED
                self.__bookings.append(new_booking)
                tour.matchBookings.append(new_booking)

                # แจ้งเตือน Notification ตามที่เขียนใน Sequence Diagram
                details = f"Tee Time Assigned: {available_slot.play_date} for Tournament: {tour.name}"
                for member in group:
                    self.create_notification(member, details)

        tour.updateStatus(TournamentStatus.DRAW_PUBLISHED)
        return f"Draw Published. {len(pairings)} groups assigned."
    
    
