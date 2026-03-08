class ScoreRecord:

    def __init__(self, hole, stroke):
        self.__hole = hole       # 🌟 เก็บเป็น Instance ของคลาส Hole เท่านั้น!
        self.__stroke = stroke   # เก็บเป็น Integer (จำนวนครั้งที่ตี)

    # --- Properties (Getters) ---
    @property
    def hole(self):
        return self.__hole

    @property
    def stroke(self):
        return self.__stroke

    # --- Setters ---
    @stroke.setter
    def stroke(self, new_stroke):
        if new_stroke < 0:
            raise ValueError("คะแนน (Stroke) ติดลบไม่ได้")
        self.__stroke = new_stroke

    # --- Methods ---
    @property
    def adjusted_score(self):
        """
        คำนวณคะแนนที่ถูกปรับตามกฎ Double Par (พาร์ x 2)
        ใช้สำหรับเอาไปคิด Handicap เพื่อไม่ให้คะแนนหลุมที่พังมาดึงแต้มต่อ
        """
        # ดึงค่าพาร์จาก Instance ของ Hole โดยตรง
        max_score = self.__hole.par * 2 
        
        if self.__stroke > max_score:
            return max_score
        return self.__stroke
class Scorecard:
    def __init__(self, member, course):
        self.__member = member   # Instance ของ Golfer
        self.__course = course   # Instance ของ Course
        
        # 🌟 เปลี่ยนจาก Dictionary เป็น List ที่เก็บออบเจกต์ ScoreRecord
        self.__records = []      

    @property
    def member(self):
        return self.__member
        
    @property
    def course(self):
        return self.__course

    @property
    def records(self):
        return self.__records

    def record_score(self, hole_number, stroke):
        # 1. ดึง Instance ของ Hole มาจาก Course
        target_hole = self.course.get_hole_info(hole_number) 
        if not target_hole:
            return False, f"ไม่พบข้อมูลหลุม {hole_number} ในสนาม {self.course.name}"
        
        # 2. เช็คว่าเคยบันทึกหลุมนี้ไปหรือยัง (ถ้าเคยให้อัปเดตคะแนน)
        for record in self.__records:
            if record.hole.number == hole_number:
                record.stroke = stroke  # อัปเดตผ่าน Setter ของ ScoreRecord
                return True, "อัปเดตคะแนนสำเร็จ"

        # 3. ถ้ายังไม่เคยบันทึก ให้สร้าง ScoreRecord ใหม่แล้วยัดลง List
        # (ไม่ต้องมานั่งเช็ค Double Par ตรงนี้แล้ว เพราะ ScoreRecord จัดการให้เอง)
        new_record = ScoreRecord(target_hole, stroke)
        self.__records.append(new_record)

        return True, "บันทึกคะแนนสำเร็จ"

    def has_recorded_scores(self):
        return len(self.__records) > 0
    
    def get_gross_score(self):
        return sum(record.stroke for record in self.__records)

    def get_adjusted_score(self):
        return sum(record.adjusted_score for record in self.__records)

    def get_course_handicap(self):
        ch = (self.member.current_handicap * (self.course.slope_rating / 113)) + (self.course.rating - self.course.par)
        return ch

    def get_net_score(self):
        return self.get_gross_score() - self.get_course_handicap()

    def get_score_to_par(self):
        return self.get_net_score() - self.get_cumulative_par()

    def get_cumulative_par(self):
        return sum(record.hole.par for record in self.__records)
    def get_holes_played(self):
        return len(self.__scores)