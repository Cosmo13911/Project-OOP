from enum import Enum

class CourseType(str, Enum):
    CHAMPIONSHIP = "CHAMPIONSHIP"
    EXECUTIVE = "EXECUTIVE"
    
class SlotStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"

# class Course:
#     def __init__(self, name, greenfee):
#         self.name = name
#         self.greenfee = greenfee
#         self.slots = []
#         self.__operating_hours = [f"{h:02d}:{m:02d}" for h in range(6, 18) for m in (0, 15, 30, 45)]

class Course:
    def __init__(self, name, fee_morning, fee_afternoon, course_type: CourseType, open_time: str = "06:00", close_time: str = "18:00"):
        self.__name = name
        self.__fee_morning = fee_morning
        self.__fee_afternoon = fee_afternoon
        self.__type = course_type
        self.__operating_hours = [f"{h:02d}:{m:02d}" for h in range(6, 18) for m in (0, 15, 30, 45)]
        self.__slots = []  

    @property
    def name(self): return self.__name
    @property
    def fee_morning(self): return self.__fee_morning
    @property
    def fee_afternoon(self): return self.__fee_afternoon
    @property
    def type(self): return self.__type
    @property
    def operating_hours(self): return self.__operating_hours
    @property
    def slots(self): return self.__slots
    
    def generate_slots_for_date(self, date: str): #***
        if any(s.play_date == date for s in self.__slots):
            return
        for time_str in self.__operating_hours:
            new_slot = Course1Reserve(date, time_str, self)
            self.__slots.append(new_slot)

    def get_available_slots(self, date: str):
        self.generate_slots_for_date(date)
        return [s for s in self.__slots if s.play_date == date and s.status == SlotStatus.AVAILABLE]

    def find_slot(self, date: str, time: str):
        self.generate_slots_for_date(date)
        for s in self.__slots:
            if s.play_date == date and s.time == time:
                return s
        return None

# class TeeTimeSlot:
#     def __init__(self, play_date, course):
#         self.play_date = play_date
#         self.course = course
#         self.status = SlotStatus.AVAILABLE

class TeeTimeSlot:
    def __init__(self, play_date, time, course):
        self.__play_date = play_date
        self.__time = time
        self.__course = course
        self.__status = SlotStatus.AVAILABLE

    @property
    def play_date(self): return self.__play_date
    @property
    def time(self): return self.__time
    @property
    def course(self): return self.__course
    @property
    def status(self): return self.__status

    @status.setter
    def status(self, val): self.__status = val
    
# สร้างคลาสใหม่สืบทอด (Inherit) จาก TeeTimeSlot ตาม Requirement
class Course1Reserve(TeeTimeSlot):
    def __init__(self, play_date, course):
        super().__init__(play_date, course)
        self.hole = 1 # ระบุชัดเจนว่าเป็นสล็อตสำหรับเริ่มที่หลุม 1