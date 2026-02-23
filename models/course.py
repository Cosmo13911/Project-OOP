from enum import Enum

class SlotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"

class Course:
    def __init__(self, name, greenfee):
        self.name = name
        self.greenfee = greenfee
        self.slots = []

class TeeTimeSlot:
    def __init__(self, play_date, course):
        self.play_date = play_date
        self.course = course
        self.status = SlotStatus.AVAILABLE