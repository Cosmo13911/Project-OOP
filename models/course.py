from enum import Enum

class SlotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"

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

        # สร้างคลาสใหม่สืบทอด (Inherit) จาก TeeTimeSlot ตาม Requirement
class Course1Reserve(TeeTimeSlot):
    def __init__(self, play_date, course):
        super().__init__(play_date, course)
        self.hole = 1 # ระบุชัดเจนว่าเป็นสล็อตสำหรับเริ่มที่หลุม 1