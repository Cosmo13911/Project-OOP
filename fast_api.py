from fastapi import FastAPI, HTTPException # เพิ่ม HTTPException เข้ามา
from system import GreenValleySystem

app = FastAPI(
    title="Green Valley Management System", # เปลี่ยนชื่อโปรเจกต์ตรงนี้
    description="ระบบจัดการสนามกอล์ฟและการสั่งอาหารสำหรับสมาชิก", # คำอธิบายระบบ
    version="1.0.0", # เวอร์ชันของ API
)

sys = GreenValleySystem()
sys.create_data()
john = sys.users[0]             # ดึงออบเจกต์ Member (John Doe)

print("\n" + "="*40)

# ------------ User ---------------------
@app.get("/view/booking", tags=["User"])
def view_bookings():
    # 1. เช็คก่อนว่ามีข้อมูลไหม เพื่อกัน IndexError
    if len(sys.bookings) == 0:
        return {"bookings": "Empty"}

    # 2. ดึงข้อมูลตัวแรก
    booking = sys.bookings[0]

    # 3. ส่งกลับเป็น Dictionary (FastAPI จะแปลงเป็น JSON ให้เอง)
    # ห้าม return ออบเจกต์ตรงๆ ให้ดึง attribute ออกมาแบบนี้ครับ
    return {
        "id": booking.booking_id,
        "requester": booking.requester.name, # สมมติว่า requester คือออบเจกต์ Member
        "orders": booking.view_orders , # นี่จะได้เป็นลิสต์ของ Order ออบเจกต์
    }

@app.get("/view/product", tags=["User"])
def view_products():
    products_list = []

    for product in sys.products:
        data = {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }

        products_list.append(data)
    
    return {"products": products_list}


@app.post("/order", tags=["User"])
def place_order(booking_id: str, product_id: str, quantity: int):
    product = sys.find_product_by_id(product_id)
    if not product:
        return {"error": "Product not found."}
    john.place_order(sys, booking_id, product, quantity)
    return {"message": "Order placed successfully."}

# ==========================================
# หมวด User (รวมฟังก์ชันของนักกอล์ฟทั้งหมด)
# ==========================================

@app.get("/user/tournaments", tags=["User"])
def view_all_tournaments():
    """User: ดูรายการแข่งขันที่เปิดรับสมัครทั้งหมด"""
    if len(sys.tournaments) == 0:
        return {"message": "No tournaments available right now."}
    
    t_list = []
    for t in sys.tournaments:
        t_list.append({
            "id": t.tournamentID,
            "name": t.name,
            "date": t.date,
            "entry_fee": t.entryFee,
            "status": t.status.value,
            "registered_count": len(t.registeredPlayers)
        })
    return {"tournaments": t_list}

@app.post("/user/tournament/register", tags=["User"])
def register_tournament(member_id: str = "M-001", tour_id: str = "T-001"):
    """User (Phase 1): สมัครเข้าร่วมแข่งขันและรับบิลชำระเงิน"""
    # 1. รับค่าที่ระบบส่งกลับมาเก็บไว้ในตัวแปร result ก่อน
    result = sys.register_tournament_get_payment(member_id, tour_id)

    # 2. เช็คว่ามีคำว่า "error" ในผลลัพธ์ไหม
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    # 3. ถ้าไม่มี Error ค่อย return ผลลัพธ์กลับไปให้ User
    return result

@app.post("/user/tournament/pay", tags=["User"])
def process_payment(payment_id: str = "PAY-001"):
    """User (Phase 1): ชำระเงินและยืนยันการเข้าร่วม"""
    # ทำแบบเดียวกันกับฟังก์ชันจ่ายเงินด้วยครับ
    result = sys.process_payment(payment_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return result

@app.get("/user/notifications", tags=["User"])
def view_user_notifications(member_id: str = "M-001"):
    """User: เช็คกล่องข้อความแจ้งเตือนของตัวเองผ่าน Member ID"""
    
    # 1. ค้นหาตัวตนของผู้ใช้ในระบบ
    member = sys.find_user_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # 2. เรียกใช้เมธอด view_notifications() ตามที่ออกแบบไว้ใน Class Diagram
    notifications = member.view_notifications()
    
    # 3. ตรวจสอบว่ามีแจ้งเตือนหรือไม่
    if not notifications:
        return {"member_name": member.name, "message": "You have no new notifications."}
    
    # 4. ส่งรายการแจ้งเตือนทั้งหมดกลับไปให้แสดงผลบนหน้าจอ UI
    return {
        "member_name": member.name, 
        "total_notifications": len(notifications),
        "notifications": notifications
    }

# ==========================================
# หมวด Admin (ฝั่งเจ้าหน้าที่ระบบ)
# ==========================================

@app.post("/admin/tournament/create", tags=["Admin"])
def admin_create_tournament(name: str = "Green Valley Masters", date: str = "2024-12-01", fee: float = 2500.,course_id: str = "C-001"):
    """Admin (Phase 0): สร้างรายการแข่งขันใหม่"""
    t_id = sys.create_tournament(name, date, fee, course_id)
    if "error" in str(t_id).lower():
        raise HTTPException(status_code=400, detail=t_id)
    return {"message": "Tournament created successfully", "tournamentID": t_id}

@app.get("/admin/tournament/players", tags=["Admin"])
def admin_view_tournament_players(tour_id: str = "T-001"):
    """Admin: ตรวจสอบจำนวนและรายชื่อผู้ที่สมัครเข้าแข่งขัน (กรอก Tournament ID)"""
    result = sys.get_tournament_players(tour_id)
    
    # ถ้าพิมพ์รหัส Tournament ผิด ให้เด้ง Error 404
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return result

@app.post("/admin/tournament/close_and_pair", tags=["Admin"])
def admin_close_registration_and_pair(tour_id: str = "T-001"):
    """Admin (Phase 2): ปิดรับสมัคร จัดก๊วนอัตโนมัติ สร้าง Booking และส่งแจ้งเตือน"""
    result = sys.close_registration_and_pairing(tour_id)
    
    if "Error" in result or "not found" in result:
        raise HTTPException(status_code=400, detail=result)
        
    return {"message": result, "status": "Draw Published & Notifications Sent"}
# 🏆 สำหรับ Tournament: เรียก record_tournament_score
@app.post("/admin/record_score/tournament", tags=["Admin"])
def admin_record_tournament_score(
    tour_id: str = "T-001", 
    member_id: str = "M-001", 
    hole1: int = 0, hole2: int = 0, hole3: int = 0, hole4: int = 0, hole5: int = 0, hole6: int = 0,
    hole7: int = 0, hole8: int = 0, hole9: int = 0, hole10: int = 0, hole11: int = 0, hole12: int = 0,
    hole13: int = 0, hole14: int = 0, hole15: int = 0, hole16: int = 0, hole17: int = 0, hole18: int = 0
):
    scores_input = {
        1: hole1, 2: hole2, 3: hole3, 4: hole4, 5: hole5, 6: hole6,
        7: hole7, 8: hole8, 9: hole9, 10: hole10, 11: hole11, 12: hole12,
        13: hole13, 14: hole14, 15: hole15, 16: hole16, 17: hole17, 18: hole18
    }
    # 🌟 เรียกฟังก์ชันสำหรับทัวร์นาเมนต์โดยเฉพาะ
    result = sys.record_tournament_score(tour_id, member_id, scores_input)
    
    if isinstance(result, str) and result.startswith("Error"): 
        raise HTTPException(status_code=400, detail=result)
    return result

# 🌲 สำหรับ General Play: เรียก record_general_play
@app.post("/admin/record_score/general", tags=["Admin"])
def admin_record_general_score(
    course_id: str = "C-001", 
    member_id: str = "M-001", 
    hole1: int = 0, hole2: int = 0, hole3: int = 0, hole4: int = 0, hole5: int = 0, hole6: int = 0,
    hole7: int = 0, hole8: int = 0, hole9: int = 0, hole10: int = 0, hole11: int = 0, hole12: int = 0,
    hole13: int = 0, hole14: int = 0, hole15: int = 0, hole16: int = 0, hole17: int = 0, hole18: int = 0
):
    scores_input = {
        1: hole1, 2: hole2, 3: hole3, 4: hole4, 5: hole5, 6: hole6,
        7: hole7, 8: hole8, 9: hole9, 10: hole10, 11: hole11, 12: hole12,
        13: hole13, 14: hole14, 15: hole15, 16: hole16, 17: hole17, 18: hole18
    }
    # 🌟 เรียกฟังก์ชันสำหรับการเล่นทั่วไปโดยเฉพาะ
    result = sys.record_general_play(member_id, course_id, scores_input)
    
    if isinstance(result, str) and result.startswith("Error"): 
        raise HTTPException(status_code=400, detail=result)
    return result
@app.get("/admin/tournament/leaderboard", tags=["User", "Admin"])
def view_tournament_leaderboard(tour_id: str = "T-001"):
    """User/Admin: ดูตารางผู้นำ (Leaderboard) แบบ Real-time หักลบแต้มต่อ (Handicap) แล้ว"""
    
    try:
        result = sys.get_tournament_leaderboard(tour_id)
        
        # 2. เช็คว่าหลังบ้านส่ง Error กลับมาไหม
        if isinstance(result, str):
            # ถ้าเป็นข้อความ (String) แปลว่าหาไม่เจอ
            raise HTTPException(status_code=404, detail=result)
            
        # 3. ส่งข้อมูลกลับให้หน้าเว็บสวยๆ
        return result
    except Exception as e:
        # ดักจับ Error เผื่อคลาส Leaderboard ของคุณพังหรือมีปัญหา
        raise HTTPException(status_code=500, detail=f"Error generating leaderboard: {str(e)}")
@app.post("/admin/tournament/end", tags=["Admin"])
def admin_end_tournament(tour_id: str = "T-001"):
    result = sys.end_tournament(tour_id)
    
    if isinstance(result, str) and result.startswith("Error"):
        raise HTTPException(status_code=400, detail=result)
        
    return {"message": result, "status": "COMPLETED"}