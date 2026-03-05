from enum import Enum

class TournamentStatus(Enum):
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    CLOSED = "CLOSED"
    DRAW_PUBLISHED = "DRAW_PUBLISHED"

class Tournament:
    def __init__(self, tour_id, name, date, fee):
        self.tournamentID = tour_id
        self.name = name
        self.date = date
        self.entryFee = fee
        self.status = TournamentStatus.REGISTRATION_OPEN
        self.registeredPlayers = [] # เก็บออบเจกต์ Member ที่จ่ายเงินแล้ว
        self.matchBookings = []

    def addPlayer(self, member):
        if member not in self.registeredPlayers:
            self.registeredPlayers.append(member)
            return True
        return False

    def updateStatus(self, status):
        self.status = status

    def generatePairing(self):
        # แบ่งกลุ่มละ 4 คนตามรายชื่อที่สมัครมา
        pairings = []
        for i in range(0, len(self.registeredPlayers), 4):
            pairings.append(self.registeredPlayers[i:i+4])
        return pairings