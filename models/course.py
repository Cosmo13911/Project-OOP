from models.enum import SlotStatus
class Hole:
    def __init__(self, number: int, par: int):
        self.__number = number
        self.__par = par

    @property
    def par(self):
        return self.__par
    
    @property
    def number(self):  
        return self.__number

    @property
    def par(self):
        return self.__par

class Course:
    def __init__(self, course_id, name, fee_morning, fee_afternoon, course_type, rating, slope_rating, open_time="06:00", close_time="18:00"):
        self.__id = course_id
        self.__name = name
        self.__fee_morning = fee_morning
        self.__fee_afternoon = fee_afternoon
        self.__type = course_type
        self.__rating = rating
        self.__slope_rating = slope_rating  
        self.__open_time = open_time
        self.__close_time = close_time
        self.__operating_hours = [f"{h:02d}:{m:02d}" for h in range(6, 18) for m in (0, 15, 30, 45)]
        self.__slots = []  
        self.__holes = []

    @property
    def id(self): return self.__id
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
    def par(self): return sum(hole.par for hole in self.__holes)
    @property
    def slots(self): return self.__slots
    @property
    def rating(self): return self.__rating
    @property
    def slope_rating(self): return self.__slope_rating
    @property
    def get_difficulty(self):
        if self.__slope_rating > 140: return "Very Hard (Championship Level)"
        elif self.__slope_rating > 120: return "Challenging"
        return "Normal"
    
    def get_price_by_time(self, time_str: str):
        hour = int(time_str.split(":")[0])
        return self.__fee_morning if hour < 12 else self.__fee_afternoon
    
    def generate_slots_for_date(self, date: str):
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
    
    def add_hole(self, number: int, par: int):
        # ตรวจสอบก่อนเพิ่มเพื่อป้องกันเลขหลุมซ้ำ (Guard Clause)
        if any(h.number == number for h in self.__holes):
            return
        
        if len(self.__holes) < 18:
            new_hole = Hole(number, par)
            self.__holes.append(new_hole)

    def get_hole_par(self, number: int):
        # วนลูปหาหลุมที่หมายเลขตรงกันใน List ของ Hole objects
        for hole in self.__holes:
            if hole.number == number:
                return hole.par
        raise ValueError(f"ไม่พบข้อมูลหลุมที่ {number} ในสนามนี้")
    
    def get_hole_info(self, number: int):
        # วนลูปหาเพื่อคืนค่า Object Hole ทั้งใบ
        for hole in self.__holes:
            if hole.number == number:
                return hole
        return None

class TeeTimeSlot:
    def __init__(self, play_date, time, course):
        # ทุก attribute เป็น private ทั้งหมด 
        self.__play_date = play_date
        self.__time = time
        # มีสถานะติดตามอย่างน้อย 3 สถานะ 
        self.__course = course
        self.__status = SlotStatus.AVAILABLE 

    @property
    def play_date(self): return self.__play_date
    @property
    def time(self): return self.__time
    @property
    def status(self): return self.__status
    @property
    def course(self): return self.__course

    @status.setter
    def status(self, new_status): 
        self.__status = new_status

# สร้างคลาสใหม่สืบทอด (Inherit) จาก TeeTimeSlot ตาม Requirement
class Course1Reserve(TeeTimeSlot):
    def __init__(self, play_date, time, course):
        super().__init__(play_date, time, course) # ส่งค่าให้คลาสแม่จัดการ
        self.__hole = 1 # เก็บค่าเฉพาะตัวไว้ที่นี่

    @property
    def get_hole(self): return self.__hole