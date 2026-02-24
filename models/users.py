from enum import Enum
from datetime import datetime , timedelta

class Notification:
    def __init__(self, title, message):
        self.__title = title
        self.__message = message
        self.__date = datetime.now().strftime("%Y-%m-%d %H:%M")
    @property
    def title(self):
        return self.__title 
    @property
    def message(self):
        return self.__message
    @property
    def date(self):
        return self.__date

class Tier(Enum):
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class User:
    def __init__(self, user_id, name, phone):
        self.__user_id = user_id
        self.__name = name
        self.__phone = phone

    # getter 
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
    @property
    def current_handicap(self):
        return self.__current_handicap
    @property
    def history(self):
        return self.__history
    @history.setter
    def history(self, new_history):
        self.__history.append(new_history)

class Member(Golfer):
    def __init__(self, user_id, name, phone, tier=Tier.SILVER, handicap=0.0):
        super().__init__(user_id, name, phone, current_handicap=handicap)
        self.__tier = tier
        self.__membership_expiry = datetime.now() + timedelta(days=365)
        self.__notifications = []
    @property
    def tier(self):
        return self.__tier
    @property
    def membership_expiry(self):
        return self.__membership_expiry
    @property
    def notifications(self):    
        return self.__notifications
    
    @notifications.setter
    def notifications(self, message):
        self.__notifications.append(message)
        
    def place_order(self, system, booking_id, product, quantity):
        return system.place_order(booking_id, product, quantity)
    
    def add_notification(self, message):
        self.__notifications.append(message)
    
    def view_notifications(self):
        return self.__notifications