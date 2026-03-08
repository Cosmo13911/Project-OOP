class Leaderboard:
    def __init__(self, scorecards_list):
        self.__scorecards = list(scorecards_list) if scorecards_list else []

    def generate(self):
        if not self.__scorecards:
            return [] 
            
        results = []
        for scorecard in self.__scorecards:
            if scorecard.has_recorded_scores(): 
                score_to_use = scorecard.get_adjusted_score() 
                cum_par = scorecard.get_cumulative_par()
                to_par_value = score_to_use - cum_par
                
                if to_par_value == 0:
                    to_par_display = "E"
                elif to_par_value > 0:
                    to_par_display = f"+{to_par_value}"
                else:
                    to_par_display = str(to_par_value)

                results.append({
                    "member_name": scorecard.member.name,
                    "handicap": int(round(scorecard.get_course_handicap())), 
                    "gross_score": scorecard.get_gross_score(), 
                    "adjusted_score": score_to_use, 
                    "net_score": round(scorecard.get_net_score(), 2), 
                    "to_par": to_par_display,
                    "thru": scorecard.get_holes_played() 
                })

        results.sort(key=lambda x: (x["net_score"], x["adjusted_score"]))
        
        for i, player_data in enumerate(results):
            if i == 0:
                player_data["rank_no"] = 1
            else:
                prev_player = results[i - 1]
                if (player_data["net_score"] == prev_player["net_score"] and 
                    player_data["adjusted_score"] == prev_player["adjusted_score"]):
                    player_data["rank_no"] = prev_player["rank_no"]
                else:
                    player_data["rank_no"] = i + 1
            
        return results