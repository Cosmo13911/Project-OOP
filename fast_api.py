from fastapi import FastAPI, HTTPException, Body, Form, Query
from system import GreenValleySystem
from models.enum import TournamentStatus

app = FastAPI(
    title="Green Valley Management System",
    description="ระบบจัดการสนามกอล์ฟและทัวร์นาเมนต์",
    version="1.0.0",
)

sys = GreenValleySystem()
sys.create_data()

# ==========================================
# หมวด User & Ordering
# ==========================================

@app.get("/view/booking", tags=["User"])
def view_bookings(booking_id: str = "BK-001"):
    if len(sys.bookings) == 0:
        return {"message": "No bookings found"}

    booking = sys.find_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    orders_list = []
    if booking.orders:
        orders_list = [{"net_total": order.calculate_net_total()} for order in booking.orders]
        
    return {
        "id": booking.booking_id,
        "requester": booking.requester.name,
        "orders": orders_list
    }

@app.get("/view/product", tags=["User"])
def view_products():
    # เรียกใช้ p.id, p.name, p.price แบบ property (ไม่มี ())
    products_list = [
        {"id": p.id, "name": p.name, "price": p.price, "remaining_stock": p.stock} 
        for p in sys.products
    ]
    return {"products": products_list}

@app.post("/place_order", tags=["User"])
def place_order(
    booking_id: str = Query("BK-001"),
    product_id: str = Query("P001"),
    quantity: int = Query(2)
):
    result = sys.place_order(booking_id, product_id, quantity)
    if "Error" in result:
        raise HTTPException(status_code=400, detail=result)
    return {"message": result}

@app.post("/user/booking/create", tags=["User"])
def create_booking(
    member_id: str = Query("M-001"),
    course_id: str = Query("C-001"),
    date: str = Query("2026-03-10"),
    time: str = Query("08:00"),
    companions: list[str] = Query(None) # ส่งเป็นก๊วนได้
):
    try:
        # เรียกใช้ Method ที่เราแก้ให้จำกัด 4 คนและล็อก Slot ทันที
        new_booking = sys.create_booking(member_id, course_id, date, time, companions)
        return {
            "message": "Booking successful",
            "booking_id": new_booking.booking_id,
            "status": new_booking.status
        }
    except ValueError as e:
        # ดักจับ Error "สนามเต็ม" หรือ "หาไม่เจอ" แล้วส่ง 400 กลับไปสวยๆ
        raise HTTPException(status_code=400, detail=str(e))
    

@app.get("/view/slots", tags=["User"])
def view_available_slots(course_id: str = "C-001", date: str = "2026-03-10"):
    course = sys.find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # เรียกใช้ method ใน Course ที่เราเขียนไว้
    slots = course.get_available_slots(date)
    return {
        "course": course.name,
        "date": date,
        "available_slots": [{"time": s.time, "status": s.status.value} for s in slots]
    }

# ==========================================
# หมวด Course Information
# ==========================================

@app.get("/view/courses", tags=["Course Information"])
def view_all_courses():
    """แสดงรายชื่อสนามทั้งหมด พร้อมเรทราคาและความยาก (Rating/Slope)"""
    if not sys.get_all_courses:
        return {"message": "No courses found in the system"}

    course_data = []
    for c in sys.get_all_courses:
        course_data.append({
            "course_id": c.id,
            "name": c.name,
            "type": c.type,
            "pricing": {
                "morning": f"{c.fee_morning} THB",
                "afternoon": f"{c.fee_afternoon} THB"
            },
            "difficulty_metrics": {
                "course_rating": c.rating,
                "slope_rating": c.slope_rating,
                "level": c.get_difficulty
            },
            "total_par": c.par # เรียกใช้ Property par ที่คุณมีอยู่แล้ว
        })

    return {
        "total_courses": len(course_data),
        "courses": course_data
    }

# ==========================================
# หมวด Tournament (User)
# ==========================================

@app.get("/user/tournaments", tags=["User"])
def view_all_tournaments():
    if len(sys.tournaments) == 0:
        return {"message": "No tournaments available right now."}
    
    t_list = [{
        "id": t.id,
        "name": t.name,
        "date": t.date,
        "entry_fee": t.entry_fee,
        "status": t.status.value,
        "registered_count": len(t.registered_players)
    } for t in sys.tournaments]
    return {"tournaments": t_list}

@app.post("/user/tournament/register", tags=["User"])
def register_tournament(member_id: str = "M-001", tour_id: str = "T-001"):
    try:
        result = sys.register_tournament_get_payment(member_id, tour_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/user/tournament/pay", tags=["User"])
def process_payment(payment_id: str = "PAY-M-001-T-001"):
    try:
        result = sys.process_payment(payment_id)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/user/notifications", tags=["User"])
def view_user_notifications(member_id: str = "M-001"):
    try:
        member = sys.find_user(member_id)
        notifications = member.get_notifications
    
    # แปลง List ของ Object เป็น List ของ Dictionary เพื่อให้ JSON อ่านได้
        return {
            "member_name": member.name, 
            "total_notifications": len(notifications),
            "notifications": [
                {
                    "message": n.message, 
                    "timestamp": n.timestamp, 
                } for n in notifications
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ==========================================
# หมวด Tournament (Admin)
# ==========================================

@app.post("/admin/tournament/create", tags=["Admin"])
def admin_create_tournament(
    name: str = "Green Valley Masters", 
    date: str = "2026-12-01", 
    fee: float = 2500.0,
    course_id: str = "C-001"
):
    try:
        result = sys.create_tournament(name, date, fee, course_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/tournament/close_and_pair", tags=["Admin"])
def admin_close_registration_and_pair(tour_id: str = "T-001"):
    try:
        result = sys.close_registration_and_pairing(tour_id)
        return {"message": result, "status": "Draw Published"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# หมวด Tournament (Scoring & Leaderboard)
# ==========================================

@app.post("/admin/tournament/start", tags=["Admin"])
def admin_start_tournament(tour_id: str = "T-001"):
    """สมมติว่าถึงวันแข่ง Admin กดเริ่มการแข่งขัน"""
    try:
        tour = sys.find_tournament(tour_id)
        tour.update_status(TournamentStatus.IN_PROGRESS) # นำเข้า TournamentStatus ด้วยนะ
        return {"message": "Tournament has started!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/user/tournament/score", tags=["User"])
def record_score(
    tour_id: str = Query("T-001"), 
    member_id: str = Query("M-001"), 
    hole_number: int = Query(1), 
    stroke: int = Query(4)
):
    """นักกอล์ฟจดคะแนนตัวเองแต่ละหลุม"""
    try:
        result = sys.record_tournament_score(tour_id, member_id, hole_number, stroke)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Unexpected error occurred")

@app.get("/view/leaderboard", tags=["User"])
def view_leaderboard(tour_id: str = "T-001"):
    """ดูตารางสรุปคะแนน"""
    try:
        result = sys.get_tournament_leaderboard(tour_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/admin/tournament/end", tags=["Admin"])
def admin_end_tournament(tour_id: str = "T-001"):
    """[สำหรับแอดมิน] ปิดการแข่งขัน, คำนวณแต้มต่อ (Handicap) ใหม่ให้ผู้เล่นทุกคน และอัปเดตประวัติ"""
    try:
        result = sys.end_tournament(tour_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))