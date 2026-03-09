from models.users import Member, Guest
from models.tournament import Tournament
from models.course import Course
from models.resources import Product, Order, OrderItem, CartType, Caddy, CaddyLevel
from models.booking import Booking
from models.enum import SlotStatus, BookingStatus, TournamentStatus, Tier, CourseType
from models.notification import Notification
class GreenValleySystem:
    MAX_GOLFERS_PER_GROUP = 4

    def __init__(self):
        self.__users = []
        self.__courses = []
        self.__products = []
        self.__bookings = []
        self.__tournaments = []

    @property
    def users(self): return self.__users
    @property
    def products(self): return self.__products
    @property
    def bookings(self): return self.__bookings
    @property
    def tournaments(self): return self.__tournaments
    @property
    def get_all_users(self): return self.__users
    @property
    def get_all_courses(self): return self.__courses
    @property
    def get_all_products(self): return self.__products


    def create_data(self):
        # 1. สร้างกลุ่มผู้ใช้ (Actors อย่างน้อย 2 กลุ่ม ตามข้อกำหนด [cite: 24])
        # ประกอบด้วย Jennie, Praw, Rewthai, Tonkla และคนอื่นๆ รวม 8 คน
        user_data = [
            ("M-001", "Jennie", "081-111-1111", Tier.PLATINUM),
            ("M-002", "Praw", "081-222-2222", Tier.PLATINUM),
            ("M-003", "Rewthai", "081-333-3333", Tier.PLATINUM),
            ("M-004", "Tonkla", "081-444-4444", Tier.PLATINUM),
            ("M-005", "Lisa", "081-555-5555", Tier.GOLD),
            ("M-006", "Jisoo", "081-666-6666", Tier.SILVER),
            ("M-007", "Rose", "081-777-7777", Tier.PLATINUM),
            ("M-008", "BamBam", "081-888-8888", Tier.GOLD)
        ]

        product_data = [
            ("P-001", "Papaya PokPok", 109, 20),
            ("P-002", "Golf Mineral Water", 29, 1000),
            ("P-003", "Fried Rice", 120, 100),
            ("P-004", "Iced Americano", 75, 100),
            ("P-005", "Thai Tea", 55, 100)
        ]
        
        for u_id, name, phone, tier in user_data:
            # ทุก attribute ใน Member ต้องเป็น private 
            self.__users.append(Member(u_id, name, phone, tier))

        # 2. สร้างสนามกอล์ฟ 2 สนาม (Entity Class ที่มี ID และจำกัดจำนวน [cite: 10, 11])
        # สนามที่ 1: Blue Canyon Championship (ยากพิเศษ)
        c1 = Course("C-001", "Blue Canyon Championship", 3500, 4500, CourseType.CHAMPIONSHIP, rating=99.9, slope_rating=148)
        # ข้อมูลหลุมแบบคละ Par (ให้ดูสมจริงขึ้น ไม่ใช่ Par 4 ทั้งหมด)
        # Front Nine (1-9)
        pars_front = [4, 3, 4, 5, 4, 3, 4, 4, 5] # รวม 36
        for i, p in enumerate(pars_front, 1): c1.add_hole(i, p)
        # Back Nine (10-18)
        pars_back = [4, 5, 3, 4, 4, 3, 4, 5, 4] # รวม 36 (Total 72)
        for i, p in enumerate(pars_back, 10): c1.add_hole(i, p)
        self.__courses.append(c1)

        # สนามที่ 2: Executive/Exclusive Course
        # สนามที่ 2: Laguna Exclusive
        c2 = Course("C-002", "Laguna Exclusive", 2500, 3200, CourseType.EXECUTIVE, rating=71.2, slope_rating=125)

        # ข้อมูลหลุม (สนาม Executive บางครั้งอาจจะมี Par 3 เยอะกว่าปกติ)
        pars_front = [2, 3, 4, 5, 4, 3, 4, 4, 5] # รวม 36
        for i, p in enumerate(pars_front, 1): c2.add_hole(i, p)
        # Back Nine (10-18)
        pars_back = [4, 5, 3, 3, 4, 3, 4, 5, 5] # รวม 36 (Total 72)
        for i, p in enumerate(pars_back, 10): c2.add_hole(i, p)
        self.__courses.append(c2)

        # สนามที่ 3: Green Valley Resort (ความยากธรรมดา)
        c3 = Course("C-003", "Ladkrabang Valley", 999, 1190, CourseType.EXECUTIVE, rating=50.7, slope_rating=113)

        # ข้อมูลหลุม (Standard Layout: Par 72)
        # Front Nine (1-9) - เน้นความง่าย พาร์ 4 เป็นหลัก
        pars_front_c3 = [2, 2, 3, 4, 3, 3, 2, 3, 1] # รวม 24
        for i, p in enumerate(pars_front_c3, 1): c3.add_hole(i, p)
        
        # Back Nine (10-18)
        pars_back_c3 = [2, 3, 3, 1, 2, 3, 3, 5, 5] # รวม 36 (Total 60)
        for i, p in enumerate(pars_back_c3, 10): c3.add_hole(i, p)
        
        self.__courses.append(c3)

        # 3. สร้างข้อมูลสินค้า/บริการ (เพื่อให้ครบองค์ประกอบค่าใช้จ่าย 4 รายการ )
        # สินค้าเหล่านี้ต้องมี ID และระบุจำนวนที่เหลือได้ 
        for p_id, name, price, stock in product_data:
            self.__products.append(Product(p_id, name, price, stock))

        # 4. จำลองการจอง (Transaction Class [cite: 8])
        # ต้องมีสถานะติดตาม (PENDING, CONFIRMED, CANCELLED) อย่างน้อย 3 สถานะ [cite: 12]

    def find_user(self, user_id: str):
        for user in self.__users:
            if user.id == user_id:
                return user
        raise ValueError(f"User with ID {user_id} not found")

    def find_course(self, course_id: str):
        for course in self.__courses:
            if course.id == course_id:
                return course
        raise ValueError(f"Course with ID {course_id} not found")

    def find_tournament(self, tour_id: str):
        for tour in self.__tournaments:
            if tour.id == tour_id:
                return tour
        raise ValueError(f"Tournament with ID {tour_id} not found")
    
    def find_booking(self, booking_id: str):
        for booking in self.__bookings:
            if booking.booking_id == booking_id:
                return booking
        raise ValueError(f"Booking with ID {booking_id} not found")

    def find_product(self, product_id: str):
        for product in self.__products:
            if product.id == product_id:
                return product
        raise ValueError(f"Product with ID {product_id} not found")

    def create_booking(self, requester_id: str, course_id: str, date: str, time: str, companion_ids: list = None):
        if companion_ids is None:
            companion_ids = []
            
        # 1. Validation: ตรวจสอบจำนวนคนในก๊วน (รวมคนจองต้องไม่เกิน 4)
        total_golfers = 1 + len(companion_ids)
        if total_golfers > self.MAX_GOLFERS_PER_GROUP:
            raise ValueError(f"1 Group can have at most {self.MAX_GOLFERS_PER_GROUP} golfers (including requester). You have {total_golfers}.")

        requester = self.find_user(requester_id)
        if not requester:
            raise ValueError(f"Requester with ID {requester_id} not found")
        course = self.find_course(course_id)
        if not course:
            raise ValueError(f"Course with ID {course_id} not found")
        # 2. ค้นหาสมาชิกคนอื่นๆ ในก๊วน
        companions = []
        for c_id in companion_ids:
            comp = self.find_user(c_id)
            if comp:
                if comp == requester:
                    raise ValueError("Requester cannot be a companion to themselves.")
                companions.append(comp)
            else: raise ValueError(f"Companion with ID {c_id} not found")

        # 3. ค้นหาและตรวจสอบ Slot
        slot = course.find_slot(date, time)
        if not slot or slot.status != SlotStatus.AVAILABLE:
            raise ValueError(f"Slot {time} on {date} is not available for course {course.name}")

        # 4. สร้างการจองและล็อก Slot ทันที (Locking Logic)
        b_id = f"BK-{len(self.__bookings) + 1:03d}"
        new_booking = Booking(b_id, requester, slot)
        
        # เพิ่มเพื่อนร่วมก๊วนเข้าไปใน Booking Object
        # (ตรวจสอบว่าในคลาส Booking มี Method add_golfers หรือยัง)
        new_booking.add_golfer(companions)

        # 5. เปลี่ยนสถานะ Slot เป็น RESERVED ทันทีเพื่อล็อกก๊วน
        # ตามเกณฑ์ข้อ 1.15 การเปลี่ยนสถานะถือเป็นการติดตามสถานะทรัพยากร
        slot.status = SlotStatus.RESERVED 

        # 6. แจ้งเตือนทุกคนในก๊วน (Notification - ข้อ 1.20)
        all_players = [requester] + companions
        for player in all_players:
            player.add_notification(Notification(f"Booking id: {b_id}, Course {course.name}, Slot time : {slot.time}"))

        self.__bookings.append(new_booking)
        return new_booking

    # ---------------- Ordering ----------------
    def place_order(self, booking_id: str, product_id: str, quantity: int):
    
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        booking = self.find_booking(booking_id)
        if not booking:
            raise KeyError(f"Booking ID {booking_id} not found")

        product = self.find_product(product_id)
        if not product:
            raise KeyError(f"Product ID {product_id} not found")

        if not product.check_stock(quantity):
            raise ValueError(f"Not enough stock. Remaining: {product.stock}")
        
        product.reduce_stock(quantity) 

        order_id = f"ORD-{len(booking.orders)+1:03d}"
        new_order = Order(order_id, booking.requester)
        new_order.add_item(OrderItem(product, quantity))
        
        booking.add_order(new_order)
        net_total = new_order.calculate_net_total

        if isinstance(booking.requester, Member):
            booking.requester.add_notification(Notification(f"Order placed: {quantity}x {product.name}. Total: {net_total} THB)"))

        return f"Order placed successfully. Total: {net_total} THB"

    # ---------------- Tournament ----------------
    def create_tournament(self, name: str, date: str, fee: float, course_id: str):
        course = self.find_course(course_id)
        if not course:
            raise ValueError(f"Course with ID {course_id} not found")
                    
        t_id = f"T-{len(self.__tournaments) + 1:03d}"
        new_tour = Tournament(t_id, name, date, fee, course)
        self.__tournaments.append(new_tour)
        return {"tournamentID": t_id, "course_assigned": course.name}

    def register_tournament_get_payment(self, member_id: str, tour_id: str):
        tour = self.find_tournament(tour_id)
        if not tour: raise ValueError(f"Tournament with ID {tour_id} not found")

        member = self.find_user(member_id)
        if not member: raise ValueError(f"Member with ID {member_id} not found")
        
        if any(entry.player.user_id == member.user_id for entry in tour.registered_players):
            raise ValueError("Already registered.")

        p_id = f"PAY-{member_id}-{tour_id}"
        return {"paymentID": p_id, "amount": tour.entry_fee, "message": "Proceed to payment"}

    def process_payment(self, payment_id: str):
        # จำลองการจ่ายเงินผ่าน
        parts = payment_id.split("-")
        if len(parts) == 3:
            member_id = f"{parts[1]}-{parts[2]}" # M-001 -> PAY-M-001-T-001 -> len is 4. Let's fix.
            member_id = parts[1] + "-" + parts[2]
            tour_id = parts[3] + "-" + parts[4] if len(parts)==5 else parts[-2]+"-"+parts[-1]
            
        tour = self.find_tournament(tour_id)
        if not tour: raise ValueError("Tournament not found.")

        member = self.find_user(member_id)
        if not member: raise ValueError("Member not found.")

        if tour.add_player(member):
            return {"status": "SUCCESS", "message": "Confirmed"}


    def close_registration_and_pairing(self, tour_id):
        # Phase 2: Closing & Mass Booking
        tour = self.find_tournament_by_id(tour_id)
        if not tour: raise ValueError("Tournament not found.")

        tour.updateStatus(TournamentStatus.CLOSED)
        pairings = tour.generatePairing()
        
        # 🌟 1. ดึงสนามและวันที่ มาจากข้อมูลงานแข่งโดยตรง
        course = tour.course 
        target_date = tour.date # สมมติว่าเก็บค่าเป็น "2026-12-02"
        
        # 🌟 2. สั่งให้ระบบเตรียมสล็อตของ "วันนั้น" ให้พร้อม
        self.ensure_slots_for_date(course, target_date)
        
        # Loop Every 4 Players
        for group in pairings:
            # 🌟 3. หาสล็อตว่าง "เฉพาะของวันที่จัดแข่งเท่านั้น" (กันพลาดไปดึงของวันอื่น)
            for slot in course.slots:
                if slot.status == SlotStatus.AVAILABLE and slot.play_date.startswith(target_date):
                    available_slot = slot
                    return available_slot
            raise ValueError(f"No available slots on {target_date} for course {course.name}")
            
            b_id = f"BK-{len(self.__bookings) + 1:03d}"
            new_booking = Booking(b_id, group[0], available_slot) # คนแรกเป็น Requester
            new_booking.update_status(BookingStatus.CONFIRMED_PAID)
            new_booking.add_golfers(group[1:]) # ยัดคนที่เหลือเข้าก๊วน
            
            # เปลี่ยนสถานะเป็น RESERVED เพื่อไม่ให้ก๊วนอื่นมาแย่ง (ป้องกันคิวชน)
            available_slot.update_status(SlotStatus.RESERVED)
            self.__bookings.append(new_booking)
            tour.add_match_booking(new_booking)

            # แจ้งเตือน Notification ตอนนี้จะเป็นเวลาและวันที่ที่ถูกต้องแล้ว
            details = f"Tee Time Assigned: {available_slot.play_date} for Tournament: {tour.name}"
            
            for member in group:
                self.create_notification(member, details)

        tour.updateStatus(TournamentStatus.DRAW_PUBLISHED)
        return f"Draw Published. {len(pairings)} groups assigned."
    
    def record_tournament_score(self, tour_id: str, member_id: str, hole_number: int, stroke: int):
        tour = self.find_tournament(tour_id)
        if not tour: 
            raise ValueError("Tournament not found")
        if tour.status.value != "IN_PROGRESS": 
            raise ValueError("Tournament is not in progress")

        success = tour.record_score(member_id, hole_number, stroke)
        if not success: 
            raise ValueError("Failed to record score. Check member ID, hole number, or stroke value.")
        
        return {"message": f"Score recorded for {member_id}: Hole {hole_number} = {stroke}"}

    def get_tournament_leaderboard(self, tour_id: str):
        tour = self.find_tournament(tour_id)
        if not tour:
            raise ValueError("Tournament not found")
        
        return {
            "tournament_name": tour.name,
            "status": tour.status.value,
            "leaderboard": tour.get_leaderboard()
        }
    
    def end_tournament(self, tour_id):
        tour = self.find_tournament(tour_id)
        if not tour: 
            raise ValueError("Tournament not found")

        if tour.status != TournamentStatus.DRAW_PUBLISHED:
            raise ValueError(f"Error: ไม่สามารถจบการแข่งได้ในสถานะ {tour.status.value}")

        updated_players = []

        # 🌟 1. เปลี่ยนมาวนลูป List ของออบเจกต์ Scorecard โดยตรง
        for sc in tour.scorecards:
            # 🌟 2. ความงดงามของ OOP! เราดึง Member จาก Scorecard ได้เลย ไม่ต้อง find_user_by_id แล้ว
            member = sc.member 
            if not member:
                raise ValueError(f"Member not found for Scorecard with member ID {sc.member.user_id}")
                
            member.add_history(sc, round_type="TOURNAMENT") 
            updated_players.append(f"{member.name} (New HC:{member.current_handicap:.1f})")
                
        # อัปเดตสถานะทัวร์นาเมนต์เมื่อทุกอย่างเสร็จสิ้น
        tour.set_to_completed()

        return {
            "status": "Success",
            "message": f"ปิดการแข่งขัน {tour.name} เรียบร้อยแล้ว",
            "players_updated": updated_players
        }