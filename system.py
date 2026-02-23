from datetime import datetime, timedelta
from models.users import Member, Tier
from models.course import Course, TeeTimeSlot, SlotStatus
from models.booking import Booking

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
        print("--- [System] Initializing Modular Data ---")
        # สร้างสนาม
        c1 = Course("Green Valley Championship", 3500)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        c1.slots.append(TeeTimeSlot(f"{tomorrow} 08:00", c1))
        c1.slots.append(TeeTimeSlot(f"{tomorrow} 09:00", c1))
        self.courses.append(c1)
        
        # สร้างสมาชิก
        self.add_member("John Doe", "081-222-3333", Tier.PLATINUM, 12.5)
        self.add_member("Mary Jane", "085-444-5555", Tier.GOLD, 24.0)
        print(f"System Ready: {len(self.courses)} Course(s) and {len(self.users)} Member(s) loaded.")

    def create_booking(self, member_index, course_index, slot_index):
        try:
            member = self.users[member_index]
            slot = self.courses[course_index].slots[slot_index]

            if slot.status == SlotStatus.AVAILABLE:
                b_id = f"BK-{len(self.bookings) + 1:03d}"
                new_booking = Booking(b_id, member, slot)
                slot.status = SlotStatus.RESERVED
                self.bookings.append(new_booking)
                print(f"Success: Booking {b_id} for {member.name}")
                return new_booking
            else:
                print("Error: Slot already reserved.")
                return None
        except IndexError:
            print("Error: Data index out of range.")
            return None