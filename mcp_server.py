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
def view_rain_checks(rain_check_code: str):
    """ตรวจสอบรายการ Rain Check (คูปองคืนเงิน) ที่ผูกกับเบอร์โทรศัพท์"""
    try:
        # กรองข้อมูลจาก property rain_check
        vouchers = [
            {
                "code": v.code, 
                "amount": v.amount, 
                "status": v.status.value
            } for v in sys.find_raincheck(rain_check_code)
        ]
        return {"rain_check_code": rain_check_code, "vouchers": vouchers}
    except Exception as e:
        return {"error": str(e)}
    
@mcp.tool()
def pay_booking(booking_id: str, rain_check_code : Optional[str] = None):
    """
    ยืนยันการชำระเงินสำหรับการจองสนาม 
    เมื่อสำเร็จจะเปลี่ยนสถานะ Booking เป็น CONFIRMED
    """
    try:
        # 2. ค้นหาการจอง
        booking = sys.find_booking(booking_id)
        if not booking:
            return {"error": f"ไม่พบข้อมูลการจองรหัส {booking_id}"}
        
        rain_check_code = rain_check_code if rain_check_code else None

        # 4. ดำเนินการชำระเงิน (เรียกใช้ process_payment ใน system)
        payment_result = sys.process_payment(booking = booking, rain_check_code = rain_check_code)
        
        # 5. อัปเดตสถานะการจองเป็น CONFIRMED (ถ้าชำระเงินสำเร็จ)
        if "successfully" in payment_result:
            return {
                "message": f"ชำระเงินสำหรับการจอง {booking_id} สำเร็จ!",
                "payment_details": payment_result,
                "booking_status": "CONFIRMED"
            }
        
        return {"error": "การชำระเงินไม่สำเร็จ", "details": payment_result}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_payment_history(user_id: str):
    """ดูประวัติการชำระเงินทั้งหมดของผู้ใช้"""
    try:
        user = sys.find_user(user_id)
        if not user:
            return {"error": "ไม่พบผู้ใช้งาน"}
            
        history = []
        for p in sys.payments:
            # กรองเฉพาะ payment ที่เกี่ยวข้องกับ user นี้ (ตรวจสอบจาก ID หรือข้อมูลอ้างอิง)
            if user_id in p.id: 
                history.append({
                    "payment_id": p.id,
                    "amount": p.amount,
                    "status": p.status.value,
                    "date": p.timestamp
                })
        return {"user": user.name, "payment_history": history}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_bookings(): 
    """ดูรายการจองทั้งหมด พร้อมรายละเอียดราคาและสถานะ"""
    bookings_list = []
    for b in sys.bookings:
        # เรียกใช้โดยไม่ต้องส่ง rain_check (เพราะใน view ปกติจะยังไม่มีการใช้คูปอง)
        # ตรวจสอบให้แน่ใจว่าใน booking.py กำหนด def calculate_total_price(self, rain_check=None):
        total_price, breakdown = b.calculate_total_price() 
        
        bookings_list.append({
            "id": b.booking_id, 
            "name": b.requester.id, 
            "price": total_price, 
            "slot": b.slot.time, 
            "status": b.status.value, 
            "addons": [str(addon) for addon in b.get_all_addons], # แปลงเป็น string เพื่อให้ JSON อ่านง่าย
            "orders": len(b.orders), 
            "Transaction": breakdown
        })
    return {"booking": bookings_list}

@mcp.tool()
def view_products():
        # เรียกใช้ p.id, p.name, p.price แบบ property ตาม system.py
    products_list = [
        {"id": p.id, "name": p.name, "price": p.price, "remaining_stock": p.stock} 
        for p in sys.products
    ]
    return {"products": products_list}
 

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
    """
    สร้างการจองสนามกอล์ฟใหม่
    :param date: วันที่ต้องการจอง **ต้องใช้รูปแบบ DD-MM-YYYY เท่านั้น** (เช่น 12-03-2026)
    :param time: เวลาที่ต้องการจอง รูปแบบ HH:MM (เช่น 08:00)
    """
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
    cart_type: Optional[str],
    cart_count: int
) -> str:
    """
    เครื่องมือสำหรับจัดการ Add-ons (แคดดี้และรถกอล์ฟ) ให้กับการจอง
    """
    try:
        booking = sys.find_booking(booking_id)
        if not booking:
            raise ValueError(f"Error: ไม่พบข้อมูลการจองรหัส {booking_id}")

        # ตรวจสอบกฎเหล็ก 1:1
        total_golfers = len(booking.golfers)
        total_requested_caddies = len(specific_caddies) + random_caddy_count
        
        if total_requested_caddies != total_golfers:
            raise ValueError(f"Error: จำนวนแคดดี้ไม่ถูกต้อง ก๊วนนี้มี {total_golfers} คน ต้องจองแคดดี้ให้ครบ {total_golfers} ท่าน")

        booking.clear_addons()

        # --- แก้ไขจุดที่ 1: ใช้ Robust Parsing เพื่อความ Consistency ---
        raw_date = booking.slot.play_date 
        time = booking.slot.time
        
        #Normalization: แปลงให้เป็นมาตรฐาน DD-MM-YYYY ก่อนส่งเข้า System
        dt_obj = sys.robust_parse_datetime(f"{raw_date} {time}")
        std_date = dt_obj.strftime("%d-%m-%Y") 
        # ---------------------------------------------------------

        assigned_details = []
        available_caddies = sys.find_available_caddies(std_date, time)
        available_carts = sys.find_available_carts(std_date, time)

        # จัดการระบุแคดดี้
        for idx, c_id in enumerate(specific_caddies):
            golfer = booking.golfers[idx]
            caddy = next((c for c in available_caddies if c.id == c_id), None)
            if not caddy:
                raise ValueError(f"Error: แคดดี้รหัส {c_id} ไม่ว่างหรือไม่มีข้อมูล")
            
            booking.assign_caddy(caddy)
            caddy.assign_to_schedule(booking)
            available_caddies.remove(caddy)
            assigned_details.append(f"{golfer.name} -> แคดดี้: {caddy.name}")

        # จัดการสุ่มแคดดี้
        start_idx = len(specific_caddies)
        if random_caddy_count > 0:
            for i in range(random_caddy_count):
                golfer = booking.golfers[start_idx + i]
                # กรองระดับแคดดี้ (ถ้าไม่ได้ระบุเลเวล ให้สุ่มจากที่ว่างทั้งหมด)
                if random_caddy_level:
                    caddy = next((c for c in available_caddies if c.leve == random_caddy_level), None)
                else:
                    caddy = available_caddies[0] if available_caddies else None

                if not caddy:
                    raise ValueError(f"Error: แคดดี้ว่างไม่เพียงพอ")
                
                # --- แก้ไขจุดที่ 2: ส่งเฉพาะ caddy ตามที่คลาส Booking กำหนด ---
                booking.assign_caddy(caddy) 
                # ---------------------------------------------------------
                caddy.assign_to_schedule(booking)
                available_caddies.remove(caddy)
                assigned_details.append(f"{golfer.name} -> แคดดี้: {caddy.name} (สุ่ม)")

        # จัดการรถกอล์ฟ
        if cart_type and cart_count > 0:
            for _ in range(cart_count):
                cart = next((c for c in available_carts if c.type.value == cart_type), None)
                if not cart:
                    raise ValueError(f"Error: รถกอล์ฟประเภท {cart_type} ว่างไม่เพียงพอ")
                
                booking.assign_cart(cart)
                cart.assign_to_schedule(booking)
                available_carts.remove(cart)
                assigned_details.append(f"รถกอล์ฟ: {cart.id} ({cart.type.value})")

        return f"ยืนยัน Add-ons สำเร็จสำหรับ {booking_id}:\n" + "\n".join(assigned_details)

    except Exception as e:
        # Error Handling: ส่งข้อความ Error กลับไปหา User อย่างชัดเจน
        return f"System Error: เกิดข้อผิดพลาดทางเทคนิค - {str(e)}"
@mcp.tool()
def view_transaction(booking_id: str):
    """ดูรายละเอียดการคำนวณราคาสุทธิของการจอง รวมถึงส่วนประกอบต่างๆ ที่นำมาคิดราคา"""
    try:
        booking = sys.find_booking(booking_id)
        if not booking:
            return {"error": f"ไม่พบข้อมูลการจองรหัส {booking_id}"}
        
        total_price, breakdown = booking.calculate_total_price()
        return {
            "booking_id": booking_id,
            "total_price": total_price,
            "price_breakdown": breakdown
        }
    except Exception as e:
        return {"error": str(e)}
    
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
def admin_view_all_payments():
    """[Admin Only] ดูรายการชำระเงินทั้งหมดที่เกิดขึ้นในระบบ"""
    try:
        # ดึงข้อมูลผ่าน property payment
        payment_history = [
            {
                "payment_id": p.payment_id, 
                "status": "SUCCESS", # หรือดึงจากสถานะจริงใน object
                "amount": getattr(p, 'amount', 0)
            } for p in sys.payments
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

# @mcp.tool()
# def register_tournament(member_id: str, tour_id: str):
#     """
#     สมัครเข้าแข่งขันในทัวร์นาเมนต์โดยตรง (ไม่จำเป็นต้องมีการจองสนามก่อน)
#     ระบบจะทำการหักค่าธรรมเนียมและเพิ่มชื่อเข้าสู่รายชื่อผู้แข่งขันทันที
#     """
#     try:
#         # 1. ค้นหาออบเจกต์ Member และ Tournament จากระบบ
#         member = sys.find_user(member_id)
#         if not member: raise ValueError(f"ไม่พบข้อมูลสมาชิก ID {member_id}")
#         tour = sys.find_tournament(tour_id)
#         if not tour : raise ValueError(f"ไม่พบข้อมูลทัวร์นาเมนต์ ID {tour_id}")
#         # 2. ตรวจสอบสถานะว่าทัวร์นาเมนต์ยังเปิดรับสมัครอยู่หรือไม่
#         # โดยเช็คจาก TournamentStatus.REGISTRATION_OPEN
#         if tour.status.value != "REGISTRATION_OPEN":
#             return {"error": f"ทัวร์นาเมนต์ {tour.name} ปิดรับสมัครแล้ว หรือยังไม่เปิดให้ลงชื่อ"}

#         # 3. ตรวจสอบว่าสมาชิกคนนี้สมัครไปแล้วหรือยัง เพื่อป้องกันข้อมูลซ้ำ
#         if member in tour.registered_players:
#             return {"error": f"สมาชิก {member.name} ได้สมัครทัวร์นาเมนต์นี้เรียบร้อยแล้ว"}


#         # 5. เพิ่มสมาชิกเข้าสู่ทัวร์นาเมนต์
#         # ฟังก์ชัน add_player จะทำการสร้าง Scorecard ให้สมาชิกโดยอัตโนมัติ
#         tour.add_player(member)

#         # 6. ส่งการแจ้งเตือนไปยังสมาชิก
#         msg = f"สมัครทัวร์นาเมนต์ {tour.name} สำเร็จ! ชำระค่าธรรมเนียม {entry_fee:,.2f} บาท เรียบร้อยแล้ว"
#         member.add_notification(Notification(msg))

#         return {
#             "status": "Success",
#             "message": msg,
#             "details": {
#                 "tournament": tour.name,
#                 "player": member.name,
#                 "fee_paid": entry_fee,
#                 "payment_id": payment.paymentID
#             }
#         }

#     except Exception as e:
#         # กรณีไม่พบ user_id หรือ tour_id ระบบจะ raise error จาก find_user/find_tournament
#         return {"error": str(e)}

@mcp.tool()
def register_tournament(member_id: str, tour_id: str):
    """สมัครเข้าแข่งขันและชำระเงินค่าธรรมเนียมทัวร์นาเมนต์ทันที"""
    try:
        # เรียกใช้เมธอดที่เราเพิ่งเพิ่มใน system.py
        result = sys.process_registration_payment(member_id, tour_id)
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
            raise ValueError("Error: มูลค่าของ Rain Check ต้องมากกว่า 0 บาท")

        # 2. เรียกใช้งาน Method จาก GreenValleySystem
        new_rc = sys.issue_raincheck_to_user(user_id, amount)

        if new_rc:
            # คืนค่าเป็น String เพื่อให้ AI นำไปแจ้งผู้ใช้ต่อได้
            return (f"ออกคูปองสำเร็จ!\n"
                    f"รหัสคูปอง: {new_rc.code}\n"
                    f"มูลค่า: {new_rc.amount:,.2f} บาท\n"
                    f"ผูกกับเบอร์โทรศัพท์: {new_rc.phone}")
        else:
            raise ValueError("Error: ไม่สามารถออกคูปองได้ (ผู้ใช้อาจไม่ใช่ Golfer หรือไม่พบข้อมูล)")

    except Exception as e:
        return f"System Error: เกิดข้อผิดพลาดทางเทคนิค - {str(e)}"

@mcp.tool()
def get_user_rainchecks(user_id: str):
    #test
    """เครื่องมือสำหรับดึงข้อมูล Rain Check ทั้งหมดของผู้ใช้รายนั้น (สำหรับตรวจสอบสถานะและมูลค่า) """
    try:
        user = sys.find_user(user_id)
        if not user:
            raise ValueError("ไม่พบผู้ใช้งาน") 
        
        # กรองข้อมูล Rain Check ที่ผูกกับเบอร์โทรศัพท์ของผู้ใช้
        rainchecks = [
            {
                "code": rc.code,
                "amount": rc.amount,
                "status": rc.status.value
            } for rc in sys.rain_check if rc.phone == user.phone
        ]
        return {"user": user.name, "rainchecks": rainchecks}
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    mcp.run()