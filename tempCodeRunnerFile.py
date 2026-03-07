@app.post("/admin/tournament/score", tags=["Admin"])
def record_player_score(
    tour_id: str = "T-001", 
    member_id: str = "M-001", 
    hole_number: int = 1, 
    stroke: int = 4
):
    """Admin: กรอกคะแนนให้ผู้เล่นในทัวร์นาเมนต์ (ระบบจะคำนวณ Double Par ให้อัตโนมัติ)"""
    
    # 1. ค้นหาทัวร์นาเมนต์
    target_tour = None
    for t in sys.tournaments:
        if t.tournamentID == tour_id:
            target_tour = t
            break
            
    if not target_tour:
        raise HTTPException(status_code=404, detail="Tournament not found")

    # 2. ค้นหาผู้เล่น
    target_member = sys.find_user_by_id(member_id)
    if not target_member:
        raise HTTPException(status_code=404, detail="Member not found")

    # 3. บันทึกคะแนน (ใช้ฟังก์ชันจากคลาส Tournament ที่เราทำไว้)
    success = target_tour.add_tournament_score_per_player_per_hole(target_member, hole_number, stroke)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to record score. Player might not be registered or hole is invalid.")
        
    return {
        "message": f"Score recorded successfully for {target_member.name}",
        "hole": hole_number,
        "input_stroke": stroke
    }

@app.get("/tournament/leaderboard", tags=["User", "Admin"])
def view_tournament_leaderboard(tour_id: str = "T-001"):
    """User/Admin: ดูตารางผู้นำ (Leaderboard) แบบ Real-time หักลบแต้มต่อ (Handicap) แล้ว"""
    
    # 1. ค้นหาทัวร์นาเมนต์
    target_tour = None
    for t in sys.tournaments:
        if t.tournamentID == tour_id:
            target_tour = t
            break
            
    if not target_tour:
        raise HTTPException(status_code=404, detail="Tournament not found")

    # 2. ดึงข้อมูล Leaderboard (จากคลาส Tournament ของเรา)
    try:
        board_data = target_tour.get_leaderboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating leaderboard: {str(e)}")

    # 3. ตรวจสอบว่ามีคนมีคะแนนหรือยัง
    if not board_data:
        return {"message": "No scores recorded yet.", "tournament": target_tour.name}

    return {
        "tournament_name": target_tour.name,
        "total_players": len(target_tour.registeredPlayers),
        "leaderboard": board_data
    }