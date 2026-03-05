from enum import Enum

class SlotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"

# 🌟 1. เพิ่ม Enum ชนิดสนาม (สืบทอดจาก str เพื่อให้ทำ Dropdown ได้)
class CourseType(str, Enum):
    CHAMPIONSHIP = "CHAMPIONSHIP"
    EXECUTIVE = "EXECUTIVE"

class Course:
    def __init__(self, name, greenfee, course_type=CourseType.CHAMPIONSHIP):        
        self.__name = name
        self.__greenfee = greenfee
        self.__type = course_type # เก็บชนิดสนาม
        self.__slots = []
    @property
    def name(self):
        return self.__name
    def greenfee(self):
        return self.__greenfee
    @property
    def type(self):
        return self.__type
    @property
    def slots(self):
        return self.__slots
    def add_slot(self, slot):
        self.__slots.append(slot)

class TeeTimeSlot:
    def __init__(self, play_date, course):
        self.__play_date = play_date
        self.__course = course
        self.__status = SlotStatus.AVAILABLE
    @property
    def play_date(self):
        return self.__play_date
    @property
    def course(self):
        return self.__course
    @property
    def status(self):
        return self.__status
    @status.setter
    def status(self, new_status):
        self.__status = new_status
    def update_status(self, new_status):
        self.__status = new_status

        # สร้างคลาสใหม่สืบทอด (Inherit) จาก TeeTimeSlot ตาม Requirement
class Course1Reserve(TeeTimeSlot):
    def __init__(self, play_date, course):
        super().__init__(play_date, course)
        self.hole = 1 # ระบุชัดเจนว่าเป็นสล็อตสำหรับเริ่มที่หลุม 1