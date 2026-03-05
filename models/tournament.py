from enum import Enum

class TournamentStatus(Enum):
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    CLOSED = "CLOSED"
    DRAW_PUBLISHED = "DRAW_PUBLISHED"

from enum import Enum

# 🌟 1. เพิ่ม Enum ชนิดรางวัล
class Prize(str, Enum):
    TROPHY = "TROPHY"
    CASH = "CASH"
    VOUCHER = "VOUCHER"

class CourseType(str, Enum):
    CHAMPIONSHIP = "CHAMPIONSHIP"
    EXECUTIVE = "EXECUTIVE"

class Tournament:
    def __init__(self, tour_id, name, date, fee):
        self.__tournamentID = tour_id
        self.__name = name
        self.__date = date
        self.__entryFee = fee
        self.__status = TournamentStatus.REGISTRATION_OPEN
        self.__registeredPlayers = [] # เก็บออบเจกต์ Member ที่จ่ายเงินแล้ว
        self.__matchBookings = []
      
        # 🌟 2. เพิ่มตัวแปรเก็บข้อมูลสนามและรางวัล (ตาม Class Diagram)
        self.__course = None 
        self.__prizes = {}

    def set_course(self, course):
        self.__course = course

    @property
    def tournamentID(self):
        return self.__tournamentID
    @property
    def name(self):
        return self.__name
    @property
    def date(self):
        return self.__date
    @property
    def entryFee(self):
        return self.__entryFee
    @property
    def status(self):
        return self.__status
    @property
    def registeredPlayers(self):
        return self.__registeredPlayers
    @property
    def matchBookings(self):
        return self.__matchBookings
    @property
    def course(self):
        return self.__course
    @property
    def prizes(self):
        return self.__prizes
    @course.setter
    def course(self, course):
        self.__course = course
    @prizes.setter
    def prizes(self, prizes):
        self.__prizes = prizes

    def addPlayer(self, member):
        if member not in self.registeredPlayers:
            self.__registeredPlayers.append(member)
            return True
        return False
    def add_match_booking(self, booking):
        self.__matchBookings.append(booking)

    def updateStatus(self, status):
        self.__status = status

    def generatePairing(self):
        # แบ่งกลุ่มละ 4 คนตามรายชื่อที่สมัครมา
        pairings = []
        for i in range(0, len(self.registeredPlayers), 4):
            pairings.append(self.registeredPlayers[i:i+4])
        return pairings