from abc import ABC, abstractmethod
from models.enum import Tier, UserStatus
from models.notification import Notification
from datetime import timedelta , datetime
from models.payment import Raincheck

class History:
    def __init__(self, score_card_instance):
        """
        sc__score_card_instance: รับเป็นออบเจกต์ sc__score_card เลย (เพราะข้างในมี Course และ List ของ ScoreRecord ครบหมดแล้ว)
        """
        self.__score_card = score_card_instance
        self.__date = datetime.now() 

        self.__gross_score = self.__score_card.get_gross_score()
        self.__adjusted_score = self.__score_card.get_adjusted_score()

    @property
    def score_card(self):
        return self.__score_card

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
        return self.__score_card.course
    
# 1. Abstract Class
class User(ABC):
    def __init__(self, user_id: str, name: str, phone: str):
        self.__user_id = user_id
        self.__name = name
        self.__phone = phone

    @property
    def id(self): return self.__user_id
    @property
    def name(self): return self.__name
    @property
    def phone(self): return self.__phone
    
    # 2. Polymorphism Method
    @abstractmethod
    def calculate_discount(self, amount: float) -> float:
        pass

# Inheritance ชั้นที่ 1
class Golfer(User):
    def __init__(self, user_id: str, name: str, phone: str, handicap: float = 0.0):
        super().__init__(user_id, name, phone)
        self.__current_handicap = handicap
        self.__history = []
        self.__strikes = 0
        self.__raincheck = []
        self.__status = UserStatus.ACTIVE

    @property
    def status(self): 
        return self.__status

    @property
    def current_handicap(self): return self.__current_handicap

    @property
    def history(self):
        return self.__history
    
    @property
    def get_raincheck(self):
        return self.__raincheck

    def add_raincheck(self, rain_check):
        self.__raincheck.append(rain_check)
    
    def add_strike(self, number: int):
        self.__strikes += int(number)
        now = datetime.now()
        
        if self.__strikes >= 3:
            self.__suspended_until = now + timedelta(days=60)
            self.__status = UserStatus.BANNED
        elif self.__strikes >= 2:
            self.__weekend_ban_until = now + timedelta(days=30)
            self.__status = UserStatus.WEEKEND_BAN
        else:
            self.__status = UserStatus.ACTIVE
        return self.__strikes 
    
    def reset_strikes(self):
        self.__strikes = 0
        self.__status = UserStatus.ACTIVE
        return "Strikes have been reset to 0 and status is now ACTIVE."

    def add_history(self, score_card_instance, round_type="General"):
        new_record = History(score_card_instance)

        self.__history.append(new_record)
        self.calculate_handicap()
        return (f"Added {round_type} round to history and updated handicap.")

    def calculate_handicap(self):
        if len(self.__history) < 1:
            return self.__current_handicap
        
        recent_history = self.__history[-20:]
        differentials = []
        for record in recent_history:
            diff = (record.adjusted_score - record.score_card.course.rating) * (113 / record.score_card.course.slope_rating)
            differentials.append(diff)        

        differentials.sort()
        num_scores = len(differentials)

        # หาค่าเฉลี่ยตามจำนวนรอบที่มี (ตามเกณฑ์มาตรฐาน WHS)
        hi = 0.0
        if num_scores == 1:

            hi = differentials[0] - 2.0

        elif num_scores == 2:

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
        # อัปเดตแต้มต่อใหม่ (จำกัดสูงสุดไม่เกิน 54.0 ตามมาตรฐาน WHS)

        new_handicap = round(min(max(hi, 0.0), 54.0), 1)
        self.__current_handicap = new_handicap
        return self.__current_handicap
# Inheritance ชั้นที่ 2
class Member(Golfer):
    def __init__(self, user_id: str, name: str, phone: str, tier: Tier = Tier.SILVER, handicap: float = 0.0):
        super().__init__(user_id, name, phone, handicap)
        self.__tier = tier
        self.__notifications = []

    @property
    def tier(self): return self.__tier

    # Polymorphism: Member ได้ส่วนลดตาม Tier (สิทธิ์/ส่วนลด 1 ประเภท)
    def calculate_discount(self, amount: float) -> float:
        return amount * self.__tier.discount_rate
    

    def add_notification(self, notification: Notification):
        self.__notifications.append(notification)

    @property   
    def get_notifications(self):
        return self.__notifications

# Inheritance ชั้นที่ 2
class Guest(Golfer):
    def __init__(self, user_id: str, name: str, phone: str):
        super().__init__(user_id, name, phone, handicap=0.0)

    # Polymorphism: Guest ไม่ได้ส่วนลด
    def calculate_discount(self, amount: float) -> float:
        return 0.0

    def add_notification(self, notification: Notification):
        pass
    
