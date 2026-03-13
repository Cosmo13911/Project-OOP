from models.enum import SlotStatus, TournamentStatus
class LeaderboardEntry:
    def __init__(self, rank_no, member_name, handicap, gross_score, net_score, to_par):
        self.__rank_no = rank_no
        self.__member_name = member_name
        self.__handicap = handicap
        self.__gross_score = gross_score
        self.__net_score = net_score
        self.__to_par = to_par

    @property
    def rank_no(self): return self.__rank_no
    
    @rank_no.setter
    def rank_no(self, value): self.__rank_no = value

    @property
    def member_name(self): return self.__member_name

    @property
    def handicap(self): return self.__handicap

    @property
    def gross_score(self): return self.__gross_score

    @property
    def net_score(self): return self.__net_score

    @property
    def to_par(self): return self.__to_par

    def to_dict(self):
        return {
            "rank_no": self.__rank_no,
            "member_name": self.__member_name,
            "handicap": self.__handicap,
            "gross_score": self.__gross_score,
            "net_score": self.__net_score,
            "to_par": self.__to_par
        }
    
class Leaderboard:
    def __init__(self, scorecards):
        self.__score_cards = scorecards

    def generate(self):
        if not self.__score_cards:
            raise ValueError ("Empty score cards")
        
        results = []
        for scorecard in self.__score_cards:
            if scorecard.has_recorded_scores():
                gross = scorecard.get_gross_score()
                cum_par = scorecard.get_cumulative_par()
                to_par_value = gross - cum_par
                
                entry = LeaderboardEntry(
                    rank_no=0,  
                    member_name=scorecard.member.name,
                    handicap=int(round(scorecard.get_course_handicap())),
                    gross_score=gross,
                    net_score=round(scorecard.get_net_score(), 2),
                    to_par=to_par_value
                )
                results.append(entry)

        results.sort(key=lambda x: (x.net_score, x.gross_score))

        # การคำนวณอันดับ (Ranking Logic)
        for i, current_player in enumerate(results):
            if i == 0:
                current_player.rank_no = 1
            else:
                prev_player = results[i - 1]
                if (current_player.net_score == prev_player.net_score and 
                    current_player.gross_score == prev_player.gross_score):
                    current_player.rank_no = prev_player.rank_no
                else:
                    current_player.rank_no = i + 1
        
        return [res.to_dict() for res in results]