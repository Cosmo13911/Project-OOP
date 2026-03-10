from fastmcp import FastMCP
from system import GreenValleySystem
from models.enum import TournamentStatus, SlotStatus 
from models.booking import Booking
from models.payment import Payment, Raincheck
from models.enum import Tier, Booking_day_limit
from models.users import Member, Guest
from typing import List, Optional
from datetime import datetime

# 1. Initialize MCP Server
mcp = FastMCP("GreenValleyMCP")

# 2. Initialize System and Mock Data
sys = GreenValleySystem()
sys.create_data()

# ==========================================
# หมวด User & Ordering (Booking & Products)
# ==========================================

@mcp.tool()
def view_bookings(booking_id: str = "BK-001"):
    """ใช้ดูข้อมูลการจองปัจจุบัน และรายการสินค้าที่สั่งไว้ในบิลนั้น"""
    try:
        if not sys.bookings:
            return {"message": "No bookings found"}
            
        booking = sys.find_booking(booking_id)
        if not booking:
            return {"error": "Booking not found"}

        # ดึงรายการ order และคำนวณยอดสุทธิ (เรียกใช้ property calculate_net_total)
        orders_list = [
            {"order_id": order.id, "net_total": order.calculate_net_total} 
            for order in booking.orders
        ]
            
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
        # เรียกใช้ p.id, p.name, p.price แบบ property ตาม system.py
        products_list = [
            {"id": p.id, "name": p.name, "price": p.price, "remaining_stock": p.stock} 
            for p in sys.products
        ]
        return {"products": products_list}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def place_order(booking_id: str, product_id: str, quantity: int):
    """ใช้สั่งซื้อสินค้าเข้าไปในรายการจอง (หักสต็อกอัตโนมัติ)"""
    try:
        # เรียกใช้ logic การสั่งซื้อจาก system.py
        result = sys.place_order(booking_id, product_id, quantity)
        return {"message": result}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_golf_booking(member_id: str, course_id: str, date: str, time: str, companions: list[str] = None):
    """ใช้จองเวลาออกรอบสนามกอล์ฟ (รองรับเพื่อนร่วมก๊วน และล็อก Slot ทันที)"""
    try:
        # เรียกใช้ create_booking ที่มีการจำกัด 4 คนและล็อก Slot
        new_booking = sys.create_booking(member_id, course_id, date, time, companions)
        return {
            "message": "Booking successful",
            "booking_id": new_booking.booking_id,
            "status": new_booking.status.value
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def select_booking_addons(
    booking_id: str,
    specific_caddies: List[str],
    random_caddy_level: Optional[str],
    random_caddy_count: int,
    cart_type: Optional[str] ,cart_count: int
) -> str:
    """
    เครื่องมือสำหรับจัดการ Add-ons (แคดดี้และรถกอล์ฟ) ให้กับการจองที่ระบุ 
    พร้อมตรวจสอบกฎธุรกิจ 1 ผู้เล่นต่อ 1 แคดดี้ และสถานะว่างของทรัพยากร
    """
    try:
        # 1. การตรวจสอบความถูกต้องเบื้องต้น (Input Validation)
        booking = sys.find_booking(booking_id)
        if not booking:
            raise ValueError(f"Error: ไม่พบข้อมูลการจองรหัส {booking_id}")

        # 2. ตรวจสอบสิทธิ์ (Business Rule: Guest ห้ามระบุแคดดี้)
        if isinstance(booking.requester, Guest) and len(specific_caddies) > 0:
            raise ValueError ("Error: ลูกค้าทั่วไป (Guest) ไม่สามารถระบุตัวแคดดี้ได้ ต้องใช้ระบบสุ่มเท่านั้น")

        # 3. ตรวจสอบกฎเหล็ก 1:1 (Business Rule Validation)
        total_golfers = len(booking.golfers)
        total_requested_caddies = len(specific_caddies) + random_caddy_count
        
        if total_requested_caddies != total_golfers:
            raise ValueError (f"Error: จำนวนแคดดี้ไม่ถูกต้อง ก๊วนนี้มี {total_golfers} คน ต้องจองแคดดี้ให้ครบ {total_golfers} ท่าน")

        # 4. ล้างค่าเดิมก่อนเริ่มการจองใหม่ (Encapsulation Principle)
        booking.clear_addons()

        raw_date = booking.get_slot.get_play_date 
        time = booking.get_slot.get_time

        # 2. แปลงจาก YYYY-MM-DD เป็น DD-MM-YYYY สำหรับ Add-ons Module
        # เพื่อให้ Module อื่นๆ นำไปใช้งานได้ตาม format ที่คาดหวัง
        try:
            date_obj = datetime.strptime(raw_date, "%Y-%m-%d")
            date = date_obj.strftime("%d-%m-%Y")
        except ValueError as e:
            # เพิ่ม Error Handling ตามเกณฑ์ [cite: 19, 20]
            return f"System Error: รูปแบบวันที่ในระบบไม่ถูกต้อง - {str(e)}"
        
        assigned_details = []
        # date, time = booking.slot.play_date, booking.slot.time
        available_caddies = sys.find_available_caddies(date, time)
        available_carts = sys.find_available_carts(date, time)
        if not available_caddies and total_requested_caddies :
            raise ValueError("Error: No caddies available for the selected time slot or No carts available for the selected time slot")

        # 5. การจัดการระบุแคดดี้ (Specific Assignment)
        for idx, c_id in enumerate(specific_caddies):
            golfer = booking.golfers[idx]
            caddy = next((c for c in available_caddies if c.id == c_id), None)
            if not caddy:
                raise ValueError (f"Error: แคดดี้รหัส {c_id} ไม่ว่างหรือไม่มีข้อมูล")
            
            # Polymorphism & Association
            booking.assign_caddy(golfer.user_id, caddy)
            caddy.assign_to_schedule(booking)
            available_caddies.remove(caddy)
            assigned_details.append(f"{golfer.name} -> แคดดี้: {caddy.name}")

        # 6. การจัดการสุ่มแคดดี้ (Random Assignment)
        start_idx = len(specific_caddies)
        if random_caddy_level and random_caddy_count > 0:
            for i in range(random_caddy_count):
                golfer = booking.golfers[start_idx + i]
                # กรองระดับแคดดี้
                caddy = next((c for c in available_caddies if c.level.value == random_caddy_level), None)
                if not caddy:
                    raise ValueError  (f"Error: แคดดี้ระดับ {random_caddy_level} ว่างไม่เพียงพอ")
                
                booking.assign_caddy(golfer.user_id, caddy)
                caddy.assign_to_schedule(booking)
                available_caddies.remove(caddy)
                assigned_details.append(f"{golfer.name} -> แคดดี้: {caddy.name} (สุ่ม)")

        # 7. การจัดการรถกอล์ฟ (Resource Management)
        if cart_type and cart_count > 0:
            for _ in range(cart_count):
                cart = next((c for c in available_carts if c.type.value == cart_type), None)
                if not cart:
                    raise ValueError (f"Error: รถกอล์ฟประเภท {cart_type} ว่างไม่เพียงพอ")
                
                booking.assign_cart(cart)
                cart.assign_to_schedule(booking)
                available_carts.remove(cart)
                assigned_details.append(f"รถกอล์ฟ: {cart.id} ({cart.type.value})")

        return f"ยืนยัน Add-ons สำเร็จสำหรับ {booking_id}:\n" + "\n".join(assigned_details)

    except Exception as e:
        return f"System Error: เกิดข้อผิดพลาดทางเทคนิค - {str(e)}"
    
@mcp.tool()
def view_all_caddies():
    """แสดงรายชื่อแคดดี้ทั้งหมดในระบบ พร้อมระดับ (Level) และค่าบริการ"""
    try:
        # ดึงข้อมูลผ่าน property caddies ใน system.py
        caddy_list = [
            {
                "id": c.id, 
                "name": c.name, 
                "level": c.level.value, 
                "price": c.price
            } for c in sys.caddies
        ]
        return {"total": len(caddy_list), "caddies": caddy_list}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_all_golf_carts():
    """แสดงรายการรถกอล์ฟทั้งหมด พร้อมประเภทและราคาเช่า"""
    try:
        # ดึงข้อมูลผ่าน property carts ใน system.py
        cart_list = [
            {
                "id": c.id, 
                "type": c.type.value, 
                "price": c.price
            } for c in sys.carts
        ]
        return {"total": len(cart_list), "carts": cart_list}
    except Exception as e:
        return {"error": str(e)}
    
@mcp.tool()
def view_rain_checks(phone: str):
    """ตรวจสอบรายการ Rain Check (คูปองคืนเงิน) ที่ผูกกับเบอร์โทรศัพท์"""
    try:
        # กรองข้อมูลจาก property rain_check
        vouchers = [
            {
                "code": v.code, 
                "amount": v.amount, 
                "status": v.status.value
            } for v in sys.rain_check if v.phone == phone
        ]
        return {"phone": phone, "vouchers": vouchers}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def admin_view_all_payments():
    """[Admin Only] ดูรายการชำระเงินทั้งหมดที่เกิดขึ้นในระบบ"""
    try:
        # ดึงข้อมูลผ่าน property payment
        payment_history = [
            {
                "payment_id": p.paymentID, 
                "status": "SUCCESS", # หรือดึงจากสถานะจริงใน object
                "amount": getattr(p, 'amount', 0)
            } for p in sys.payment
        ]
        return {"total_transactions": len(payment_history), "history": payment_history}
    except Exception as e:
        return {"error": str(e)}    

@mcp.tool()
def view_available_slots(course_id: str, date: str):
    """ใช้ตรวจสอบเวลาที่ยังว่างอยู่ของสนามในวันที่ระบุ"""
    try:
        course = sys.find_course(course_id)
        if not course:
            return {"error": "Course not found"}
        
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
    """แสดงรายชื่อสนามทั้งหมด พร้อมเรทราคาและความยาก (Rating/Slope)"""
    try:
        courses = sys.get_all_courses
        if not courses:
            return {"message": "No courses found"}

        course_data = []
        for c in courses:
            course_data.append({
                "course_id": c.id,
                "name": c.name,
                "pricing": {"morning": c.fee_morning, "afternoon": c.fee_afternoon},
                "difficulty": {
                    "rating": c.rating,
                    "slope": c.slope_rating,
                    "level": c.get_difficulty
                },
                "total_par": c.par
            })
        return {"total_courses": len(course_data), "courses": course_data}
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# หมวด Tournament (User)
# ==========================================

@mcp.tool()
def view_tournaments():
    """ดูรายการแข่งขันที่มีในระบบ สถานะ และจำนวนผู้สมัคร"""
    try:
        t_list = [{
            "id": t.id,
            "name": t.name,
            "date": t.date,
            "entry_fee": t.entry_fee,
            "status": t.status.value,
            "registered_count": len(t.registered_players)
        } for t in sys.tournaments]
        return {"tournaments": t_list}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def register_tournament(member_id: str, tour_id: str):
    """สมัครเข้าแข่งขันในทัวร์นาเมนต์ (ระบบจะคืนรหัส Payment)"""
    try:
        result = sys.register_tournament_get_payment(member_id, tour_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def process_tournament_payment(payment_id: str):
    """ชำระเงินค่าสมัครทัวร์นาเมนต์หรือค่าจองสนาม"""
    try:
        result = sys.process_payment(payment_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_my_notifications(member_id: str):
    """ดูการแจ้งเตือนส่วนตัวของสมาชิก (เช่น ยืนยันการจอง/การจ่ายเงิน)"""
    try:
        member = sys.find_user(member_id)
        notifications = member.get_notifications # เรียกใช้ property
        
        return {
            "member": member.name,
            "notifications": [
                {"message": n.message, "timestamp": n.time} for n in notifications
            ]
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
        return {"message": "Tournament created", "details": result}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def admin_publish_draw(tour_id: str):
    """[Admin Only] ปิดรับสมัครและจัดกลุ่มก๊วนแข่ง (Pairing) พร้อมส่งการแจ้งเตือน"""
    try:
        result = sys.close_registration_and_pairing(tour_id)
        return {"message": result}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def admin_start_tournament(tour_id: str):
    """[Admin Only] เริ่มการแข่งขันอย่างเป็นทางการ"""
    try:
        tour = sys.find_tournament(tour_id)
        tour.update_status(TournamentStatus.IN_PROGRESS)
        return {"message": f"Tournament {tour.name} has started!"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def record_tournament_score(tour_id: str, member_id: str, hole: int, stroke: int):
    """บันทึกคะแนนการตีรายหลุม (ตรวจสอบสิทธิ์และสถานะงานแข่งอัตโนมัติ)"""
    try:
        result = sys.record_tournament_score(tour_id, member_id, hole, stroke)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_leaderboard(tour_id: str):
    """ดูตารางสรุปคะแนน (Leaderboard) แบบ Real-time"""
    try:
        result = sys.get_tournament_leaderboard(tour_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def admin_end_tournament(tour_id: str):
    """[Admin Only] ปิดงานแข่ง, คำนวณ Handicap ใหม่ และอัปเดตประวัติผู้เล่น"""
    try:
        result = sys.end_tournament(tour_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def issue_rain_check(user_id: str, amount: float) -> str:
    """
    เครื่องมือสำหรับออกคูปอง Rain Check ให้แก่ผู้เล่น (Golfer) 
    ระบบจะสร้างรหัสคูปองอัตโนมัติและส่งการแจ้งเตือนหากเป็นสมาชิก (Member)
    """
    try:
        # 1. Validation เบื้องต้นตามกฎธุรกิจ (Business Rule) [cite: 99]
        if amount <= 0:
            return "Error: มูลค่าของ Rain Check ต้องมากกว่า 0 บาท"

        # 2. เรียกใช้งาน Method จาก GreenValleySystem
        new_rc = sys.issue_raincheck_to_user(user_id, amount)
        
        if new_rc:
            # คืนค่าเป็น String เพื่อให้ AI นำไปแจ้งผู้ใช้ต่อได้
            return (f"ออกคูปองสำเร็จ!\n"
                    f"รหัสคูปอง: {new_rc.code}\n"
                    f"มูลค่า: {new_rc.amount:,.2f} บาท\n"
                    f"ผูกกับเบอร์โทรศัพท์: {new_rc.phone}")
        else:
            return "Error: ไม่สามารถออกคูปองได้ (ผู้ใช้อาจไม่ใช่ Golfer หรือไม่พบข้อมูล)"

    except ValueError as e:
        # Error Handling ตามเกณฑ์ข้อ 1.19 [cite: 19, 99]
        return f"Fail: {str(e)}"
    except Exception as e:
        return f"System Error: เกิดข้อผิดพลาดทางเทคนิค - {str(e)}"

if __name__ == "__main__":
    mcp.run()