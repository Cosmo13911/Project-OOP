from models.users import Member, Guest, Golfer
from models.tournament import Tournament
from models.course import Course
from models.resources import Product, Order, OrderItem, CartType, Caddy, CaddyLevel , GolfCart
from models.booking import Booking
from models.enum import SlotStatus, BookingStatus, TournamentStatus, Tier, CourseType, RainCheckStatus , UserStatus
from models.notification import Notification
import random 
from models.payment import Raincheck, RainCheckStatus
from datetime import timedelta , datetime
from models.payment import Payment, PaymentStatus


class GreenValleySystem:

    MAX_GOLFERS_PER_GROUP = 4

    def __init__(self):
        self.__users = []
        self.__courses = []
        self.__products = []
        self.__bookings = []
        self.__tournaments = []
        self.__caddies = []
        self.__carts = []
        self.__rain_checks = []
        self.__payments = []

    @property
    def users(self): return self.__users
    @property
    def products(self): return self.__products
    @property
    def bookings(self): return self.__bookings
    @property
    def tournaments(self): return self.__tournaments
    @property
    def get_all_courses(self): return self.__courses
    @property
    def caddies(self): return self.__caddies
    @property
    def carts(self): return self.__carts
    @property
    def rain_checks(self): return self.__rain_checks
    @property
    def payments(self): return self.__payments
    
# กำหนด Format ที่เป็นไปได้ทั้งหมด
    DATE_FORMATS = ["%d-%m-%Y", "%Y-%m-%d"] 
    DATETIME_FORMATS = ["%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M"]

    # สร้างฟังก์ชันกลางในการแปลงวันที่ (Robust Parsing)
    def robust_parse_datetime(self, dt_str):
        for fmt in self.DATETIME_FORMATS:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"ไม่รองรับรูปแบบเวลา: {dt_str} กรุณาใช้ DD-MM-YYYY HH:MM หรือ YYYY-MM-DD HH:MM")
    

    def create_data(self):
        # 1. สร้างกลุ่มผู้ใช้ (Actors อย่างน้อย 2 กลุ่ม ตามข้อกำหนด [cite: 24])
        # ประกอบด้วย Jennie, Praw, Rewthai, Tonkla และคนอื่นๆ รวม 8 คน
        member_data = [
            ("M-001", "Jennie", "081-111-1111", Tier.PLATINUM),
            ("M-002", "Praw", "081-222-2222", Tier.PLATINUM),
            ("M-003", "Rewthai", "081-333-3333", Tier.PLATINUM),
            ("M-004", "Tonkla", "081-444-4444", Tier.PLATINUM),
            ("M-005", "Lisa", "081-555-5555", Tier.GOLD),
            ("M-006", "Jisoo", "081-666-6666", Tier.SILVER),
            ("M-007", "Rose", "081-777-7777", Tier.PLATINUM),
            ("M-008", "BamBam", "081-888-8888", Tier.GOLD)
        ]

        guest_data = [
            ("G-001", "Somchai Guest", "089-999-9999"),
            ("G-002", "Somsak Guest", "089-888-8888"),
            ("G-003", "Somying Guest", "089-777-7777")
        ]

        product_data = [
            ("P-001", "Papaya PokPok", 109, 20),
            ("P-002", "Golf Mineral Water", 29, 1000),
            ("P-003", "Fried Rice", 120, 100),
            ("P-004", "Iced Americano", 75, 100),
            ("P-005", "Thai Tea", 55, 100)
        ]

        # ===============================================
        # walk in na ja
        caddy_data = [
            ("พี่แนน (Pro)", CaddyLevel.PRO, 1200),
            ("พี่นุ่น (Pro)", CaddyLevel.PRO, 1200),
            ("น้องฝ้าย (Pro)", CaddyLevel.PRO, 1200),
            ("น้องโบว์ (Pro)", CaddyLevel.PRO, 1200),
            ("สมชาย (Pro)", CaddyLevel.PRO, 1200),
            ("สมศรี (Pro)", CaddyLevel.PRO, 1200),
            ("สมหญิง (Pro)", CaddyLevel.PRO, 1200),
            ("พี่แมว (Pro)", CaddyLevel.PRO, 1200),
            ("พี่ฟ้า (Pro)", CaddyLevel.PRO, 1200),
            ("น้องอิ่ม (Pro)", CaddyLevel.PRO, 1200),
            ("น้องเก่ง (Regular)", CaddyLevel.REGULAR, 800),
            ("สมน้ำหน้า (Regular)", CaddyLevel.REGULAR, 800),
            ("สมบูรณื (Regular)", CaddyLevel.REGULAR, 800),
            ("สมมูล (Regular)", CaddyLevel.REGULAR, 800),
            ("พี่พราววี่ (Regular)", CaddyLevel.REGULAR, 800),
            ("พี่ต้นกล้ากี้ (Trainee)", CaddyLevel.TRAINEE, 499),
            ("พี่เจนนีนี่ (Trainee)", CaddyLevel.TRAINEE, 499),
            ("พี่ต้นหลิววี่ (Trainee)", CaddyLevel.TRAINEE, 499),
            ("น้องต้น (Trainee)", CaddyLevel.TRAINEE, 499),
            ("น้องเค้น (Trainee)", CaddyLevel.TRAINEE, 499),
            ("น้องดี (Trainee)", CaddyLevel.TRAINEE, 499),
            ("น้องไม่ดี (Trainee)", CaddyLevel.TRAINEE, 499),
        ]

        golf_cart_data = [
            (CartType.STANDARD, 790, 20), 
            (CartType.COUPLE, 1200, 10), 
            (CartType.VIP, 7777, 7)
        ]
        # สร้างสมาชิกที่มี Strike

        for u_id, name, phone, tier in member_data:
            # ทุก attribute ใน Member ต้องเป็น private 
            self.__users.append(Member(u_id, name, phone, tier))

        for g_id, name, phone in guest_data:
        # ใช้คลาส Guest ตามที่ import มาจาก models.users
            self.users.append(Guest(g_id, name, phone))

        for name, level, fee in caddy_data:
            self.add_caddy(name, level, fee)

        for cart_type, fee, quantity in golf_cart_data:
            self.add_golfcart(cart_type, fee, quantity)

        # self.__users.append(Guest("G-001", "Somchai Guest", "089-999-9999")) 

        # m4 = self.add_member("Tim (Silver)", "083-111-5645", Tier.SILVER)
        # m4.add_strike(3) 
        # m5 = self.add_member("Jill (Platinum)", "083-121-777", Tier.PLATINUM)
        # m5.add_strike(2)
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
        # 7. สุ่มบันทึกคะแนนให้ครบ 18 หลุม สำหรับทุกคน (Simulation)
        # ตามข้อกำหนดที่ต้องการให้สุ่มเพิ่มคะแนนไว้แล้วทั้ง 18 หลุม
        # 4. จำลองการจอง (Transaction Class [cite: 8])
        # ต้องมีสถานะติดตาม (PENDING, CONFIRMED, CANCELLED) อย่างน้อย 3 สถานะ [cite: 12]
        # ===============================================
        # 5. จำลองทัวร์นาเมนต์ (Tournament Simulation)
        # ===============================================
        
        # 5.1 สร้างรายการแข่ง "Green Valley Open 2026"
        tour_info = self.create_tournament(
            name="Green Valley Open 2026", 
            date="25-03-2026", 
            fee=1500.0, 
            course_id="C-001"
        )
        tour = self.find_tournament(tour_info["tournamentID"])
        self.close_registration_and_pairing(tour.id)
        
        # 5.2 ให้ Member ทุกคนสมัครเข้าแข่งขัน
        # (จำลองการสมัครและสร้าง Scorecard อัตโนมัติ)
        for member in self.users:
            if isinstance(member, Member):
                tour.add_player(member)
        
        # 5.3 เปลี่ยนสถานะเป็นกำลังแข่งขัน เพื่อให้บันทึกคะแนนได้
        tour.update_status(TournamentStatus.IN_PROGRESS)
        
        # 5.4 สุ่มบันทึกคะแนนให้ครบ 18 หลุม สำหรับทุกคน
        for member in self.users:
            if isinstance(member, Member):
                for hole_num in range(1, 19):
                    # สุ่มคะแนนระหว่าง 2 ถึง 6 strokes ต่อหลุม
                    random_stroke = random.randint(2, 20)
                    self.record_tournament_score(
                        tour_id=tour.id,
                        member_id=member.id,
                        hole_number=hole_num,
                        stroke=random_stroke
                    )

        # 5.5 สร้าง Tournament เพิ่มเติมรายการที่ 2: "Summer Classic 2026" (สถานะ: เปิดรับสมัคร)
        tour2_info = self.create_tournament(
            name="Summer Classic 2026", 
            date="15-04-2026", 
            fee=1200.0, 
            course_id="C-002"
        )
        # ให้ Member บางส่วนสมัคร (ยังไม่บันทึกคะแนน)
        tour2 = self.find_tournament(tour2_info["tournamentID"])

        for member in self.users:
            if isinstance(member, Member):
                tour2.add_player(member)
            
        self.close_registration_and_pairing(tour.id)
        tour2.update_status(TournamentStatus.IN_PROGRESS)

        for member in self.users:
            if isinstance(member, Member):
                for hole_num in range(1, 19):
                    # สุ่มคะแนนระหว่าง 2 ถึง 6 strokes ต่อหลุม
                    random_stroke = random.randint(2, 13)
                    self.record_tournament_score(
                        tour_id=tour2.id,
                        member_id=member.id,
                        hole_number=hole_num,
                        stroke=random_stroke
                    )
        
        # 5.3 เปลี่ยนสถานะเป็นกำลังแข่งขัน เพื่อให้บันทึกคะแนนได้

        # 5.6 สร้าง Tournament เพิ่มเติมรายการที่ 3: "Midnight Championship" (สถานะ: แข่งขันเสร็จสิ้น)
        tour3_info = self.create_tournament(
            name="Midnight Championship", 
            date="01-02-2026", 
            fee=2000.0, 
            course_id="C-003"
        )
        tour3 = self.find_tournament(tour3_info["tournamentID"])
        
        for member in self.users:
            if isinstance(member, Member):
                tour3.add_player(member)
            
        self.close_registration_and_pairing(tour.id)
        tour3.update_status(TournamentStatus.IN_PROGRESS)

        for member in self.users:
            if isinstance(member, Member):
                for hole_num in range(1, 19):
                    # สุ่มคะแนนระหว่าง 2 ถึง 6 strokes ต่อหลุม
                    random_stroke = random.randint(0, 7)
                    self.record_tournament_score(
                        tour_id=tour3.id,
                        member_id=member.id,
                        hole_number=hole_num,
                        stroke=random_stroke
                    )


    def add_member(self, name, phone, tier: Tier,handicap: float = 0.0):
        new_id = f"M-{len(self.__users) + 1:03d}"
        new_member = Member(new_id, name, phone, tier , handicap)
        self.__users.append(new_member)
        return new_member


    def add_caddy(self, name, level: CaddyLevel, fee):
        new_id = f"CDY-{len(self.__caddies) + 1:03d}"
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
        return added_carts # คืนค่ากลุ่มรายการรถที่ถูกเพิ่มเข้าไป
    

    def find_available_caddies(self, date: str, time: str):
        return [c for c in self.__caddies if c.is_available(date, time)]
    
    def find_available_carts(self, date: str, time: str):
        return [c for c in self.__carts if c.is_available(date, time)]

    def find_payment_by_id(self, paymentID):
        return next((p for p in self.__payments if p.payment_id == paymentID), None)
    
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

    def find_available_carts(self, date, time):
    # กรองเฉพาะรถกอล์ฟที่มีสถานะว่างใน Slot เวลานั้นๆ 
    # และต้องเป็นไปตามเงื่อนไข 'Entity Class มีจำนวนจำกัด' 
        available = [cart for cart in self.__carts if cart.is_available(date, time)]
        return available

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

    def find_booking_by_member(self, member_id: str):
        for booking in self.__bookings:
            if booking.requester.id == member_id:
                return booking
        raise ValueError(f"Booking with ID {member_id} not found")

    def find_product(self, product_id: str):
        for product in self.__products:
            if product.id == product_id:
                return product
        raise ValueError(f"Product with ID {product_id} not found")

    # ------------------- booking ----------------------- #
    def find_available_caddies(self, date: str, time: str):
        return [c for c in self.__caddies if c.is_available(date, time)]
    
    def find_available_carts(self, date: str, time: str):
        return [c for c in self.__carts if c.is_available(date, time)]
        
    def find_payment_by_id(self, paymentID):
        return next((p for p in self.__payments if p.payment_id == paymentID), None)

    def find_raincheck(self, rain_check_code: str):
        return next((rc for rc in self.__rain_checks if rc.code == rain_check_code), None)
    
    def get_course_by_type(self, course_type):
        return next((c for c in self.__courses if c.type == course_type), None)

    def check_booking_lead_time(self, user, date_str: str):
        now = datetime.now().date()
        target_date = self.parse_date(date_str)

        # กรณี Guest (Walk-in)
        if isinstance(user, Guest):
            if target_date != now:
                raise ValueError("Walk-in guests can only book for the same day")

        # กรณี Member ตาม Tier
        diff_days = (target_date - now).days

        # ใช้ .tier เพราะเราทำ encapsulation ไว้ในไฟล์ users.py แล้ว
        limit = user.tier.booking_day_limit.day_limit
        if diff_days > limit:
            raise ValueError(f"{user.name} ({user.tier.name}) can only book up to {limit} days in advance. You tried to book {diff_days} days ahead.")
        
    def check_5_hour_rule(self, identifier: str, new_date: str, new_time: str):
        
        target_dt = self.robust_parse_datetime(f"{new_date} {new_time}")
        std_new_date = target_dt.strftime("%d-%m-%Y")
        
        new_dt = self.parse_datetime(new_date, new_time)     
           
        for b in self.__bookings:
            # 📌 กรองเฉพาะคิวที่ไม่ได้ยกเลิก และ "จองในวันเดียวกัน" จะได้ทำงานเร็วขึ้น
            if b.status.value != "CANCELLED" and b.slot.play_date == std_new_date:
                existing_dt = self.robust_parse_datetime(f"{b.slot.play_date} {b.slot.time}")
                time_diff = abs((new_dt - existing_dt).total_seconds()) / 3600
                
                if time_diff < 5:
                    for g in b.golfers:
                        # 📌 เช็คคลุมทั้ง user_id (Member) และเบอร์โทร (Walk-in) ในบรรทัดเดียว!
                        if g.user_id == identifier or getattr(g, 'phone', '') == identifier:
                            return False # ปฏิเสธการจอง (เจอคิวซ้ำ)
        return True # ผ่าน
    
    def create_booking(self, requester_id: str, course_id: str, date: str, time: str, companion_ids: list = None):
        if companion_ids is None:
            companion_ids = []
            
        # 1. Normalization: แปลงวันที่ให้เป็นมาตรฐานเดียวกันก่อนทำงาน 
        dt_obj = self.robust_parse_datetime(f"{date} {time}")
        std_date = dt_obj.strftime("%d-%m-%Y")
        target_date = dt_obj.date()
        today = datetime.now().date()

        # 2. กฎ: ห้ามจองวันในอดีต [ข้อกำหนดใหม่]
        if target_date < today:
            raise ValueError(f"ไม่สามารถจองย้อนหลังได้ (วันที่ระบุ: {target_date}, วันนี้: {today})")

        # 3. ค้นหาข้อมูลผู้จองและสนาม 
        requester = self.find_user(requester_id)
        course = self.find_course(course_id)

        # 4. กฎการจองล่วงหน้าแยกตามประเภทผู้ใช้ 
        diff_days = (target_date - today).days

        if isinstance(requester, Guest):
            if target_date != today:
                raise ValueError("Guest (Walk-in) สามารถจองได้เฉพาะภายในวันนี้เท่านั้น")
        elif isinstance(requester, Member):
            # ตรวจสอบ limit ตาม Tier (สูงสุด 30 วันตามกฎใหม่)
            limit = requester.tier.booking_day_limit.day_limit 
            if diff_days > limit:
                raise ValueError(f"สมาชิก Tier {requester.tier.name} จองล่วงหน้าได้สูงสุด {limit} วัน (คุณพยายามจองล่วงหน้า {diff_days} วัน)")
        
        # 5. ตรวจสอบว่าวันนั้นมี Tournament หรือไม่ [ข้อกำหนดใหม่]
        for tour in self.__tournaments:
            if self.is_tournament_day(course_id, date):
                raise ValueError(f"สนามนี้มีการจัดทัวร์นาเมนต์ในวันที่ {date} ขออภัยในความไม่สะดวก")

        # 2. Validation: ตรวจสอบจำนวนคนในก๊วน (รวมคนจองต้องไม่เกิน 4) 
        total_golfers_count = 1 + len(companion_ids)
        if total_golfers_count > self.MAX_GOLFERS_PER_GROUP:
            raise ValueError(f"1 Group can have at most {self.MAX_GOLFERS_PER_GROUP} golfers. You have {total_golfers_count}.")

        requester = self.find_user(requester_id)
        course = self.find_course(course_id)

        # 3. ค้นหาสมาชิกคนอื่นๆ ในก๊วน
        companions = []
        for c_id in companion_ids:
            comp = self.find_user(c_id)
            if comp:
                if comp == requester:
                    raise ValueError("Requester cannot be a companion to themselves.")
                companions.append(comp)

        # 4. ตรวจสอบ Slot ด้วยวันที่มาตรฐาน
        slot = course.find_slot(std_date, time)
        if not slot or slot.status != SlotStatus.AVAILABLE:
            raise ValueError(f"Slot {time} on {std_date} is not available.")

        # 5. สร้างการจองและล็อก Slot
        b_id = f"BK-{len(self.__bookings) + 1:03d}"
        new_booking = Booking(b_id, requester, slot)
        
        # เพิ่มเพื่อนร่วมก๊วนเข้าไป (ตรวจสอบว่าส่ง list ของ object เข้าไป)
        for companion in companions:
            new_booking.add_golfer(companion)

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

        if booking.status == BookingStatus.CONFIRMED_PAID:
                raise ValueError("Cannot place order: This booking has already been paid.")

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
        net_total = new_order.price

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

    def process_payment(self, booking: Booking, tour: Tournament = None, member: Member = None, rain_check_code: str = None):
        # 1. แยกส่วนประกอบของรหัส Payment        
        try:
            if tour and member:
                payment = Payment(tour.entry_fee, member, tournament_id=tour.id)

            else:
                member = self.find_user(booking.requester.id)
                if not member:
                    raise ValueError(f"Member with ID {booking.requester.id} not found")
                
                if rain_check_code:
                    rain_check_amount = self.validate_and_use_raincheck(rain_check_code, member.phone)
                else:
                    rain_check_amount = None
            
                total_price , msg = booking.calculate_total_price(rain_check_amount)
                payment = Payment(total_price, member, booking_id=booking.booking_id, transaction=msg)
                booking.set_status(BookingStatus.CONFIRMED_PAID)

            payment.set_status(PaymentStatus.SUCCESS)
            self.__payments.append(payment)

            
            # [เพิ่ม] การแจ้งเตือนการชำระเงินเสร็จสิ้น
            msg = f"Payment Successful! [{payment.get_type}] is confirmed."
            member.add_notification(Notification(msg))     

            return {"status": "SUCCESS", "message": msg}
        except (IndexError, ValueError) as e:
            raise ValueError(f"Error processing booking payment: {str(e)}")

        
    def close_registration_and_pairing(self, tour_id):
        tour = self.find_tournament(tour_id)
        if not tour:
            raise ValueError("Tournament not found")
        tour.update_status(TournamentStatus.DRAW_PUBLISHED)
        
        pairings = tour.generate_pairing() # ได้ list ของ match_group
        course = tour.course 
        target_date = tour.date 
        course.generate_slots_for_date(target_date)
        
        for group_obj in pairings:
            current_players = group_obj.players
            
            # 1. ค้นหาสล็อตว่าง
            available_slot = None
            for slot in course.slots:
                if slot.status == SlotStatus.AVAILABLE and slot.play_date == target_date:
                    available_slot = slot
                    break
            
            if not available_slot:
                raise ValueError(f"No available slots on {target_date}")
            
            # 2. ผูกสล็อตเข้ากับกลุ่มการแข่ง
            group_obj.slot = available_slot
            
            # 3. สร้าง Booking และส่ง Notification
            b_id = f"BK-T-{len(self.bookings) + 1:03d}"
            new_booking = Booking(b_id, current_players[0], available_slot)
            new_booking.set_status(BookingStatus.CONFIRMED_PAID)
            
            for companion in current_players[1:]:
                new_booking.add_golfer(companion)
            
            # --- เพิ่มส่วนการแจ้งเตือนรอบเวลาแข่ง ---
            msg = f"Tournament {tour.name}: Your Tee-off is at {available_slot.time} on {target_date}."
            for p in current_players:
                p.add_notification(Notification(msg))
            
            available_slot.status = SlotStatus.RESERVED 
            self.bookings.append(new_booking)
            tour.match_bookings.append(new_booking)

        tour.update_status(TournamentStatus.IN_PROGRESS)
        return f"Draw Published. {len(pairings)} groups assigned with tee times."


    def record_tournament_score(self, tour_id: str, member_id: str, hole_number: int, stroke: int):
        tour = self.find_tournament(tour_id)
        if not tour: 
            raise ValueError("Tournament not found")
        
        # 🌟 เพิ่มบรรทัดนี้: ค้นหาออบเจกต์ Member จริงๆ จาก ID ก่อน
        member_obj = self.find_user(member_id)
        if not member_obj:
            raise ValueError(f"Member with ID {member_id} not found")

        if tour.status.value != "IN_PROGRESS": 
            raise ValueError("Tournament is not in progress")

        # 🌟 แก้ไข: ส่ง member_obj (Object) แทน member_id (String)
        success = tour.record_player_score(member_obj, hole_number, stroke)
        if not success: 
            raise ValueError("Failed to record score. Scorecard not found for this member.")
        
        return {"message": f"Score recorded for {member_obj.name}: Hole {hole_number} = {stroke}"}

    def get_tournament_leaderboard(self, tour_id: str):
        tour = self.find_tournament(tour_id)
        if not tour:
            raise ValueError("Tournament not found")
        
        return {
            "tournament_name": tour.name,
            "status": tour.status.value,
            "leaderboard": tour.get_leaderboard()
        }
    
    # เพิ่มใน system.py
    def register_tournament_pending(self, member_id: str, tour_id: str):
        
        tour = self.find_tournament(tour_id)
        member = self.find_user(member_id)
        
        user = self.find_user(member_id) # เปลี่ยนชื่อตัวแปรให้สื่อความหมายกว้างขึ้น
    
        # 1. ตรวจสอบว่าเป็น Guest หรือไม่ (Guest ห้ามสมัคร)
        if isinstance(user, Guest):
            raise ValueError(f"ข้อผิดพลาด: Guest ({user.name}) ไม่สามารถสมัครทัวร์นาเมนต์ได้ สิทธิ์นี้เฉพาะสมาชิกเท่านั้น")
        
        # 2. ตรวจสอบสถานะการโดนแบน (Member ที่สถานะไม่ใช่ ACTIVE ห้ามสมัคร)
        # อ้างอิงจากสถานะใน models/users.py และ models/enum.py
        if hasattr(user, 'status') and user.status != UserStatus.ACTIVE:
            raise ValueError(f"ข้อผิดพลาด: สมาชิก {user.name} ไม่สามารถสมัครได้เนื่องจากสถานะปัจจุบันคือ {user.status.value}")
                
        # Validation: เช็คว่าสมัครซ้ำไหม หรือทัวร์เต็ม/ปิดหรือยัง
        if any(m.id == member_id for m in tour.registered_players):
            raise ValueError("คุณได้สมัครทัวร์นาเมนต์นี้ไปแล้ว")
            
        # สร้างรายการชำระเงินแบบ PENDING
        payment = Payment(
            amount=tour.entry_fee, 
            member=member, 
            tournament_id=tour.id
        )
        payment.set_status(PaymentStatus.PENDING) # สำคัญ: ตั้งเป็นรอดำเนินการ
        self.__payments.append(payment)
        
        # เพิ่มชื่อเข้าทัวร์นาเมนต์ (ชื่อจะไปปรากฏในระบบแล้ว แต่สถานะการเงินยังไม่ Success)
        tour.add_player(member) 
        
        member.add_notification(Notification(f"สมัคร {tour.name} สำเร็จ! กรุณาชำระเงิน {tour.entry_fee} บาท เพื่อยืนยันสิทธิ์"))
        
        return payment.payment_id
    
    # เพิ่มใน system.py
    def confirm_tournament_payment(self, payment_id: str):
        # ค้นหารายการ Payment จาก ID
        payment = next((p for p in self.__payments if p.payment_id == payment_id), None)
        
        if not payment:
            raise ValueError("ไม่พบรายการชำระเงินนี้")
            
        # เปลี่ยนสถานะเป็นสำเร็จ
        payment.set_status(PaymentStatus.SUCCESS)
        
        # แจ้งเตือนผู้ใช้
        payment.member.add_notification(Notification(f"ชำระเงินค่าสมัครทัวร์นาเมนต์ {payment.tournament_id} เรียบร้อยแล้ว!"))
        
        return True 
    
    # เพิ่มลงในคลาส GreenValleySystem ในไฟล์ system.py
    def process_registration_payment(self, member_id: str, tour_id: str):
        """จัดการชำระเงินค่าสมัครทัวร์นาเมนต์และเพิ่มชื่อผู้เข้าแข่งขัน"""
        # 1. Find Tournament and Member objects
        tour = self.find_tournament(tour_id)
        member = self.find_user(member_id)

        # 2. Check if already registered
        if any(entry.id == member.id for entry in tour.registered_players):
            raise ValueError("Already registered for this tournament.")

        # 3. Check Tournament status
        if tour.status != TournamentStatus.REGISTRATION_OPEN:
            raise ValueError(f"Tournament registration is {tour.status.value}")

        # --- FIX: Pass arguments as keywords to bypass the 'booking' positional argument ---
        # This prevents the "'str' object has no attribute 'requester'" error
        self.process_payment(booking=None, tour=tour, member=member) 

        # 5. Add player to tournament
        tour.add_player(member)

        # 6. Notify the member
        msg = f"Payment Successful for {tour.name}. Amount: {tour.entry_fee} THB"
        member.add_notification(Notification(msg))

        return {
            "status": "SUCCESS",
            "message": msg
        }
    
    def end_tournament(self, tour_id):
        tour = self.find_tournament(tour_id)
        if not tour: 
            raise ValueError("Tournament not found")

        if tour.status != TournamentStatus.IN_PROGRESS:
            raise ValueError(f"Error: ไม่สามารถจบการแข่งได้ในสถานะ {tour.status.value}")

        updated_players = []

        rank = 0
        # 🌟 1. เปลี่ยนมาวนลูป List ของออบเจกต์ Scorecard โดยตรง
        for sc in tour.score_cards:
            # 🌟 2. ความงดงามของ OOP! เราดึง Member จาก Scorecard ได้เลย ไม่ต้อง find_user_by_id แล้ว
            member = sc.member 
            if not member:
                raise ValueError(f"Member not found for Scorecard with member ID {sc.member.user_id}")
                
            member.add_history(sc, round_type="TOURNAMENT") 
            updated_players.append(f"{member.name} (New HC:{member.current_handicap:.1f})")
            member.add_notification(Notification(f"Tournament {tour.name} has ended. Your final score: {sc.get_gross_score()} strokes. New Handicap: {member.current_handicap:.1f}"))   
            # อัปเดตสถานะทัวร์นาเมนต์เมื่อทุกอย่างเสร็จสิ้น
        tour.update_status(TournamentStatus.COMPLETED)

        return {
            "status": "Success",
            "message": f"ปิดการแข่งขัน {tour.name} เรียบร้อยแล้ว",
            "players_updated": updated_players
        }

    def issue_raincheck_to_user(self, user_id: str, amount: float):
        user = self.find_user(user_id)
        if not user : 
            raise ValueError("Not found user id")

        booking = self.find_booking_by_member(user_id) # สมมติว่ามี method นี้เพื่อเช็คว่าผู้ใช้มีการจองที่เกี่ยวข้องหรือไม่
        if not booking:
            raise ValueError("Error: ผู้ใช้ไม่พบหรือไม่ได้ทำการจอง")
        
        booking.set_status(BookingStatus.RAIN_CHECK_ISSUED)
        
        if user and isinstance(user, Golfer):
            auto_code = f"RC-{len(self.__rain_checks) + 1:04d}-{user_id}"
            # ดึงเบอร์จาก User เพื่อให้ code ผูกติดกับเบอร์
            new_rc = Raincheck(code=auto_code, amount=amount, phone=user.phone)
            # เพพิ่มลงใน system & user(member/guest)
            self.__rain_checks.append(new_rc)
            user.add_raincheck(new_rc)
            # ส่ง noti ไปที่ member 
            msg = f"คุณได้รับคูปอง Rain Check รหัส {auto_code} มูลค่า {amount:,.2f} บาท"
            
            if user and isinstance(user, Member):
                user.add_notification(Notification(msg))
                
            return new_rc
        return None
    
        # เช็ค Raincheck ด้วย code และ user_id โดยดู code ที่ผูกติดกับเบอร์ผ่าน user_id
    def validate_and_use_raincheck(self, code: str, phone: str):
        if not code:
            raise ValueError("Rain Check code is required")
        voucher = next((v for v in self.__rain_checks if v.code == code and v.phone == phone), None)
        if voucher:
            return voucher.amount
        
        raise ValueError("Invalid Rain Check code or phone number")