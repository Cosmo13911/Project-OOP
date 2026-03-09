from fastmcp import FastMCP
from system import GreenValleySystem
from models.enum import TournamentStatus

# 1. สร้าง MCP Server
mcp = FastMCP("GreenValleyMCP")

# 2. จำลองระบบและฐานข้อมูล
sys = GreenValleySystem()
sys.create_data()

# ==========================================
# หมวด User & Ordering (Booking & Products)
# ==========================================
@mcp.tool()
def view_bookings(booking_id: str = "BK-001"):
    """ใช้ดูข้อมูลการจองปัจจุบัน และรายการสินค้าที่สั่งไว้ในบิลนั้น"""
    try:
        booking = sys.find_booking(booking_id)
        if not booking:
            return {"error": f"ไม่พบการจองรหัส {booking_id}"}

        orders_list = []
        if booking.orders:
            orders_list = [{"net_total": order.calculate_net_total()} for order in booking.orders]
            
        return {
            "id": booking.booking_id,
            "requester": booking.requester.name,
            "orders": orders_list
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_products():
    """ใช้ดูรายการสินค้าทั้งหมดในระบบ พร้อมราคาและสต็อกที่เหลือ"""
    try:
        if not sys.products:
            return {"message": "ไม่มีสินค้าในระบบ"}

        products_list = [
            {
                "id": p.id, 
                "name": p.name, 
                "price": p.price, 
                "remaining_stock": p.stock # แก้ให้ตรงตาม Model
            } 
            for p in sys.products
        ]
        return {"products": products_list}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def place_order(booking_id: str, product_id: str, quantity: int):
    """ใช้สั่งซื้อสินค้าเข้าไปในรายการจอง"""
    try:
        result = sys.place_order(booking_id, product_id, quantity)
        return {"message": result}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_golf_booking(member_id: str, course_id: str, date: str, time: str, companions: list[str] = None):
    """ใช้จองเวลาออกรอบสนามกอล์ฟ"""
    try:
        new_booking = sys.create_booking(member_id, course_id, date, time, companions)
        return {
            "message": "Booking successful",
            "booking_id": new_booking.booking_id,
            "status": new_booking.status.value
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_available_slots(course_id: str, date: str):
    """ใช้ตรวจสอบเวลาที่ยังว่างอยู่ของสนามในวันที่ระบุ"""
    try:
        course = sys.find_course(course_id)
        if not course:
            return {"error": "ไม่พบสนามที่ระบุ"}
        
        slots = course.get_available_slots(date)
        return {
            "course": course.name,
            "date": date,
            "available_slots": [{"time": s.time, "status": s.status.value} for s in slots]
        }
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# หมวด Course Information
# ==========================================

@mcp.tool()
def view_all_courses():
    """แสดงรายชื่อสนามกอล์ฟทั้งหมด พร้อมราคาและความยาก"""
    try:
        if not sys.get_all_courses:
            return {"message": "No courses found."}

        course_data = []
        for c in sys.get_all_courses:
            course_data.append({
                "id": c.id,
                "name": c.name,
                "pricing": {"morning": c.fee_morning, "afternoon": c.fee_afternoon},
                "difficulty": {
                    "rating": c.rating,
                    "slope": c.slope_rating,
                    "level": c.get_difficulty
                },
                "par": c.par
            })
        return {"courses": course_data}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# หมวด Tournament (User)
# ==========================================

@mcp.tool()
def view_tournaments():
    """ดูรายการแข่งขัน ทั้งหมดที่มีในระบบ"""
    try:
        if len(sys.tournaments) == 0:
            return {"message": "No tournaments available."}
        
        t_list = [{
            "id": t.id,
            "name": t.name,
            "date": t.date,
            "status": t.status.value,
            "registered": len(t.registered_players) # แก้ให้ตรงตาม Model
        } for t in sys.tournaments]
        return {"tournaments": t_list}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def register_tournament(member_id: str, tour_id: str):
    """สมัครเข้าแข่งขันในทัวร์นาเมนต์"""
    try:
        result = sys.register_tournament_get_payment(member_id, tour_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def process_tournament_payment(payment_id: str):
    """ชำระเงินค่าสมัครทัวร์นาเมนต์"""
    try:
        result = sys.process_payment(payment_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_my_notifications(member_id: str):
    """ดูการแจ้งเตือนส่วนตัวของสมาชิก"""
    try:
        member = sys.find_user(member_id)
        if not member: return {"error": "Member not found"}
        notifications = member.get_notifications
        
        return {
            "member": member.name,
            "notifications": [{"msg": n.message, "at": n.timestamp} for n in notifications]
        }
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# หมวด Admin (Tournament Management)
# ==========================================

@mcp.tool()
def admin_create_tournament(name: str, date: str, fee: float, course_id: str):
    """[Admin Only] สร้างงานแข่งทัวร์นาเมนต์ใหม่"""
    try:
        result = sys.create_tournament(name, date, fee, course_id)
        return {"message": "Tournament created successfully", "details": result}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def admin_start_tournament(tour_id: str):
    """[Admin Only] เริ่มการแข่งขัน"""
    try:
        tour = sys.find_tournament(tour_id)
        if not tour: return {"error": "Tournament not found"}
        tour.update_status(TournamentStatus.IN_PROGRESS)
        return {"message": f"Success: งานแข่ง {tour.name} เริ่มขึ้นแล้ว!"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def admin_end_tournament(tour_id: str):
    """[Admin Only] ปิดงานแข่ง และคำนวณ Handicap ใหม่"""
    try:
        result = sys.end_tournament(tour_id)
        return result
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# หมวด Scoring & Leaderboard
# ==========================================

@mcp.tool()
def record_tournament_score(tour_id: str, member_id: str, hole: int, stroke: int):
    """บันทึกคะแนนการตี"""
    try:
        result = sys.record_tournament_score(tour_id, member_id, hole, stroke)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_leaderboard(tour_id: str):
    """ดูตารางคะแนนล่าสุด"""
    try:
        result = sys.get_tournament_leaderboard(tour_id)
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()