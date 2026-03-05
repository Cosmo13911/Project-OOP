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
    def __init__(self, course_id, name, greenfee,par,rating,slope_rating):
        if not course_id.startswith("C-"):
            raise ValueError(f"Course ID '{course_id}' ต้องขึ้นต้นด้วย 'C-' เท่านั้น!")
        self.__id = course_id
        self.__name = name
        self.__greenfee = greenfee
        self.__slots = []
        self.__holes = {}
        self.__par=par
        self.__rating=rating
        self.__slope_rating=slope_rating
    @property
    def id(self):  # 🌟 เพิ่ม property สำหรับดึง ID
        return self.__id
    @property
    def name(self):
        return self.__name
        
    @property
    def par(self):
        return self.__par
        
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
        # ฟังก์ชันสำหรับเพิ่มข้อมูลหลุมเข้าไปในสนาม
        self.__holes[number] = Hole(number, par, stroke_index, distance)
    def get_hole_par(self, number):
        # ดึงข้อมูลหลุมที่ i ออกมาจาก dictionary __holes
        hole = self.__holes.get(number)
        if hole:
            return hole.par # คืนค่าพาร์ (เช่น 4) กลับไปคำนวณคะแนน
        return 0
    def get_hole_info(self, number):
        # ฟังก์ชันดึงข้อมูลหลุมมาดู
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