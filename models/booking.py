from datetime import datetime

class Booking:
    def __init__(self, booking_id, requester, slot):
        self.booking_id = booking_id
        self.requester = requester
        self.slot = slot
        self.created_at = datetime.now()
        self.golfers = [requester]