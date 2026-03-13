import uuid
from datetime import datetime
from models.enum import PaymentStatus, RainCheckStatus, TournamentStatus

class Payment:
    def __init__(self, amount, member, transaction = None, booking_id=None, tournament_id=None):
        unique_suffix = str(uuid.uuid4())[:6].upper()
        self.__payment_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.__amount = amount
        self.__booking_id = booking_id
        self.__tournament_id = tournament_id
        self.__member = member
        self.__type = "TOURNAMENT" if tournament_id else "BOOKING"
        self.__status = PaymentStatus.PENDING
        self.__transaction = transaction
        self.__time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    @property
    def member(self): return self.__member
    @property
    def payment_id(self): return self.__payment_id
    @property
    def amount(self): return self.__amount
    @property
    def status(self): return self.__status
    @property
    def time(self): return self.__time
    @property
    def get_type(self):
        return self.__type
    @property
    def booking_id(self): return self.__booking_id
    
    def set_status(self, new_status):
        self.__status = new_status
        
    def get_transaction_details(self):
        return self.__transaction
        
    @property
    def tournament_id(self):
        return self.__tournament_id
    
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

        
        def set_status(self, new_status):
            self.__status = new_status