from models.score import Scorecard
from models.enum import TournamentStatus
from models.leaderboard import Leaderboard

class MatchGroup:
    def __init__(self, group_number: int, players: list, slot=None):
        # เก็บหมายเลขกลุ่ม (เช่น กลุ่มที่ 1, 2, 3)
        self.__group_number = group_number
        # เก็บ List ของ Object Member ที่อยู่ในกลุ่มนี้
        self.__players = players 
        self.__slot = slot

    @property
    def group_number(self):
        return self.__group_number

    @property
    def slot(self): return self.__slot

    @slot.setter
    def slot(self, data): self.__slot = data

    @property
    def players(self):
        return self.__players

    # ฟังก์ชันเสริมสำหรับแสดงข้อมูล 
    def __str__(self):
        player_names = ", ".join([p.name for p in self.__players])
        return f"Group {self.__group_number}: {player_names}"
    

class Tournament:
    def __init__(self, tour_id, name, date, fee,course):
        self.__id = tour_id
        self.__name = name
        self.__date = date
        self.__entry_fee = fee
        self.__course = course
        self.__status = TournamentStatus.REGISTRATION_OPEN
        self.__registered_players = [] # เก็บออบเจกต์ Member ที่จ่ายเงินแล้ว
        self.__match_bookings = []
        self.__score_cards = []
        self.__reserved_slots = []
    @property
    def id(self): return self.__id
    
    @property
    def name(self): return self.__name

    @property
    def entry_fee(self): return self.__entry_fee

    @property
    def registered_players(self): return self.__registered_players

    @property
    def status(self): return self.__status

    @status.setter
    def status(self, new_status):
        self.__status = new_status

    @property
    def match_bookings(self): return self.__match_bookings
    
    @property
    def course(self): return self.__course
    
    @property
    def date(self): return self.__date
    
    @property
    def score_cards(self): return self.__score_cards

    def set_to_draw_published(self):
        self.__status = TournamentStatus.DRAW_PUBLISHED

    def set_to_completed(self):
        self.__status = TournamentStatus.COMPLETED

    def update_status(self, status):
        self.__status = status

    def add_player(self, member):
        # member คือ Instance ของ Member
        if member not in self.__registered_players:
            self.__registered_players.append(member)           
            
            # 🌟 สร้าง Scorecard instance แล้ว .append() ใส่ List ตรงนี้จบเลย
            new_scorecard = Scorecard(member, self.__course)
            self.__score_cards.append(new_scorecard)
            return True
        return False

    def generate_pairing(self):
        # 🌟 จุดแก้ที่ 3: ยกเลิกการทำ List ซ้อน List เปลี่ยนมาใช้คลาส MatchGroup แทน
        pairings = []
        group_num = 1
        for i in range(0, len(self.registered_players), 4):
            group_players = self.registered_players[i:i+4]
            # สร้าง Instance ของ MatchGroup แล้วเก็บลง List
            pairings.append(MatchGroup(group_num, group_players))
            group_num += 1
        return pairings

    def record_player_score(self, member, hole_number, stroke):
        # 🌟 จุดแก้ที่ 4: เปลี่ยนจากการหาด้วย Key ใน Dict มาเป็นการวนลูปเปรียบเทียบ Instance
        for sc in self.__score_cards:
            if sc.member == member:  # เทียบออบเจกต์ Member ตรงๆ ได้เลย (เจ๋งตรงนี้แหละ OOP)
                sc.record_score(hole_number, stroke)
                return True
        return False

    def get_leaderboard(self):        
        # 🌟 จุดแก้ที่ 5: self.score_cards เป็น List ของ Object อยู่แล้ว ส่งเข้าไปได้เลย!
        board = Leaderboard(self.score_cards) 
        return board.generate()

    
    def get_scorecard_by_member_id(self, member_id):
        """วนลูปหาใบจดคะแนนใน List ตาม ID ของสมาชิก (คืนค่า Instance ของ Scorecard)"""
        for sc in self.__score_cards:
            # สมมติว่า Member ของคุณมี property ชื่อ ID (ถ้าชื่ออื่นเช่น member_id ให้แก้ด้วยนะครับ)
            if sc.member.id == member_id: 
                return sc
        return None