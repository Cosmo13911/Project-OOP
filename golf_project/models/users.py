from enum import Enum
from datetime import datetime, timedelta

class Tier(Enum):
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    
class UserStatus(Enum):
    ACTIVE = "ACTIVE"
    WEEKEND_BAN = "WEEKEND_BAN"
    BANNED = "BANNED"
    EXPIRED = "EXPIRED"

# class User:
#     def __init__(self, user_id, name, phone):
#         self.user_id = user_id
#         self.name = name
#         self.phone = phone

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
    
    @property
    def phone(self): 
        return self.__phone

class Golfer(User):
    def __init__(self, user_id, name, phone, current_handicap=0.0):
        super().__init__(user_id, name, phone)
        self.__current_handicap = current_handicap
        self.__history = []
        self.__my_rainchecks = []

    @property
    def history(self): 
        return self.__history
    
    @property
    def my_rainchecks(self):
        return self.__my_rainchecks
    
    def add_to_history(self, booking):
        self.__history.append(booking)
        
    def add_raincheck(self, raincheck):
        self.__my_rainchecks.append(raincheck)
    
class Member(Golfer):
    def __init__(self, user_id, name, phone, tier=Tier.SILVER, handicap=0.0):
        super().__init__(user_id, name, phone, current_handicap=handicap)
        self.tier = tier
        self.membership_expiry = datetime.now() + timedelta(days=365)
        self.__notifications = []
        self.__strikes = 0
        self.__suspended_until = None
        self.__weekend_ban_until = None
        self.__status = UserStatus.ACTIVE

    @property
    def tier(self): 
        return self.__tier
    
    @property
    def strikes(self): 
        return self.__strikes
    
    @property
    def status(self): 
        return self.__status
    
    @property
    def suspended_until(self): 
        return self.__suspended_until
    
    @property
    def weekend_ban_until(self): 
        return self.__weekend_ban_until
    
    @status.setter
    def status(self, val): 
        self.__status = val
    
    def add_strike(self):
        self.__strikes += 1
        now = datetime.now()
        if self.__strikes == 2:
            self.__weekend_ban_until = now + timedelta(days=30)
            self.__status = UserStatus.WEEKEND_BAN
        elif self.__strikes >= 3:
            self.__suspended_until = now + timedelta(days=60)
            self.__status = UserStatus.BANNED
                    
    def is_suspended(self):
        if self.__suspended_until and datetime.now() < self.__suspended_until:
            return True, f"บัญชีถูกระงับชั่วคราวถึง {self.__suspended_until.date()} (สะสมครบ 3 Strike)"
        return False, ""

    def is_weekend_banned(self, target_date_str):
        target_dt = datetime.strptime(target_date_str, "%d-%m-%Y")
        is_weekend = target_dt.weekday() >= 5 # 5=Sat, 6=Sun
        if is_weekend and self.__weekend_ban_until and datetime.now() < self.__weekend_ban_until:
            return True
        return False
    
    def check_and_update_status(self): # update stike status ตามเวลาที่ผ่านไป  
        now = datetime.now()
        # 1. BANNED (3 Strikes) ครบกำหนด 60 วัน
        if self.status == UserStatus.BANNED:
            if self.__suspended_until and now >= self.__suspended_until:
                self.status = UserStatus.ACTIVE
                self.__strikes = 0 # รีเซ็ตแต้มความผิด (Option)
                return "UNBANNED"
        # 2. Weekend Ban ครบกำหนด 30 วัน
        elif self.status == UserStatus.WEEKEND_BAN:
            if self.__weekend_ban_until and now >= self.__weekend_ban_until:
                self.status = UserStatus.ACTIVE
        return "NO_CHANGE"
    
    def add_notification(self, message):
        self.__notifications.append(message)
    
    def view_notifications(self):
        return self.__notifications
    
    def place_order(self, system, booking_id, product, quantity):
        return system.place_order(booking_id, product, quantity)
    
    def add_notification(self, message):
        self.__notifications.append(message)
    
    def view_notifications(self):
        return self.__notifications
    
class Guest(Golfer):
    def __init__(self, user_id, name, phone, handicap=0.0):
        super().__init__(user_id, name, phone, current_handicap=handicap)