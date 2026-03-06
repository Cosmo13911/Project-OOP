from enum import Enum
from datetime import datetime

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

# class Payment:
    # def __init__(self, payment_id, amount, p_type, member, tournament_id):
    #     self.paymentID = payment_id
    #     self.amount = amount
    #     self.type = p_type
    #     self.status = PaymentStatus.PENDING
    #     self.member = member # เก็บออบเจกต์ Member
    #     self.tournamentID = tournament_id

class Payment:
    def __init__(self, paymentID, booking_id, amount, breakdown, individual_bills):
        self.__paymentID = paymentID
        self.__booking_id = booking_id
        self.__amount = amount
        self.__breakdown = breakdown # สรุปยอดรวมของทั้งใบจองถูกแบ่งเป็นค่าบริการหมวดหมู่ไหนบ้าง หมวดละเท่าไหร่
        self.__individual_bills = individual_bills #ยอดที่แต่ละคนต้องจ่าย
        self.__status = PaymentStatus.PENDING

    @property
    def paymentID(self): return self.__paymentID
    @property
    def booking_id(self): return self.__booking_id
    @property
    def amount(self): return self.__amount
    @property
    def status(self): return self.__status
    
    def validate(self):
        self.status = PaymentStatus.SUCCESS
        return self.status

class Raincheck:
        def __init__(self, code: str, amount: float, phone: str):
            self.__code = code
            self.__amount = amount
            self.__phone = phone
            self.__status = RainCheckStatus.VALID

        @property
        def code(self):
            return self.__code

        @property
        def amount(self):
            return self.__amount

        @property
        def phone(self):
            return self.__phone

        @property
        def status(self):
            return self.__status

        def mark_as_used(self):
            if self.__status == RainCheckStatus.VALID:
                self.__status = RainCheckStatus.USED
