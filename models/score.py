# Project-OOP/models/score.py

class ScoreRecord:
    def __init__(self, hole_number: int, stroke: int):
        self.__hole_number = hole_number
        self.__stroke = stroke

    @property
    def hole_number(self):
        return self.__hole_number

    @property
    def stroke(self):
        return self.__stroke

class Scorecard:
    def __init__(self, member, course):
        self.__member = member
        self.__course = course
        # เปลี่ยนจาก {} เป็น [] เพื่อเก็บ ScoreRecord objects
        self.__scores = [] 

    @property
    def member(self): 
        return self.__member
    
    @property
    def course(self):
        return self.__course

    def record_score(self, hole_number  : int, stroke: int):
        if stroke > 0:
            # ตรวจสอบว่าเคยจดหลุมนี้ไปหรือยัง ถ้ามีให้ อัปเดต ถ้าไม่มีให้ append ใหม่
            for record in self.__scores:
                if record.hole_number == hole_number:
                    # ในทางปฏิบัติอาจจะสร้าง setter หรือสร้าง object ใหม่ทับ
                    self.__scores.remove(record)
                    break
            
            new_record = ScoreRecord(hole_number, stroke)
            self.__scores.append(new_record)
            return True
        return False
         
    def has_recorded_scores(self):
        return len(self.__scores) > 0

    def get_gross_score(self):
        # วนลูปบวกคะแนนจาก List ของ objects
        return sum(record.stroke for record in self.__scores)

    def get_course_handicap(self):
        # ดึงแต้มต่อมาจาก Member
        return self.__member.current_handicap

    def get_net_score(self):
        return self.get_gross_score() - self.get_course_handicap()

    def get_cumulative_par(self):
        # ดึงค่าพาร์รวมจากสนาม (Course)
        return self.__course.par
    
    # เพิ่มใน models/score.py คลาส Scorecard
    def get_adjusted_score(self):
        # ตามมาตรฐานกอล์ฟ มักจะจำกัดคะแนนต่อหลุมไม่เกิน Net Double Bogey
        # แต่เบื้องต้นสามารถใช้ Gross Score ไปก่อนได้ถ้ายังไม่มี Logic ซับซ้อน
        return self.get_gross_score()