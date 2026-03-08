from enum import Enum
from datetime import datetime, timedelta
class History:
    def __init__(self, scorecard_instance, round_type="GENERAL"):
        """
        scorecard_instance: รับเป็นออบเจกต์ Scorecard เลย (เพราะข้างในมี Course และ List ของ ScoreRecord ครบหมดแล้ว)
        """
        self.__scorecard = scorecard_instance
        self.__round_type = round_type
        self.__date = datetime.now() # เก็บวันที่บันทึกประวัติ

        # 🌟 โค้ดสั้นลงมาก! เพราะเราโยนหน้าที่คำนวณไปให้ Scorecard และ ScoreRecord ทำหมดแล้ว
        self.__gross_score = self.__scorecard.get_gross_score()
        self.__adjusted_score = self.__scorecard.get_adjusted_score()

    # --- Properties ---
    @property
    def scorecard(self):
        return self.__scorecard

    @property
    def round_type(self):
        return self.__round_type

    @property
    def date(self):
        return self.__date

    @property
    def gross_score(self):
        return self.__gross_score

    @property
    def adjusted_score(self):
        return self.__adjusted_score

    @property
    def course(self):
        # ดึง Course ผ่าน Scorecard ได้เลย
        return self.__scorecard.course
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
    def add_history(self, scorecard_instance, round_type="General"):

        new_record = History(scorecard_instance)

        self.__history.append(new_record)
        self.calculate_handicap()
        print(f"Added {round_type} round to history and updated handicap.")

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