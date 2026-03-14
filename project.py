from fastmcp import FastMCP
from system import GreenValleySystem
from models.enum import TournamentStatus, SlotStatus 
from models.booking import Booking
from models.payment import Payment, Raincheck
from models.enum import Tier
from models.users import Member, Guest
from typing import List, Optional
from datetime import datetime

mcp = FastMCP("GreenValleyMCP")

sys = GreenValleySystem()
sys.create_data()

# หมวด User & Ordering (Booking & Products)

@mcp.tool()
def view_rain_checks(rain_check_code: str):
    """
    ตรวจสอบรายละเอียดของ Rain Check (คูปองคืนเงิน) โดยใช้รหัสคูปอง
    
    Args:
        rain_check_code (str): รหัสคูปองที่ขึ้นต้นด้วย 'RC-' (เช่น 'RC-0001-M-001')
    
    Returns:
        Dict: ข้อมูลมูลค่าคูปองและสถานะ (AVAILABLE, USED) หากไม่พบจะคืนค่า error
    """
    try:
        voucher = sys.find_raincheck(rain_check_code)
        if not voucher:
            return {"error": f"ไม่พบข้อมูล Rain Check รหัส {rain_check_code}"}
        return {
                    "rain_check_code": rain_check_code, 
                    "vouchers": [{
                        "code": voucher.code, 
                        "amount": voucher.amount, 
                        "status": voucher.status.value
                    }]
        }
    except Exception as e:
        return {"error": f"System Error: {str(e)}"}
    
@mcp.tool()
def pay_booking(booking_id: str, rain_check_code = None):
    """
    [User] ดำเนินการชำระเงินสำหรับการจองสนาม (Booking) เพื่อเปลี่ยนสถานะจาก PENDING เป็น CONFIRMED
    
    Args:
        booking_id (str): รหัสการจองที่ต้องการจ่ายเงิน (เช่น 'BK-001')
        rain_check_code (Optional[str]): รหัสคูปอง Rain Check หากต้องการใช้เป็นส่วนลดเพิ่มเติม
        
    Note:
        - ระบบจะคำนวณราคาสุทธิโดยหักส่วนลดตาม Tier ของสมาชิกและคูปองอัตโนมัติ
        - เมื่อสำเร็จ สถานะ Booking จะเปลี่ยนเป็น CONFIRMED_PAID และส่ง Notification หาผู้ใช้
    """
    try:
        booking = sys.find_booking(booking_id)
        if not booking:
            return {"error": f"ไม่พบข้อมูลการจองรหัส {booking_id}"}
        
        rain_check_code = rain_check_code if rain_check_code else None

        payment_result = sys.process_payment(booking = booking, rain_check_code = rain_check_code)
    
        if payment_result:
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
    """ดูประวัติการชำระเงินทั้งหมดของสมาชิก (ทั้งค่าจองสนามและค่าสมัครทัวร์นาเมนต์)"""
    try:
        user = sys.find_user(user_id)
        if not user:
            return {"error": "ไม่พบผู้ใช้งาน"}
            
        history = []
        for p in sys.payments:
            if p.member and p.member.id == user_id:
                history.append({
                    "payment_id": p.payment_id,
                    "amount": p.amount,
                    "status": p.status.value,
                    "date": getattr(p, 'time', 'N/A')
                })
        return {"user": user.name, "payment_history": history}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_bookings(): 
    """
    [Admin] ดูรายการจอง (Booking) ทั้งหมดในระบบ พร้อมรายละเอียดราคาและสถานะปัจจุบัน
    """
    bookings_list = []
    for b in sys.bookings:
        total_price, breakdown = b.calculate_total_price() 
        
        formatted_addons = []
        for addon in b.get_all_addons:
            if hasattr(addon, 'level'): # กรณีแคดดี้
                formatted_addons.append({"type": "CADDY", "id": addon.id, "name": addon.name, "price": addon.price})
            elif hasattr(addon, 'type'): # กรณีรถกอล์ฟ
                formatted_addons.append({"type": "CART", "id": addon.id, "cart_type": addon.type.value, "price": addon.price})
            elif hasattr(addon, 'order_id'): # กรณีสั่งสินค้า
                formatted_addons.append({"type": "ORDER", "id": addon.order_id, "price": addon.price})

        bookings_list.append({
            "id": b.booking_id, 
            "group_leader": b.requester.id, 
            "total_group_price": total_price, 
            "slot": b.slot.time, 
            "status": b.status.value, 
            "addons": formatted_addons, 
            "orders": len(b.orders), 
            "Transaction_Receipt": breakdown
        })
    return {"booking": bookings_list}

@mcp.tool()
def view_products():
    """
    [User] ตรวจสอบรายการสินค้า อาหาร และบริการ พร้อมราคาและจำนวนคงเหลือในสต็อก
    """
    products_list = [
        {"id": p.id, "name": p.name, "price": p.price, "remaining_stock": p.stock} 
        for p in sys.products
    ]
    return {"products": products_list}
 

@mcp.tool()
def place_order(booking_id: str, product_id: str, quantity: int):
    """
    [User] สั่งซื้อสินค้า/อาหารเข้าสู่รายการจอง (หักสต็อกอัตโนมัติ)
    
    Args:
        booking_id (str): รหัสการจองที่ต้องการสั่งสินค้า (เช่น 'BK-001')
        product_id (str): รหัสสินค้า (เช่น 'P-001')
        quantity (int): จำนวนที่ต้องการสั่ง
    """
    try:
        result = sys.place_order(booking_id, product_id, quantity)
        return {"message": result}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_golf_booking(member_id: str, course_id: str, date: str, time: str, companions: list[str] = None):
    """
    [User] สร้างรายการจองสนามกอล์ฟใหม่ (Tee-off Booking)
    
    Args:
        member_id (str): ID ของผู้จอง (เช่น 'M-001')
        course_id (str): ID ของสนาม (เช่น 'C-001', 'C-002')
        date (str): วันที่ต้องการจอง **รูปแบบ DD-MM-YYYY เท่านั้น** (เช่น '25-12-2026')
        time (str): เวลาที่ต้องการจอง รูปแบบ HH:MM (เช่น '08:00')
        companions (Optional[list[str]]): รายชื่อ ID ของเพื่อนร่วมก๊วน (รวมผู้จองต้องไม่เกิน 4 คน)
        
    Constraint:
        - Member จองล่วงหน้าได้ตาม Tier limit (Platinum 30 วัน, Gold 14 วัน, Silver 7 วัน)
        - Guest (Walk-in) จองได้เฉพาะวันปัจจุบันเท่านั้น
        - ระบบจะล็อก Slot สนามทันทีเป็นสถานะ RESERVED
    """
    
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
def select_booking_addons(
    booking_id: str,
    specific_caddies: List[str],
    random_caddy_level: Optional[str],
    random_caddy_count: int,
    cart_type: Optional[str],
    cart_count: int
):
    """
    [User] เลือกแคดดี้และรถกอล์ฟเพิ่มเติมสำหรับการจองที่สร้างไว้แล้ว
    
    Args:
        booking_id (str): รหัสการจอง (เช่น 'BK-001')
        specific_caddies (list[str]): รายชื่อ ID แคดดี้ที่ต้องการระบุเจาะจง (เช่น ['CDY-001'])
        random_caddy_level (Optional[str]): ระดับแคดดี้กรณีต้องการสุ่ม (PRO, REGULAR, TRAINEE)
        random_caddy_count (int): จำนวนแคดดี้ที่ต้องการสุ่มเพิ่ม
        cart_type (Optional[str]): ประเภทรถกอล์ฟ (STANDARD, COUPLE, VIP)
        cart_count (int): จำนวนรถกอล์ฟที่ต้องการเช่า
        
    Requirement:
        - จำนวนแคดดี้รวม (เจาะจง + สุ่ม) ต้องเท่ากับจำนวนนักกอล์ฟในก๊วนพอดี (1 คนต่อ 1 แคดดี้)
    """
    try:
        booking = sys.find_booking(booking_id)
        if not booking:
            return {"error": f"ไม่พบข้อมูลการจองรหัส {booking_id}"}

        total_golfers = len(booking.golfers) 
        total_requested_caddies = len(specific_caddies) + random_caddy_count
        
        if total_requested_caddies != total_golfers:
            return {"error": f"จำนวนแคดดี้ไม่ถูกต้อง ก๊วนนี้มี {total_golfers} คน ต้องจองแคดดี้ให้ครบ {total_golfers} ท่าน"}

        booking.clear_addons()

        dt_obj = sys.robust_parse_datetime(f"{booking.slot.play_date} {booking.slot.time}")
        std_date = dt_obj.strftime("%d-%m-%Y")
        time = booking.slot.time

        available_caddies = sys.find_available_caddies(std_date, time)
        available_carts = sys.find_available_carts(std_date, time)
        
        assigned_details = []

        # จัดการระบุแคดดี้
        for idx, c_id in enumerate(specific_caddies):
            golfer = booking.golfers[idx]
            caddy = next((c for c in available_caddies if c.id == c_id), None)
            if not caddy:
                raise ValueError(f"Error: แคดดี้ {c_id} ไม่ว่าง")
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
                    caddy = next((c for c in available_caddies if c.level.value == random_caddy_level), None)
                else:
                    caddy = available_caddies[0] if available_caddies else None

                if not caddy:
                    raise ValueError(f"Error: แคดดี้ว่างไม่เพียงพอ")
                
                booking.assign_caddy(caddy) 
                
                caddy.assign_to_schedule(booking)
                available_caddies.remove(caddy)
                assigned_details.append(f"{golfer.name} -> แคดดี้: {caddy.name} (สุ่ม)")

        # จัดการรถกอล์ฟ
        if cart_type and cart_count > 0:
            for _ in range(cart_count):
                cart = next((c for c in available_carts if c.type.value == cart_type), None)
                if cart:
                    booking.assign_cart(cart)
                    cart.assign_to_schedule(booking)
                    available_carts.remove(cart)
                    assigned_details.append(f"รถกอล์ฟ: {cart.id} ({cart.type.value})")

        return {"message": f"ยืนยัน Add-ons สำเร็จสำหรับ {booking_id}:\n" + "\n".join(assigned_details)}

    except Exception as e:
        return {"error": str(e)}
    

@mcp.tool()
def view_transaction(booking_id: str):
    """
    [User] ตรวจสอบรายละเอียดราคาสุทธิ การคำนวณส่วนลด และค่าใช้จ่ายทั้งหมดของรายการจอง
    """

    try:
        booking = sys.find_booking(booking_id)
        if not booking:
            return {"error": f"ไม่พบข้อมูลการจองรหัส {booking_id}"}
        
        if booking.status.value == "CONFIRMED_PAID":
            payment = next((p for p in sys.payments if p.booking_id == booking_id), None)
            if payment and payment.get_transaction_details():
                return {
                    "booking_id": booking_id,
                    "total_price": payment.amount,
                    "price_breakdown": payment.get_transaction_details()
                }
        
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
    """[User/Admin] แสดงรายชื่อแคดดี้ทั้งหมด พร้อมระดับและราคาบริการ"""
    try:
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
def view_all_available_caddies(date: str, time: str):
    """ตรวจสอบรายชื่อแคดดี้ที่ว่างในวันที่และเวลาที่ระบุ (สำหรับการจอง)"""
    try:
        available_caddies = sys.find_available_caddies(date, time)
        caddy_list = [
            {
                "id": c.id, 
                "name": c.name, 
                "level": c.level.value, 
                "price": c.price
            } for c in available_caddies
        ]
        return {"date": date, "time": time, "available_caddies": caddy_list}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_all_golf_carts():
    """[User/Admin] แสดงรายการรถกอล์ฟทั้งหมดที่มีในระบบและราคาเช่า"""
    try:
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
    """
    [User] ตรวจสอบเวลาว่าง (Available Slots) ของสนามกอล์ฟในวันที่ระบุ
    
    Args:
        course_id (str): ID สนาม (เช่น 'C-001')
        date (str): วันที่ **รูปแบบ DD-MM-YYYY เท่านั้น**
    """
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

# หมวด Course Information

@mcp.tool()
def view_all_courses():
    """[User] แสดงรายชื่อสนามกอล์ฟทั้งหมด พร้อมข้อมูลเรทราคาและความยาก"""
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

# หมวด Tournament (User)

@mcp.tool()
def view_tournaments():
    """[User] ดูรายการแข่งขัน (Tournament) ทั้งหมด สถานะการรับสมัคร และค่าธรรมเนียม"""
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
def apply_for_tournament(member_id: str, tour_id: str):
    """
    [User] สมัครเข้าร่วมการแข่งขัน (สถานะจะเป็น PENDING จนกว่าจะชำระเงิน)
    
    Args:
        member_id (str): ID สมาชิก (เช่น 'M-001')
        tour_id (str): ID ทัวร์นาเมนต์ (เช่น 'T-001')
    """
    try:
        p_id = sys.register_tournament_pending(member_id, tour_id)
        return {
            "status": "PENDING",
            "payment_id": p_id,
            "message": "สมัครสำเร็จ! กรุณาชำระเงินโดยใช้รหัส Payment ID นี้"
        }
    except Exception as e:
        return {"error": str(e)}
    

@mcp.tool()
def pay_tournament_fee(payment_id: str):
    """[User] ยืนยันการชำระเงินค่าสมัครทัวร์นาเมนต์โดยใช้รหัส Payment ID"""
    try:
        if sys.confirm_tournament_payment(payment_id):
            return {"status": "SUCCESS", "message": "ชำระเงินเรียบร้อย สิทธิ์การแข่งของคุณยืนยันแล้ว"}
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

# หมวด Admin (Tournament Management)

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
    """[Admin Only] ปิดรับสมัครและจัดกลุ่มก๊วน (Pairing) พร้อมกำหนดเวลา Tee-off"""
    try:
        result = sys.close_registration_and_pairing(tour_id)
        return {"message": result}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def admin_start_tournament(tour_id: str):
    """[Admin Only] เปลี่ยนสถานะทัวร์นาเมนต์เป็น IN_PROGRESS เพื่อเริ่มบันทึกคะแนน"""
    try:
        tour = sys.find_tournament(tour_id)
        tour.update_status(TournamentStatus.IN_PROGRESS)
        return {"message": f"Tournament {tour.name} has started!"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def record_tournament_score(tour_id: str, member_id: str, hole: int, stroke: int):
    """
    [Admin/Staff] บันทึกคะแนนการตี (Strokes) ของผู้เล่นรายหลุม
    
    Args:
        tour_id (str): ID ทัวร์นาเมนต์
        member_id (str): ID ผู้เล่น
        hole (int): หมายเลขหลุม (1-18)
        stroke (int): จำนวนครั้งที่ตี
    """
    try:
        result = sys.record_tournament_score(tour_id, member_id, hole, stroke)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def view_leaderboard(tour_id: str):
    """[User/Admin] ดูตารางคะแนนสด (Real-time Leaderboard) ของทัวร์นาเมนต์ที่กำลังแข่ง"""
    try:
        result = sys.get_tournament_leaderboard(tour_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def admin_end_tournament(tour_id: str):
    """[Admin Only] จบการแข่งขัน คำนวณ Handicap ใหม่ และสรุปผลเข้าระบบประวัติผู้เล่น"""
    try:
        result = sys.end_tournament(tour_id)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def issue_rain_check(user_id: str) -> str:
    """
    [Admin Only] ออกคูปอง Rain Check ให้แก่ผู้เล่น (กรณีฝนตกสนามเล่นไม่ได้)
    ระบบจะคำนวณมูลค่าคูปองให้อัตโนมัติ (25% ของยอดสุทธิการจอง)
    
    Args:
        user_id (str): ID สมาชิกที่จะได้รับคูปอง (เช่น 'M-001')
    """
    try:
        booking = sys.find_booking_by_member(user_id) # สมมติว่ามี method นี้เพื่อเช็คว่าผู้ใช้มีการจองที่เกี่ยวข้องหรือไม่
        if not booking:
            raise ValueError("Error: ผู้ใช้ไม่พบหรือไม่ได้ทำการจอง")
        total_price, _ = booking.calculate_total_price()
        calculated_amount = float(total_price) * 0.25
        new_rc = sys.issue_raincheck_to_user(user_id, calculated_amount)
        if new_rc:
            return (f"ออกคูปองสำเร็จ!\n"
                    f"รหัสคูปอง: {new_rc.code}\n"
                    f"มูลค่า: {new_rc.amount:,.2f} บาท\n"
                    f"ผูกกับเบอร์โทรศัพท์: {new_rc.phone}")
        else:
            raise ValueError("Error: ไม่สามารถออกคูปองได้ (ผู้ใช้อาจไม่ใช่ Golfer หรือไม่พบข้อมูล)")

    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_user_rainchecks(user_id: str):
    
    """เครื่องมือสำหรับดึงข้อมูล Rain Check ทั้งหมดของผู้ใช้รายนั้น (สำหรับตรวจสอบสถานะและมูลค่า) """
    try:
        user = sys.find_user(user_id)
        if not user:
            return {"error": "ไม่พบผู้ใช้งาน"}
        
        rainchecks = [
            {
                "code": rc.code,
                "amount": rc.amount,
                "status": rc.status.value
            } for rc in sys.rain_checks if rc.phone == getattr(user, 'phone', None)
        ]
        return {"user": user.name, "rainchecks": rainchecks}
    except Exception as e:
        return {"error": str(e)}
    

@mcp.tool()
def admin_add_strike(user_id: str, reason: str, count: int = 1):
    """
    [Admin Only] ลงโทษสมาชิกด้วยการเพิ่ม Strike กรณีทำผิดกฎสนาม (เช่น No-show หรือเล่นล่าช้า)
    
    Args:
        user_id (str): ID ของสมาชิกที่ต้องการลงโทษ (เช่น 'M-001')
        reason (str): เหตุผลในการลงโทษ (เพื่อใช้ในการบันทึก log)
        count (int): จำนวน Strike ที่จะเพิ่ม (ค่าเริ่มต้นคือ 1)
        
    Penalty Logic:
        - 2 Strikes: ระงับสิทธิ์การจองวันเสาร์-อาทิตย์เป็นเวลา 30 วัน (WEEKEND_BAN)
        - 3 Strikes: ระงับสิทธิ์การใช้งานถาวร/ชั่วคราว 60 วัน (BANNED)
    """
    try:
        result = sys.admin_strike_user(user_id, count)
        
        result["reason"] = reason
        return result
        
    except Exception as e:
        return {"error": str(e)}
    
@mcp.tool()
def admin_clear_user_strikes(user_id: str):
    """
    [Admin Only] ล้างจำนวน Strike ทั้งหมดของผู้เล่น และปรับสถานะกลับเป็น ACTIVE
    ใช้ในกรณีที่ต้องการยกเลิกการแบน หรือแอดมินพิจารณาคืนสิทธิ์ให้ผู้เล่น
    """
    try:
        user = sys.find_user(user_id)
        if not hasattr(user, 'reset_strikes'):
            return {"error": "ผู้ใช้ประเภทนี้ไม่มีระบบ Strike"}
            
        msg = user.reset_strikes()
        return {"message": f"ดำเนินการสำเร็จสำหรับ {user.name}", "details": msg}
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    mcp.run()