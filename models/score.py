class Scorecard:
    def __init__(self, member, course):
        self.__member = member
        self.__course = course
        self.__scores = {}
    @property
    def member(self):
        return self.__member
    @property
    def course(self):
        return self.__course

    def record_score(self, hole_number, stroke):
        
        target_hole = self.course.get_hole_info(hole_number)
        
        if not target_hole:
            raise ValueError(f"ไม่พบหลุม {hole_number} ในสนาม {self.course.name}")

        #ระบบตัดคะแนนแบบ Double Par (ทัวร์นาเมนต์สมัครเล่นนิยมใช้)
        max_allowed_score = target_hole.par * 2
        actual_score = min(stroke, max_allowed_score)

        self.__scores[hole_number] = actual_score
        return actual_score


    @property
    def scores(self):
        return self.__scores.copy()

    def has_recorded_scores(self):
        return len(self.__scores) > 0
    
    def get_gross_score(self):
        return sum(self.__scores.values())

    def get_course_handicap(self):
        ch = (self.member.current_handicap * (self.course.slope_rating / 113)) + (self.course.rating - self.course.par)
        return ch
    def get_net_score(self):
        # คะแนนสุทธิ = คะแนนดิบ - แต้มต่อสนาม (Course Handicap)
        return self.get_gross_score() - self.get_course_handicap()

    def get_score_to_par(self):
        # คะแนนเทียบพาร์ (เรียกใช้ attribute .par ของ Course ได้เลย)
        return self.get_net_score() - self.course.par
    def get_cumulative_par(self):
        total_par = 0
        # วนลูปตามเลขหลุมที่ผู้เล่นคนนี้บันทึกคะแนนไปแล้ว
        for hole_num in self.__scores.keys():
            # ดึงค่าพาร์ของหลุมนั้นๆ มาจากออบเจกต์ Course
            total_par += self.course.get_hole_par(hole_num) 
        return total_par