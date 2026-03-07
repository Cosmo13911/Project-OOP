class Scorecard:
    def __init__(self, member, course):
        self.__member = member
        self.__course = course
        self.__gross_scores = {} 
        self.__adjusted_scores = {}
    @property
    def member(self):
        return self.__member
    @property
    def course(self):
        return self.__course

    def record_score(self, hole_number, stroke):
        
        # สมมติว่า course ของคุณมีเมธอด get_hole_info (หรือ get_hole_par)
        target_hole = self.course.get_hole_info(hole_number) 
        if not target_hole:
            return False, f"ไม่พบข้อมูลหลุม {hole_number} ในสนาม {self.course.name}"
        
        max_allowed_score = target_hole.par * 2
        actual_score = min(stroke, max_allowed_score)

        self.__gross_scores[hole_number] = stroke
        self.__adjusted_scores[hole_number] = actual_score

        return True, "บันทึกคะแนนสำเร็จ"


    @property
    def scores(self):
        return self.__gross_scores.copy()

    @property
    def adjusted_scores(self):
        return self.__adjusted_scores.copy()

    def has_recorded_scores(self):
        return len(self.__gross_scores) > 0
    
    def get_gross_score(self):
        return sum(self.__gross_scores.values())

    def get_adjusted_score(self):
        return sum(self.__adjusted_scores.values())

    def get_course_handicap(self):
        ch = (self.member.current_handicap * (self.course.slope_rating / 113)) + (self.course.rating - self.course.par)
        return ch

    def get_net_score(self):
        return self.get_gross_score() - self.get_course_handicap()

    def get_score_to_par(self):
        return self.get_net_score() - self.get_cumulative_par()

    def get_cumulative_par(self):
        total_par = 0
        for hole_num in self.__gross_scores.keys():
            target_hole = self.course.get_hole_info(hole_num)
            if target_hole:
                total_par += target_hole.par 
        return total_par