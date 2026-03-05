from datetime import datetime, timedelta
from fastapi import HTTPException
from models.users import Golfer, Member, Guest, Tier
from models.course import Course, TeeTimeSlot, SlotStatus , Course1Reserve
from models.booking import Booking, BookingStatus
from models.order import Order, OrderItem, Product
from models.tournament import Tournament, TournamentStatus
from models.payment import Payment, PaymentType, PaymentStatus, Raincheck
from models.course import SlotStatus, CourseType
from models.resources import Caddy, CaddyLevel, GolfCart, CartType

class GreenValleySystem:
    def __init__(self):
        self.__users = []
        self.__courses = []
        self.__bookings = []
        self.__products = []
        self.__tournaments = [] # เพิ่มอันนี้
        self.__payments = []    # เพิ่มอันนี้
        self.__rain_checks = []
        self.__caddies = []
        self.__carts = []

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
    def rain_checks(self):
        return self.__rain_checks

    @property
    def caddies(self):
        return self.__caddies

    @property
    def carts(self):
        return self.__carts
    
    @property
    def payments(self):
        return self.__payments

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

    def add_caddy(self, name, level: CaddyLevel, fee):
        new_id = f"C-{len(self.__caddies) + 1:03d}"
        new_caddy = Caddy(new_id, name, level, fee)
        self.__caddies.append(new_caddy)
        return new_caddy

    def add_golfcart(self, cart_type: CartType, fee: float, quantity: int = 1):
        added_carts = []
        for _ in range(quantity):
            new_id = f"CRT-{len(self.__carts) + 1:03d}"
            new_cart = GolfCart(new_id, cart_type, fee)
            self.__carts.append(new_cart)
            added_carts.append(new_cart)
            
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

        # สร้างสมาชิกที่มี Strike
        m4 = self.add_member("Tim (Silver)", "083-111-5645", Tier.SILVER)
        m4.add_strike(3) 
        m5 = self.add_member("Jill (Platinum)", "083-121-777", Tier.PLATINUM)
        m5.add_strike(2)

        # สร้างสนาม + ราคา
        self.__courses.append(Course("Green Valley Championship", fee_morning=3500, fee_afternoon=3000, course_type=CourseType.CHAMPIONSHIP))
        self.__courses.append(Course("Green Valley Executive", fee_morning=2200, fee_afternoon=1800, course_type=CourseType.EXECUTIVE))
        
        # สร้างแคดดี้และรถกอล์ฟ
        self.add_caddy("พี่แนน (Pro)", CaddyLevel.PRO, 600)
        self.add_caddy("น้องฝ้าย (Regular)", CaddyLevel.REGULAR, 450)
        self.add_caddy("พี่นุ่น (Pro)", CaddyLevel.PRO, 600)
        self.add_caddy("น้องโบว์ (Regular)", CaddyLevel.REGULAR, 450)
        self.add_caddy("สมชาย (Trainee)", CaddyLevel.TRAINEE, 350)
        self.add_caddy("สมศรี (Trainee)", CaddyLevel.TRAINEE, 350)
        self.add_caddy("สมหญิง (Trainee)", CaddyLevel.TRAINEE, 350)
        
        self.add_golfcart(CartType.STANDARD, 700, quantity=5)
        self.add_golfcart(CartType.COUPLE, 1200, quantity=2)
        self.add_golfcart(CartType.VIP, 2000, quantity=3)
        
        # สร้าง raincheck
        self.__rain_checks.append(Raincheck("RC-500", 500.0, "081-222-3333"))

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
    
# ------------------- booking ----------------------- #
    def find_available_caddies(self, date: str, time: str):
        return [c for c in self.__caddies if c.is_available(date, time)]
    
    def find_available_carts(self, date: str, time: str):
        return [c for c in self.__carts if c.is_available(date, time)]
        
    def find_payment_by_id(self, paymentID):
        return next((p for p in self.__payments if p.paymentID == paymentID), None)

    def get_course_by_type(self, course_type):
        return next((c for c in self.__courses if c.type == course_type), None)

    def check_booking_lead_time(self, user, date_str: str):
        now = datetime.now().date()
        try:
            target_date = datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            raise HTTPException(400, "วันที่ไม่ถูกต้อง")

        # กรณี Guest (Walk-in)
        if isinstance(user, Guest):
            if target_date != now:
                raise HTTPException(400, "ลูกค้า Walk-in จองได้เฉพาะวันปัจจุบันเท่านั้น")
            return

        # กรณี Member ตาม Tier
        diff_days = (target_date - now).days
        tier_limits = {
            Tier.SILVER: 7,
            Tier.GOLD: 14,
            Tier.PLATINUM: 30
        }
        
        # ใช้ .tier เพราะเราทำ encapsulation ไว้ในไฟล์ users.py แล้ว
        limit = tier_limits.get(user.tier, 0)
        if diff_days > limit:
            raise HTTPException(400, f"Member ระดับ {user.tier.value} จองล่วงหน้าได้ไม่เกิน {limit} วัน")
        
    def check_5_hour_rule(self, identifier: str, new_date: str, new_time: str):
        new_dt = datetime.strptime(f"{new_date} {new_time}", "%d-%m-%Y %H:%M")
        
        for b in self.__bookings:
            # 📌 กรองเฉพาะคิวที่ไม่ได้ยกเลิก และ "จองในวันเดียวกัน" จะได้ทำงานเร็วขึ้น
            if b.status.value != "CANCELLED" and b.slot.play_date == new_date:
                existing_dt = datetime.strptime(f"{b.slot.play_date} {b.slot.time}", "%d-%m-%Y %H:%M")
                time_diff = abs((new_dt - existing_dt).total_seconds()) / 3600
                
                if time_diff < 5:
                    for g in b.golfers:
                        # 📌 เช็คคลุมทั้ง user_id (Member) และเบอร์โทร (Walk-in) ในบรรทัดเดียว!
                        if g.user_id == identifier or getattr(g, 'phone', '') == identifier:
                            return False # ปฏิเสธการจอง (เจอคิวซ้ำ)
        return True # ผ่าน
    
    def issue_raincheck_to_user(self, user_id, raincheck_obj):
        # 1. หาออบเจกต์ User จาก ID
        user = self.find_user_by_id(user_id)
        
        if user and isinstance(user, Golfer):
            # 2. เพิ่มเข้าถังกลางของ System (เพื่อการตรวจสอบ)
            self.__rain_checks.append(raincheck_obj)
            
            # 3. เพิ่มเข้าไปในรายการของ User คนนั้น (เพื่อให้เจ้าของเห็น)
            user.add_raincheck(raincheck_obj)
            return True
        return False
    
    # 📌 เช็ค Raincheck ด้วยโค้ด + เบอร์โทรศัพท์ของผู้ใช้งาน
    def validate_and_use_raincheck(self, code: str, owner_phone: str):
        if not code: return 0
        voucher = next((v for v in self.rain_checks 
                        if v.code == code and v.owner_phone == owner_phone and v.status == "VALID"), None)
        if voucher:
            voucher.mark_as_used()
            return voucher.amount
        return -1

    def process_booking_payment(self, payment_id: str):
        # 1. ค้นหาออบเจกต์ Payment จากลิสต์ในระบบ
        payment = next((p for p in self.__payments if p.paymentID == payment_id), None)
        if not payment:
            return {"error": "ไม่พบข้อมูลการชำระเงิน (Payment ID Not Found)"}
        # 2. ตรวจสอบว่า Payment นี้มีรหัสการจอง (booking_id) ผูกอยู่หรือไม่
        b_id = getattr(payment, 'booking_id', None)
        if not b_id:
            return {"error": "ข้อมูลการชำระเงินนี้ไม่ได้ผูกกับรายการจองสนาม"}
        # 3. ยืนยันการชำระเงิน (เปลี่ยนสถานะเป็น SUCCESS)
        if payment.validate() == PaymentStatus.SUCCESS:
            # 4. อัปเดตสถานะของ Booking เป็นจ่ายเงินแล้ว
            booking = self.find_booking_by_id(b_id)
            if booking:
                booking.set_status(BookingStatus.CONFIRMED_PAID)
                # 5. ส่งการแจ้งเตือน
                self.create_notification(booking.requester, f"ชำระเงินสำเร็จ! การจองหมายเลข {b_id} ยืนยันแล้ว")
                return {
                    "status": "SUCCESS", 
                    "message": f"จ่ายเงินสำเร็จสำหรับรายการ {b_id}",
                    "booking_id": b_id
                }
        
        return {"status": "FAILED", "message": "การยืนยันการชำระเงินล้มเหลว"}
    
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