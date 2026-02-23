from enum import Enum
from datetime import datetime, timedelta

class Tier(Enum):
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class User:
    def __init__(self, user_id, name, phone):
        self.user_id = user_id
        self.name = name
        self.phone = phone

class Golfer(User):
    def __init__(self, user_id, name, phone, current_handicap=0.0):
        super().__init__(user_id, name, phone)
        self.current_handicap = current_handicap
        self.history = []

class Member(Golfer):
    def __init__(self, user_id, name, phone, tier=Tier.SILVER, handicap=0.0):
        super().__init__(user_id, name, phone, current_handicap=handicap)
        self.tier = tier
        self.membership_expiry = datetime.now() + timedelta(days=365)