from models.score import Scorecard
from models.enum import TournamentStatus
from models.leaderboard import Leaderboard

class MatchGroup:
    def __init__(self, group_number: int, players: list, slot=None):
        # เก็บหมายเลขกลุ่ม (เช่น กลุ่มที่ 1, 2, 3)
        self.__group_number = group_number
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
        self.__registered_players = [] 
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

    
    def update_status(self, new_status):
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

    def add_player(self, member):
        if member not in self.__registered_players:
            self.__registered_players.append(member)           
            
            new_scorecard = Scorecard(member, self.__course)
            self.__score_cards.append(new_scorecard)
            return True
        return False

    def generate_pairing(self):
        pairings = []
        group_num = 1
        for i in range(0, len(self.registered_players), 4):
            group_players = self.registered_players[i:i+4]
            pairings.append(MatchGroup(group_num, group_players))
            group_num += 1
        return pairings

    def record_player_score(self, member, hole_number, stroke):
        for sc in self.__score_cards:
            if sc.member == member:  
                sc.record_score(hole_number, stroke)
                return True
        return False

    def get_leaderboard(self):        
        board = Leaderboard(self.score_cards) 
        return board.generate()

    
    def get_scorecard_by_member_id(self, member_id):
        """วนลูปหาใบจดคะแนนใน List ตาม ID ของสมาชิก (คืนค่า Instance ของ Scorecard)"""
        for sc in self.__score_cards:
            if sc.member.id == member_id: 
                return sc
        return None