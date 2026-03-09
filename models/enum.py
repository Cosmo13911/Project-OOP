from enum import Enum

class BookingStatus(Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED_PAID = "CONFIRMED_PAID"   
    CANCELLED = "CANCELLED"

class CourseType(str, Enum):
    CHAMPIONSHIP = "CHAMPIONSHIP"
    EXECUTIVE = "EXECUTIVE"

class SlotStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"

class PaymentType(Enum):
    TOURNAMENT_FEE = "TOURNAMENT_FEE"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    QR_CODE = "QR_CODE"
    CASH = "CASH"

class RainCheckStatus(Enum):
    VALID = "VALID"
    USED = "USED"
    EXPIRED = "EXPIRED"

class TournamentStatus(Enum):
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    CLOSED = "CLOSED"
    DRAW_PUBLISHED = "DRAW_PUBLISHED"
    COMPLETED = "COMPLETED"

class Tier(Enum):
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class UserStatus(Enum):
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
    VIP = "VIP"