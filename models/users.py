from enum import Enum
from datetime import datetime, timedelta
class History:
    def __init__(self,course,gross_score):
        self.course=course
        self.gross_score=gross_score
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
    def add_history(self, course, gross_score):
        self.__history.append(History(course, gross_score))
        self.calculate_handicap() # คำนวณแต้มต่อใหม่ทันทีที่เพิ่มรอบใหม่
    def calculate_handicap(self):
        # 1. เช็กว่ามีประวัติการเล่นอย่างน้อย 3 รอบหรือไม่
        if len(self.__history) < 3:
            return self.__current_handicap 

        # 2. ดึงประวัติการเล่น "20 รอบล่าสุด"
        recent_history = self.__history[-20:]
        differentials = []

        # 3. คำนวณ Score Differential ของแต่ละรอบ
        for record in recent_history:
            diff = (record.gross_score - record.course.rating) * (113 / record.course.slope_rating)
            differentials.append(diff)

        # 4. เรียงลำดับจากน้อยไปมาก เพื่อหาค่าที่ดีที่สุด (ต่ำที่สุด)
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