from datetime import datetime
from models.enum import PaymentStatus, RainCheckStatus

class Payment:
    def __init__(self, amount, member, booking_id=None, tournament_id=None):
        self.__payment_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.__amount = amount
        self.__booking_id = booking_id
        self.__tournament_id = tournament_id
        self.__member = member
        self.__type = "TOURNAMENT" if tournament_id else "BOOKING"
        self.__status = PaymentStatus.PENDING

    @property
    def payment_id(self): return self.__payment_id

    @property
    def get_type(self):
        return self.__type
    
    def set_status(self, new_status):
        self.__status = new_status
        
    def get_transaction_details(self):
        return {
            "payment_id": self.__payment_id,
            "amount": self.__amount,
            "type": self.__type,
            "status": self.__status.value,
            "member_id": self.__member.id,
            "booking_id": self.__booking_id,
            "tournament_id": self.__tournament_id
        }

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