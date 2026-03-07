from enum import Enum
from models.score import Scorecard
from models.leaderboard import Leaderboard
class TournamentStatus(Enum):
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    CLOSED = "CLOSED"
    DRAW_PUBLISHED = "DRAW_PUBLISHED"
    COMPLETED = "COMPLETED"

class Tournament:
    def __init__(self, tour_id, name, date, fee,course):
        self.__tournamentID = tour_id
        self.__name = name
        self.__date = date
        self.__entryFee = fee
        self.__course = course
        self.__status = TournamentStatus.REGISTRATION_OPEN
        self.__registeredPlayers = [] # เก็บออบเจกต์ Member ที่จ่ายเงินแล้ว
        self.__matchBookings = []
        self.__scorecards = {}
        self.__reserved_slots = []
    @property
    def tournamentID(self):
        return self.__tournamentID
    @property
    def scorecards(self):
        return self.__scorecards
    @property
    def name(self):
        return self.__name

    @property
    def entryFee(self):
        return self.__entryFee

    @property
    def registeredPlayers(self):
        return self.__registeredPlayers

    @property
    def status(self):
        return self.__status

    @property
    def matchBookings(self):
        return self.__matchBookings
    @property
    def course(self):
        return self.__course
    @property
    def date(self):
        return self.__date
    def set_to_in_progress(self):
        self.__status = TournamentStatus.IN_PROGRESS

    def set_to_draw_published(self):
        self.__status = TournamentStatus.DRAW_PUBLISHED
    def set_to_completed(self):
        self.__status = TournamentStatus.COMPLETED
    def addPlayer(self, member):
        # 🌟 แก้ไขให้ใช้ self.__registeredPlayers (จัดการตัวแปร Private โดยตรง)
        if member not in self.__registeredPlayers:
            self.__registeredPlayers.append(member)
            self.__scorecards[member.user_id] = Scorecard(member, self.course)
            return True
        return False

    def updateStatus(self, status):
        self.__status = status

    def generatePairing(self):
        # แบ่งกลุ่มละ 4 คนตามรายชื่อที่สมัครมา
        pairings = []
        for i in range(0, len(self.registeredPlayers), 4):
            pairings.append(self.registeredPlayers[i:i+4])
        return pairings

    # 🌟 1. แก้ไขเมธอดนี้ (ใส่ __ ให้ครบ)
    def record_player_score(self, member, hole_number, stroke):
        # เปลี่ยนจาก self._scorecards เป็น self.__scorecards
        if member.user_id not in self.__scorecards:
            return False
            
        # เปลี่ยนจาก self._scorecards เป็น self.__scorecards เช่นกัน
        self.__scorecards[member.user_id].record_score(hole_number, stroke)
        return True

    @property
    def scorecards(self):
        return self.__scorecards
    def get_leaderboard(self):
        from models.leaderboard import Leaderboard # import ภายในถ้าติด Circular Import
        scorecards_list = list(self.scorecards.values())
        
        board = Leaderboard(scorecards_list)
        return board.generate()