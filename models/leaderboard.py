class Leaderboard:
    def __init__(self, scorecards):
        self.__scorecards = scorecards 

    def generate(self):
        if self.__scorecards==None:
            return "Empty scorecards"
        results = []
        for scorecard in self.__scorecards:
            if scorecard.has_recorded_scores(): 
                gross = scorecard.get_gross_score()
                cum_par = scorecard.get_cumulative_par()
                to_par_value = gross - cum_par # เช่น ตี 4 ในหลุมพาร์ 4 -> 4 - 4 = 0
                
                results.append({
                    "member_name": scorecard.member.name,
                    "handicap": int(round(scorecard.get_course_handicap())), 
                    "gross_score": gross,
                    "net_score": round(scorecard.get_net_score(), 2), 
                    "to_par": to_par_value # โชว์เป็น 0, -1 (Birdie), +1 (Bogey)
                })

        results.sort(key=lambda x: (x["net_score"], x["gross_score"]))
        for i, player_data in enumerate(results):
            if i == 0:
                player_data["rank_no"] = 1
            else:
                prev_player = results[i - 1]
                if (player_data["net_score"] == prev_player["net_score"] and 
                    player_data["gross_score"] == prev_player["gross_score"]):
                    player_data["rank_no"] = prev_player["rank_no"]
                else:
                    player_data["rank_no"] = i + 1
            
        return results