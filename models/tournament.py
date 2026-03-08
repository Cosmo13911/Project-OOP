from enum import Enum
from models.score import Scorecard
from models.leaderboard import Leaderboard
class MatchGroup:
    """Class ดูแลความสัมพันธ์ของกลุ่มผู้เล่น (แทนการใช้ List ซ้อน List)"""
    def __init__(self, group_number, players):
        self.__group_number = group_number
        self.__players = players  # เก็บเป็น List ของออบเจกต์ Member (Golfer)

    @property
    def group_number(self):
        return self.__group_number

    @property
    def players(self):
        return self.__players
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
        self.__scorecards = []
        self.__reserved_slots = []
    @property
    def tournamentID(self): return self.__tournamentID
    
    @property
    def name(self): return self.__name

    @property
    def entryFee(self): return self.__entryFee

    @property
    def registeredPlayers(self): return self.__registeredPlayers

    @property
    def status(self): return self.__status
    @status.setter
    def status(self, new_status):
        self.__status = new_status

    @property
    def matchBookings(self): return self.__matchBookings
    
    @property
    def course(self): return self.__course
    
    @property
    def date(self): return self.__date
    
    @property
    def scorecards(self): return self.__scorecards

    def set_to_draw_published(self):
        self.__status = TournamentStatus.DRAW_PUBLISHED

    def set_to_completed(self):
        self.__status = TournamentStatus.COMPLETED

    def updateStatus(self, status):
        self.__status = status

    def addPlayer(self, member):
        # member คือ Instance ของ Member
        if member not in self.__registeredPlayers:
            self.__registeredPlayers.append(member)           
            
            # 🌟 สร้าง Scorecard instance แล้ว .append() ใส่ List ตรงนี้จบเลย
            new_scorecard = Scorecard(member, self.course)
            self.__scorecards.append(new_scorecard)
            return True
        return False

    def generatePairing(self):
        # 🌟 จุดแก้ที่ 3: ยกเลิกการทำ List ซ้อน List เปลี่ยนมาใช้คลาส MatchGroup แทน
        pairings = []
        group_num = 1
        for i in range(0, len(self.registeredPlayers), 4):
            group_players = self.registeredPlayers[i:i+4]
            # สร้าง Instance ของ MatchGroup แล้วเก็บลง List
            pairings.append(MatchGroup(group_num, group_players))
            group_num += 1
        return pairings

    def record_player_score(self, member, hole_number, stroke):
        # 🌟 จุดแก้ที่ 4: เปลี่ยนจากการหาด้วย Key ใน Dict มาเป็นการวนลูปเปรียบเทียบ Instance
        for sc in self.__scorecards:
            if sc.member == member:  # เทียบออบเจกต์ Member ตรงๆ ได้เลย (เจ๋งตรงนี้แหละ OOP)
                sc.record_score(hole_number, stroke)
                return True
        return False

    def get_leaderboard(self):        
        # 🌟 จุดแก้ที่ 5: self.scorecards เป็น List ของ Object อยู่แล้ว ส่งเข้าไปได้เลย!
        board = Leaderboard(self.scorecards) 
        return board.generate()
    def add_scorecard(self, member, course):
        """ให้ทัวร์นาเมนต์เป็นคนจัดการสร้างและเก็บ Scorecard เอง"""
        # สมมติว่ามี self.__scorecards = {} อยู่ใน __init__
        new_scorecard = Scorecard(member, course)
        self.__scorecards[member.id] = new_scorecard
        
    def get_scorecard(self, member_id):
        return self.__scorecards.get(member_id)
        
    def get_all_scorecards(self):
        return list(self.__scorecards.values())
    def get_scorecard_by_member_id(self, member_id):
        """วนลูปหาใบจดคะแนนใน List ตาม ID ของสมาชิก (คืนค่า Instance ของ Scorecard)"""
        for sc in self.__scorecards:
            # สมมติว่า Member ของคุณมี property ชื่อ ID (ถ้าชื่ออื่นเช่น member_id ให้แก้ด้วยนะครับ)
            if sc.member.user_id == member_id: 
                return sc
        return None