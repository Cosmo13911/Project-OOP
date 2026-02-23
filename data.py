# data.py
from enum import Enum
from datetime import datetime, timedelta

class Tier(Enum):
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class SlotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"

# --- 1. คลาสพื้นฐานที่สุด ---
class User:
    def __init__(self, user_id, name, phone):
        self.user_id = user_id
        self.name = name
        self.phone = phone

# --- 2. คลาส Golfer (สืบทอดจาก User) ---
# เก็บข้อมูลเฉพาะของนักกอล์ฟ เช่น Handicap
class Golfer(User):
    def __init__(self, user_id, name, phone, current_handicap=0.0):
        super().__init__(user_id, name, phone)
        self.current_handicap = current_handicap
        self.history = []  # เก็บ ScoreRecord ในอนาคต

# --- 3. คลาส Member (สืบทอดจาก Golfer) ---
class Member(Golfer):
    def __init__(self, user_id, name, phone, tier=Tier.SILVER, handicap=0.0):
        # ส่งค่าไปให้ Golfer และ User ตามลำดับ
        super().__init__(user_id, name, phone, current_handicap=handicap)
        self.tier = tier
        self.membership_expiry = datetime.now() + timedelta(days=365)

# --- ส่วนอื่นๆ ของระบบ ---
class Course:
    def __init__(self, name, greenfee):
        self.name = name
        self.greenfee = greenfee
        self.slots = []

class TeeTimeSlot:
    def __init__(self, play_date, course):
        self.play_date = play_date
        self.course = course
        self.status = SlotStatus.AVAILABLE

class Booking:
    def __init__(self, booking_id, requester, slot):
        self.booking_id = booking_id
        self.requester = requester # คนจองต้องเป็น Golfer/Member
        self.slot = slot
        self.golfers = [requester] # ลิสต์รายชื่อคนเล่นในกลุ่ม (1-4 คน)

class GreenValleySystem:
    def __init__(self):
        self.users = []
        self.courses = []
        self.bookings = []

    def add_member(self, name, phone, tier_type, handicap=0.0):
        new_id = f"M-{len(self.users) + 1:03d}"
        new_member = Member(new_id, name, phone, tier_type, handicap)
        self.users.append(new_member)
        return new_member

    def create_data(self):
        print("--- [System] Initializing Data with Inheritance ---")
        
        # สร้างสนาม
        c1 = Course("Green Valley Championship", 3500)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        c1.slots.append(TeeTimeSlot(f"{tomorrow} 08:00", c1))
        self.courses.append(c1)
        
        # สร้าง Member (ซึ่งเป็น Golfer โดยอัตโนมัติ)
        # John: Platinum, Handicap 12.5
        self.add_member("John Doe", "081-222-3333", Tier.PLATINUM, 12.5)
        # Mary: Gold, Handicap 24.0
        self.add_member("Mary Jane", "085-444-5555", Tier.GOLD, 24.0)
        
        print(f"Loaded: {len(self.users)} Members (as Golfers)")

    def create_booking(self, member_index, course_index, slot_index):
        member = self.users[member_index]
        slot = self.courses[course_index].slots[slot_index]

        if slot.status == SlotStatus.AVAILABLE:
            b_id = f"BK-{len(self.bookings) + 1:03d}"
            new_booking = Booking(b_id, member, slot)
            slot.status = SlotStatus.RESERVED
            self.bookings.append(new_booking)
            print(f"Success: Booking {b_id} for Golfer '{member.name}'")
            return new_booking
        return None