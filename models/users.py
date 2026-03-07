from enum import Enum
from datetime import datetime, timedelta
class History:
    def __init__(self, course, hole_scores, round_type="TOURNAMENT"):
        """
        course: ออบเจกต์สนาม (เพื่อให้รู้ว่าแต่ละหลุม พาร์อะไร)
        hole_scores: Dictionary คะแนน 18 หลุม เช่น {1: 4, 2: 5, ..., 18: 6}
        """
        self.course = course
        self.hole_scores = hole_scores 
        self.round_type = round_type

        # 1. Gross Score: คะแนนดิบ (ตีจริงเท่าไหร่ รวมเท่านั้น)
        self.gross_score = sum(hole_scores.values())
        
        # 2. Adjusted Score: คะแนนที่ถูกตัดเพดาน Double Par แล้ว (เอาไว้คิด Handicap)
        self.adjusted_score = self.calculate_adjusted_score()

    def calculate_adjusted_score(self):
        """ฟังก์ชันคำนวณคะแนน โดยจำกัดเพดานสูงสุดไว้ที่ Double Par ต่อหลุม"""
        adjusted_total = 0
        
        for hole_number, stroke in self.hole_scores.items():
            # สมมติว่าออบเจกต์ Course ของคุณมีฟังก์ชันหรือดิกชันนารีเก็บค่าพาร์แต่ละหลุม
            # เช่น course.get_par(1) จะได้ค่า 4
            hole_par = self.course.get_hole_par(hole_number) 
            
            # กฎ Double Par (เช่น พาร์ 4 ตีได้สูงสุดแค่ 8)
            max_allowed_score = hole_par * 2  
            
            # ถ้าตีเกิน Double Par ให้คิดแค่ Double Par
            if stroke > max_allowed_score:
                adjusted_total += max_allowed_score
            else:
                adjusted_total += stroke
                
        return adjusted_total
class Tier(Enum):
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class User:
    def __init__(self, user_id, name, phone):
        self.__user_id = user_id
        self.__name = name
        self.__phone = phone
    @property
    def user_id(self):
        return self.__user_id
    @property
    def name(self):
        return self.__name

class Golfer(User):
    def __init__(self, user_id, name, phone, current_handicap=0.0):
        super().__init__(user_id, name, phone)
        self.__current_handicap = current_handicap
        self.__history = []
    @property
    def current_handicap(self):
        return self.__current_handicap
        
    @property
    def history(self):
        return self.__history

    # 🌟 ฟังก์ชันเสริม: เอาไว้รับคะแนนจาก Scorecard มาใส่ประวัติ
    def add_history(self, course, hole_scores, round_type="TOURNAMENT"):
        # สร้าง History object ใหม่ด้วยข้อมูลหลุมต่อหลุม
        new_record = History(course, hole_scores, round_type)
        self.__history.append(new_record)
        self.calculate_handicap()

    def calculate_handicap(self):
        if len(self.__history) < 3:
            return self.__current_handicap 

        recent_history = self.__history[-20:]
        differentials = []

        for record in recent_history:
            # 🌟 เปลี่ยนจาก record.gross_score เป็น record.adjusted_score !!
            # เพื่อให้ Handicap แม่นยำตามมาตรฐาน WHS
            diff = (record.adjusted_score - record.course.rating) * (113 / record.course.slope_rating)
            differentials.append(diff)
        differentials.sort()
        num_scores = len(differentials)

        # 5. หาค่าเฉลี่ยตามจำนวนรอบที่มี (ตามเกณฑ์มาตรฐาน WHS)
        hi = 0.0
        if num_scores == 3:
            hi = differentials[0] - 2.0
        elif num_scores == 4:
            hi = differentials[0] - 1.0
        elif num_scores == 5:
            hi = differentials[0]
        elif num_scores == 6:
            hi = sum(differentials[:2]) / 2 - 1.0
        elif 7 <= num_scores <= 8:
            hi = sum(differentials[:2]) / 2
        elif 9 <= num_scores <= 11:
            hi = sum(differentials[:3]) / 3
        elif 12 <= num_scores <= 14:
            hi = sum(differentials[:4]) / 4
        elif 15 <= num_scores <= 16:
            hi = sum(differentials[:5]) / 5
        elif 17 <= num_scores <= 18:
            hi = sum(differentials[:6]) / 6
        elif num_scores == 19:
            hi = sum(differentials[:7]) / 7
        else: # 20 รอบพอดี
            hi = sum(differentials[:8]) / 8

        # 6. อัปเดตแต้มต่อใหม่ (จำกัดสูงสุดไม่เกิน 54.0 ตามมาตรฐาน WHS)
        new_handicap = round(min(max(hi, 0.0), 54.0), 1)
        self.__current_handicap = new_handicap
        return self.__current_handicap

class Member(Golfer):
    def __init__(self, user_id, name, phone, tier=Tier.SILVER, handicap=0.0):
        super().__init__(user_id, name, phone, current_handicap=handicap)
        self.__tier = tier
        self.__membership_expiry = datetime.now() + timedelta(days=365)
        self.__notifications = []

    @property
    def tier(self):
        return self.__tier
    def place_order(self, system, booking_id, product, quantity):
        return system.place_order(booking_id, product, quantity)
    
    def add_notification(self, message):
        self.__notifications.append(message)
    
    def view_notifications(self):
        return self.__notifications