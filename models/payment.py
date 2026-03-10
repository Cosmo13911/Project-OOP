from datetime import datetime
from models.enum import PaymentStatus, RainCheckStatus

class Payment:
    def __init__(self, payment_id, amount, p_type, member, booking_id=None, tournament_id=None, breakdown=None, individual_bills=None):
        self.__payment_id = payment_id
        self.__amount = amount
        self.__type = p_type
        self.__member = member
        self.__booking_id = booking_id
        self.__tournament_id = tournament_id
        self.__breakdown = breakdown
        self.__individual_bills = individual_bills
        self.__status = PaymentStatus.PENDING


    @property
    def payment_id(self):
        return self.__payment_id
    @property
    def amount(self):
        return self.__amount
    def booking_id(self): return self.__booking_id
    @property
    def type(self):
        return self.__type  
    @property
    def status(self):
        return self.__status
    @property
    def member(self):
        return self.__member
    @property
    def tournament_id(self):
        return self.__tournament_id
    @status.setter
    def status(self, new_status):
        self.__status = new_status
        
    def validate(self):
        # จำลองการยืนยันการชำระเงิน
        self.__status = PaymentStatus.SUCCESS
        return self.__status
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