from enum import Enum
from datetime import datetime

class PaymentType(Enum):
    TOURNAMENT_FEE = "TOURNAMENT_FEE"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"

class Payment:
    def __init__(self, payment_id, amount, p_type, member, tournament_id):
        self.__paymentID = payment_id
        self.__amount = amount
        self.__type = p_type
        self.__status = PaymentStatus.PENDING
        self.__member = member # เก็บออบเจกต์ Member
        self.__tournamentID = tournament_id
    @property
    def paymentID(self):
        return self.__paymentID
    @property
    def amount(self):
        return self.__amount
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
    def tournamentID(self):
        return self.__tournamentID
    @status.setter
    def status(self, new_status):
        self.__status = new_status
    

    def validate(self):
        # จำลองการยืนยันการชำระเงิน
        self.__status = PaymentStatus.SUCCESS
        return self.__status