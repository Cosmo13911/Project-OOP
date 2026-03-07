class Leaderboard:
    def __init__(self, scorecards_list):
        # รับค่ามาเก็บเป็น Private และบังคับครอบด้วย list() เพื่อตัดขาดจากภายนอก
        self.__scorecards = list(scorecards_list) if scorecards_list else []

    def generate(self):
        if not self.__scorecards:
            return [] # 🌟 แนะนำให้คืนค่าเป็น List ว่าง แทน String เพื่อให้หน้าเว็บพ่น 0 คนได้โดยไม่พัง
            
        results = []
        for scorecard in self.__scorecards:
            # ใช้ Public Method/Property ของ Scorecard ตามหลักเป๊ะๆ
            if scorecard.has_recorded_scores(): 
                score_to_use = scorecard.get_adjusted_score() 
                cum_par = scorecard.get_cumulative_par()
                to_par_value = score_to_use - cum_par
                
                # 🌟 3. จัด Format ของ To Par ให้สวยงามแบบสากล
                if to_par_value == 0:
                    to_par_display = "E"
                elif to_par_value > 0:
                    to_par_display = f"+{to_par_value}"
                else:
                    to_par_display = str(to_par_value)

                results.append({
                    "member_name": scorecard.member.name,
                    "handicap": int(round(scorecard.get_course_handicap())), 
                    "gross_score": scorecard.get_gross_score(), # โชว์คะแนนดิบให้คนดูรู้
                    "adjusted_score": score_to_use, # โชว์คะแนนที่ตัด Double Par แล้ว
                    "net_score": round(scorecard.get_net_score(), 2), 
                    "to_par": to_par_display,
                    # 🌟 4. เพิ่ม Thru ว่าเล่นไปกี่หลุมแล้ว (นับจากจำนวน key ในดิกชันนารีคะแนน)
                    "thru": len(scorecard.scores) 
                })

        # จัดเรียง: เทียบ Net Score ก่อน ถ้าเท่ากัน ดูคะแนนที่เล่นได้ (น้อยกว่าแปลว่าเก่งกว่า)
        results.sort(key=lambda x: (x["net_score"], x["adjusted_score"]))
        
        # ระบบ Rank Tie-break (โค้ดเดิมของคุณ ดีเยี่ยมอยู่แล้วครับ)
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