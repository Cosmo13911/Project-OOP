from enum import Enum
from datetime import datetime

class PaymentType(Enum):
    TOURNAMENT_FEE = "TOURNAMENT_FEE"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"

class Payment:
    def __init__(self, payment_id, amount, p_type, member, tournament_id):
        self.paymentID = payment_id
        self.amount = amount
        self.type = p_type
        self.status = PaymentStatus.PENDING
        self.member = member # เก็บออบเจกต์ Member
        self.tournamentID = tournament_id

    def validate(self):
        # จำลองการยืนยันการชำระเงิน
        self.status = PaymentStatus.SUCCESS
        return self.status