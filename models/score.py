class Scorecard:
    def __init__(self, member, course):
        self.__member = member
        self.__course = course
        self.__scores = {}

    @property
    def member(self): 
        return self.__member

    def record_score(self, hole_number: int, stroke: int):
        if stroke > 0:
            self.__scores[hole_number] = stroke
            return True
        return False
        
    def has_recorded_scores(self):
        return len(self.__scores) > 0

    def get_gross_score(self):
        return sum(self.__scores.values())

    def get_course_handicap(self):
        # ดึงแต้มต่อมาจาก Member
        return self.__member.current_handicap

    def get_net_score(self):
        return self.get_gross_score() - self.get_course_handicap()

    def get_cumulative_par(self):
        # คำนวณพาร์สะสม (ตัวอย่าง: สมมติว่าสนามมี .par เก็บไว้)
        # หรือถ้าเก็บแยกทีละหลุม ก็สามารถดึงผลรวมพาร์เฉพาะหลุมที่เล่นไปแล้วมาได้
        if hasattr(self.__course, 'par'):
            return self.__course.par
        return 72 # ค่า Default มาตรฐานกอล์ฟ