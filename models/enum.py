from enum import Enum

class BookingStatus(Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED_PAID = "CONFIRMED_PAID"   
    CANCELLED = "CANCELLED"
    RAIN_CHECK_ISSUED = "RAIN_CHECK_ISSUED"

class CourseType(str, Enum):
    CHAMPIONSHIP = "CHAMPIONSHIP"
    EXECUTIVE = "EXECUTIVE"

class SlotStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"

class RainCheckStatus(Enum):
    VALID = "VALID"
    USED = "USED"
    EXPIRED = "EXPIRED"

class TournamentStatus(Enum):
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    CLOSED = "CLOSED"
    DRAW_PUBLISHED = "DRAW_PUBLISHED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

# models/enum.py
class Tier(Enum):
    SILVER = 0.05    # เก็บค่า rate ไว้ที่นี่เลย
    GOLD = 0.10
    PLATINUM = 0.15
    NONE = 0.0

    @property
    def discount_rate(self) -> float:
        return self.value

    @property
    def booking_day_limit(self) -> int:
        if self == Tier.PLATINUM:
            return 30
        elif self == Tier.GOLD:
            return 14
        elif self == Tier.SILVER:
            return 7
        return 0
        
class UserStatus(str,Enum):
    ACTIVE = "ACTIVE"
    WEEKEND_BAN = "WEEKEND_BAN"
    BANNED = "BANNED"

class CartType(str, Enum):
    STANDARD = "STANDARD"
    COUPLE = "COUPLE"
    VIP = "VIP"

class CaddyLevel(str, Enum):
    TRAINEE = "TRAINEE"
    REGULAR = "REGULAR"
    PRO = "PRO"
    