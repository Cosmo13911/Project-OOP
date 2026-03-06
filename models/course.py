from enum import Enum

class SlotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
class Hole:
    def __init__(self, number, par, stroke_index, distance=0):
        self.__number = number            # เลขหลุม (1-18)
        self.__par = par                  # พาร์ประจำหลุม (3, 4, หรือ 5)
        self.__stroke_index = stroke_index # ความยากของหลุม (1-18)
        self.__distance = distance        # ระยะทาง (หลา/เมตร) - ใส่หรือไม่ใส่ก็ได้
    @property
    def par(self):
        return self.__par
class Course:
    # 🌟 1. เอา 'par' ออกจากพารามิเตอร์ของ __init__
    def __init__(self, course_id, name, greenfee, rating, slope_rating):
        if not course_id.startswith("C-"):
            raise ValueError(f"Course ID '{course_id}' ต้องขึ้นต้นด้วย 'C-' เท่านั้น!")
            
        self.__id = course_id
        self.__name = name
        self.__greenfee = greenfee
        self.__slots = []
        self.__holes = {}  # เก็บเป็น Dictionary {เลขหลุม: Object หลุม}
        
        # self.__par = par  <-- 🌟 ลบบรรทัดนี้ทิ้งได้เลย
        self.__rating = rating
        self.__slope_rating = slope_rating

    @property
    def id(self):  
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def par(self):
        # 🌟 2. ให้มันคำนวณพาร์รวมของสนาม จากพาร์ของทุกหลุมมารวมกัน! (Dynamic Calculation)
        # ถ้ายังไม่มีหลุมเลย ผลรวมจะเป็น 0 อัตโนมัติ
        return sum(hole.par for hole in self.__holes.values())

    @property
    def rating(self):
        return self.__rating

    @property
    def slope_rating(self):
        return self.__slope_rating

    @property
    def slots(self):
        return self.__slots

    def add_hole(self, number, par, stroke_index, distance=0):
        # 🌟 3. สร้าง Object Hole ภายในนี้เลย (Composition) ถูกหลัก OOP สุดๆ
        self.__holes[number] = Hole(number, par, stroke_index, distance)

    def get_hole_par(self, number):
        hole = self.__holes.get(number)
        if hole:
            return hole.par
        raise ValueError(f"ไม่พบข้อมูลหลุมที่ {number} ในสนามนี้") # 🌟 ดัก Error ให้ชัดเจนขึ้นแทนการ return 0

    def get_hole_info(self, number):
        return self.__holes.get(number)
class TeeTimeSlot:
    def __init__(self, play_date, course):
        self.__play_date = play_date
        self.__course = course
        self.__status = SlotStatus.AVAILABLE
    @property
    def status(self):
        return self.__status
        
    # 🌟 2. Setter: เปิดให้แก้ไขค่า status ได้ (ตอนจองจะได้เปลี่ยนเป็น RESERVED)
    @status.setter
    def status(self, new_status):
        self.__status = new_status

    # 🌟 3. เผื่อไว้: test.py ใน Step 3 มีการดึงข้อมูลเวลาและสนามไปโชว์ด้วย
    @property
    def play_date(self):
        return self.__play_date
        
    @property
    def course(self):
        return self.__course
        # สร้างคลาสใหม่สืบทอด (Inherit) จาก TeeTimeSlot ตาม Requirement
class Course1Reserve(TeeTimeSlot):
    def __init__(self, play_date, course):
        super().__init__(play_date, course)
        self.__hole = 1 # ระบุชัดเจนว่าเป็นสล็อตสำหรับเริ่มที่หลุม 1