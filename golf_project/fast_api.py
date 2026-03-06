import re
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query  # เพิ่ม HTTPException เข้ามา
from system import GreenValleySystem
from typing import List, Optional
from models.users import Golfer, Member, Guest, Tier, UserStatus
from models.course import SlotStatus, CourseType
from models.resources import CaddyLevel, CartType
from models.booking import Booking, BookingStatus
from models.payment import Payment, PaymentMethod, PaymentStatus
from models.request_form import BillRequest

app = FastAPI(
    title="Green Valley Management System", # เปลี่ยนชื่อโปรเจกต์ตรงนี้
    description="ระบบจัดการสนามกอล์ฟและการสั่งอาหารสำหรับสมาชิก", # คำอธิบายระบบ
    version="1.0.0", # เวอร์ชันของ API
)

sys = GreenValleySystem()
sys.create_data()
john = sys.users[0]             # ดึงออบเจกต์ Member (John Doe)

print("\n" + "="*40)

# ------------ ฟังก์ชัน Validation สำหรับ booking ---------------------
# รูปแบบเบอร์โทร
def validate_phone(phone: str): #✔️
    if not re.match(r"^\d{3}-\d{3}-\d{4}$", phone):
        raise HTTPException(400, "รูปแบบเบอร์โทรศัพท์ผิด (ต้องเป็น XXX-XXX-XXXX)")
# รูปแบบวัน
def validate_search_date_range(date_str: str, time_str: Optional[str] = None):
    # 1. ตรวจสอบรูปแบบวันที่
    if not re.match(r"^\d{2}-\d{2}-\d{4}$", date_str):
        raise HTTPException(400, f"รูปแบบวันที่ '{date_str}' ไม่ถูกต้อง (เช่น 01-12-2024)")
    try:
        target_date = datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        raise HTTPException(400, f"วันที่ '{date_str}' ไม่ถูกต้อง")
    
    # 2. เช็คห้ามเป็นวันที่ในอดีต
    now = datetime.now()
    if target_date < now.date():
        raise HTTPException(400, "ไม่สามารถจอง/ค้นหาย้อนหลังได้")
    
    # 3. ค้นหาล่วงหน้าสูงสุด 1 ปี
    if target_date > now.date() + timedelta(days=365):
        raise HTTPException(400, "สามารถค้นหาล่วงหน้าได้สูงสุด 1 ปี เท่านั้น")
    
    # 4. ตรวจสอบรูปแบบเวลาและเช็คห้ามเป็นเวลาในอดีต
    if time_str:
        if not re.match(r"^\d{2}:\d{2}$", time_str):
            raise HTTPException(400, "รูปแบบเวลาไม่ถูกต้อง (เช่น 06:00)")
        target_time = datetime.strptime(time_str, "%H:%M").time()
        if target_date == now.date() and target_time < now.time():
            raise HTTPException(400, f"เวลา {time_str} ผ่านมาแล้ว")
            
    return target_date

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

# view bookings by member_id***
@app.get("/view/bookings", tags=["User"])
def view_my_bookings(user_id: str = Query(..., description="รหัส Member (เช่น M-001, M-002)")):
    # 1. เช็คว่ามี User นี้ในระบบไหม
    user = sys.find_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "ไม่พบข้อมูลผู้ใช้ในระบบ")
        
    # 2. เช็คว่าเป็น Member หรือไม่ (Walk-in ดูไม่ได้)
    if not isinstance(user, Member):
        raise HTTPException(403, "ขออภัยครับ ฟังก์ชันนี้สงวนสิทธิ์เฉพาะ Member เท่านั้น")

    my_bookings = []
    
    # 3. วนลูปหา Booking ที่มีชื่อ Member คนนี้อยู่ในก๊วน
    for b in sys.bookings:
        if any(g.user_id == user_id for g in b.golfers):
            
            # 1. จัดรูปแบบข้อมูลแคดดี้ (ใครได้แคดดี้คนไหน)
            caddies_info = []
            for g_id, caddy in b.caddy_assignments.items():
                golfer_name = next((g.name for g in b.golfers if g.user_id == g_id), g_id)
                caddies_info.append(f"{golfer_name} ได้แคดดี้ -> {caddy.name} (ระดับ: {caddy.level.value})")
            # 2. จัดรูปแบบข้อมูลรถกอล์ฟ
            carts_info = [f"คันที่ {cart.id} ({cart.type.value})" for cart in b.carts]

            my_bookings.append({
                "booking_id": b.booking_id,
                "status": b.status.value,
                "course": b.slot.course.name,
                "date": b.slot.play_date,
                "time": b.slot.time,
                "role": "Requester (คนจอง)" if b.requester.user_id == user_id else "Companion (ผู้ร่วมก๊วน)",
                "golfers": [f"{g.name} ({getattr(g, 'phone', '-')})" for g in b.golfers], # แสดงชื่อและเบอร์โทร
                "caddies": caddies_info if caddies_info else ["- ยังไม่ได้เลือกแคดดี้ -"],
                "carts": carts_info if carts_info else ["- ไม่ได้ใช้รถกอล์ฟ -"]
            })
            
    return {
        "user_id": user.user_id,
        "name": user.name,
        "tier": user.tier.value,
        "total_bookings": len(my_bookings),
        "history": my_bookings
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

# 📙 ฺBOOKING FLOW ---------------------------------

@app.get("/user/search_slot", tags=["User"])
def search_available_slots(date: str = Query(..., description="วันที่จอง (DD-MM-YYYY)"),
                           course_type: Optional[CourseType] = Query(None)):
    
    validate_search_date_range(date)
    available = []
    
    for course in sys.courses:
        if course_type is None or course.type == course_type:
            slots = course.get_available_slots(date)
            morning_times = []
            afternoon_times = []
            for slot in slots:
                hour = int(slot.time.split(":")[0])
                if hour < 12:
                    morning_times.append(slot.time)
                else:
                    afternoon_times.append(slot.time)
            if morning_times:
                available.append({
                    "course": course.name,
                    "session": "MORNING",
                    "green_fee_per_pax": course.fee_morning,
                    "available_times": morning_times
                })
            
            if afternoon_times:
                available.append({
                    "course": course.name,
                    "session": "AFTERNOON",
                    "green_fee_per_pax": course.fee_afternoon,
                    "available_times": afternoon_times
                })
    return {"date": date, "available_slots": available}

@app.post("/user/online_booking", tags=["User"])
def create_booking(user_id: str = "M-001", 
                   course_type: CourseType = CourseType.CHAMPIONSHIP, 
                   date: str = Query(..., description="วันที่จอง (DD-MM-YYYY)"), 
                   time: str = Query(..., description="เวลาที่ต้องการออกรอบ (HH:MM)"),
                   companion_ids: List[str] = Query([], description="เพิ่ม id เพื่อน (ถ้ามี)")):
    
    if user_id in companion_ids:
        raise HTTPException(400, "ไม่สามารถเพิ่มตัวเองเป็น Guest ซ้ำในก๊วนได้")

    user = sys.find_user_by_id(user_id)
    if not user or not isinstance(user, Member):
        raise HTTPException(403, "เฉพาะ Member เท่านั้นที่สามารถจองออนไลน์ได้")

    target_course = sys.get_course_by_type(course_type)
    if len(companion_ids) > 3: raise HTTPException(400, "ก๊วนนึงรับได้สูงสุด 4 คน")
    
    # Check Strike & Suspension
    is_ban, msg = user.is_suspended()
    if is_ban: raise HTTPException(403, msg)
    if user.is_weekend_banned(date):
        raise HTTPException(403, "คุณถูกระงับสิทธิ์การจองล่วงหน้าในวันหยุด (สะสมครบ 2 Strike)")

    # Validate Formats
    validate_search_date_range(date, time)
    sys.check_booking_lead_time(user, date)
    
    for g_id in [user_id] + companion_ids:
        if not sys.check_5_hour_rule(g_id, date, time):
            raise HTTPException(400, f"ปฏิเสธการจอง! รหัส {g_id} มีคิวออกรอบใน 5 ชั่วโมงนี้")
    
    slot = target_course.find_slot(date, time)
    
    if not slot:
        raise HTTPException(400, f"เวลา {time} (ไม่อยู่ในเวลาทำการ)")
        
    if slot.status != SlotStatus.AVAILABLE:
        raise HTTPException(400, f"เวลา {time} ถูกจองไปแล้ว")
    
    slot.status = SlotStatus.RESERVED
    
    b_id = f"BK-{len(sys.bookings) + 1:03d}"
    new_booking = Booking(b_id, user, slot)
    
    for g_id in companion_ids:
        companion = sys.find_user_by_id(g_id)
        if not companion: raise HTTPException(400, f"ไม่พบข้อมูลผู้เล่นรหัส {g_id}")
        new_booking.add_golfer(companion)

    sys.bookings.append(new_booking)
    
    for golfer in new_booking.golfers:
        if isinstance(golfer, Golfer):
            golfer.add_to_history(new_booking)
                
    return {"message": "Booking Created", "booking_id": b_id, "golfers": [{"id": g.user_id, "name": g.name} for g in new_booking.golfers]}

# สำหรับ guest
@app.post("/user/walk-in_booking", tags=["User"])
def walk_in_booking(
    guest_name: str = Query(..., description="ชื่อลูกค้า Walk-in"),
    phone: str = Query(..., description="เบอร์โทรศัพท์ (XXX-XXX-XXXX)"),
    course_type: CourseType = Query(CourseType.CHAMPIONSHIP),
    date: str = Query(datetime.now().strftime("%d-%m-%Y"), description="วันที่ (DD-MM-YYYY)"),
    time: str = Query(..., description="เวลาที่ต้องการออกรอบ (HH:MM)"),
    companion_phones: List[str] = Query([], description="เพิ่มเบอร์โทรศัพท์เพื่อนร่วมก๊วน (ถ้ามี)")
):
    target_course = sys.get_course_by_type(course_type)
    
    validate_search_date_range(date, time)
    
    # เช็คกฎล่วงหน้า?
    temp_guest = Guest("temp", guest_name, phone)
    sys.check_booking_lead_time(temp_guest, date)
    
    # ตรวจสอบเบอร์โทร
    validate_phone(phone)
    for p in companion_phones:
        validate_phone(p)
    
    # เช็คจำนวนคนในก๊วนทั้งหมด (1 ก๊วน ไม่เกิน 4 คน)
    # เช็คจำนวนคนรวมหัวหน้าก๊วน
    if len(companion_phones) + 1 > 4: 
        raise HTTPException(400, "ก๊วนนึงรับได้สูงสุด 4 คนเท่านั้น")
    
    target_dt = datetime.strptime(f"{date} {time}", "%d-%m-%Y %H:%M")
    slot = target_course.find_slot(date, time)
    
    if not slot:
        raise HTTPException(400, f"เวลา {time} (ไม่อยู่ในเวลาทำการ)")
    if slot.status != SlotStatus.AVAILABLE:
        raise HTTPException(400, f"เวลา {time} ถูกจองไปแล้ว")
        
    # รับแค่ชื่อคนแรก ที่เหลือตั้งชื่อเพื่อนให้อัตโนมัติ
    guest_data = [{"name": guest_name, "phone": phone}] # ข้อมูลหัวหน้าก๊วน (คนที่ 1)
    
    # สร้างข้อมูลลูกก๊วน พร้อมตั้งชื่ออัตโนมัติ
    for i, comp_phone in enumerate(companion_phones, start=1):
        guest_data.append({
            "name": f"เพื่อนของ {guest_name} ({i})",
            "phone": comp_phone
        })

    created_guests = sys.create_walkin_group(guest_data)
      
    # สร้าง Booking
    slot.status = SlotStatus.RESERVED
    b_id = f"WK-{len(sys.bookings) + 1:03d}"
    
    # หัวหน้าก๊วน (created_guests[0])
    new_booking = Booking(b_id, created_guests[0], slot)
    
    # แอดเพื่อนๆ เข้าไปในก๊วน (ตั้งแต่ created_guests[1] เป็นต้นไป)
    for comp_guest in created_guests[1:]:
        new_booking.add_golfer(comp_guest)

    sys.bookings.append(new_booking)
    
    return {
        "message": "Walk-in Created", 
        "booking_id": b_id, 
        "golfers": [{"id": g.user_id, "name": g.name, "phone": g.phone} for g in new_booking.golfers]
    }

@app.post("/user/booking/addons", tags=["User"])
def select_addons(booking_id: str, 
                  specific_caddies: List[str] = Query([], description="ระบุรหัสแคดดี้ (ตามลำดับ)"),
                  random_caddy_level: Optional[CaddyLevel] = Query(None, description="ระดับแคดดี้สุ่ม"),
                  random_caddy_count: int = Query(0, description="จำนวนแคดดี้สุ่ม"),
                  cart_type: Optional[CartType] = Query(None, description="ประเภทรถ"),
                  cart_count: int = Query(0, description="จำนวนรถ")):
    
    booking = sys.find_booking_by_id(booking_id)
    if not booking: raise HTTPException(404, "Booking not found")
    
    if isinstance(booking.requester, Guest):
        if len(specific_caddies) > 0:
            raise HTTPException(403, "ขออภัยครับ ลูกค้า Walk-in / Guest ไม่สามารถระบุตัวแคดดี้ได้ ต้องใช้ระบบสุ่มเท่านั้น")
       
    booking.clear_addons()

    total_golfers = len(booking.golfers)
    total_requested_caddies = len(specific_caddies) + random_caddy_count

    # กฎ: 1 ผู้เล่นต่อ 1 แคดดี้
    # 📌 กฎเหล็ก: 1 ผู้เล่นต่อ 1 แคดดี้เท่านั้น (ห้ามขาดห้ามเกิน)
    if total_requested_caddies != total_golfers:
        raise HTTPException(400, f"จำนวนแคดดี้ไม่ถูกต้อง! ก๊วนนี้มี {total_golfers} คน ต้องเลือกแคดดี้ให้ครบ {total_golfers} ท่าน (1:1)")
    
    # if len(specific_caddies) + random_caddy_count > len(booking.golfers):
    #     raise HTTPException(400, "จองแคดดี้รวมกันต้องไม่เกินจำนวนคนในก๊วน")

    assigned_details = []
    date, time = booking.slot.play_date, booking.slot.time
    available_caddies = sys.find_available_caddies(date, time)
    available_carts = sys.find_available_carts(date, time)

    for idx, c_id in enumerate(specific_caddies):
        golfer = booking.golfers[idx]
        caddy = next((c for c in available_caddies if c.id == c_id), None)
        if not caddy: raise HTTPException(400, f"แคดดี้รหัส {c_id} ติดจองงานอื่น หรือไม่พบข้อมูล")
        
        booking.assign_caddy(golfer.user_id, caddy)
        caddy.assign_to_schedule(booking)
        available_caddies.remove(caddy)
        assigned_details.append(f"{golfer.name} -> ได้แคดดี้: {caddy.name}")

    start_idx = len(specific_caddies)
    if random_caddy_level and random_caddy_count > 0:
        for i in range(random_caddy_count):
            golfer = booking.golfers[start_idx + i]
            caddy = next((c for c in available_caddies if c.level == random_caddy_level), None)
            if not caddy: raise HTTPException(400, f"แคดดี้ระดับ {random_caddy_level.value} ว่างไม่พอ")
            
            booking.assign_caddy(golfer.user_id, caddy)
            caddy.assign_to_schedule(booking)
            available_caddies.remove(caddy)
            assigned_details.append(f"{golfer.name} -> ได้แคดดี้: {caddy.name} (สุ่ม)")

    if cart_type and cart_count > 0:
        for _ in range(cart_count):
            cart = next((c for c in available_carts if c.type == cart_type), None)
            if not cart: raise HTTPException(400, f"รถกอล์ฟประเภท {cart_type.value} ว่างไม่พอ")
            
            booking.assign_cart(cart)
            cart.assign_to_schedule(booking)
            available_carts.remove(cart)
            assigned_details.append(f"Cart: {cart.id} ({cart.type.value})")

    return {"message": "Add-ons Confirmed", "assigned": assigned_details}

@app.post("/user/booking/bill", tags=["User"])
def issue_payment(request: BillRequest):
    booking = sys.find_booking_by_id(request.booking_id)
    if not booking: raise HTTPException(404, "Booking not found")
    
    if len(booking.caddy_assignments) != len(booking.golfers):
        raise HTTPException(
            status_code=400, 
            detail=f"ไม่สามารถออกบิลได้! ต้องระบุแคดดี้ให้ครบแบบ 1:1 (ก๊วนนี้มี {len(booking.golfers)} คน แต่ระบุแคดดี้มา {len(booking.caddy_assignments)} คน) กรุณาทำรายการ Add-ons ก่อน"
        )
        
    raincheck_map = {rc.user_id: rc.code for rc in request.rainchecks if rc.code}
    
    hour = int(booking.slot.time.split(":")[0])
    green_fee = booking.slot.course.fee_morning if hour < 12 else booking.slot.course.fee_afternoon
    golfers_count = len(booking.golfers)
    
    individual_bills = []
    sub_total_amount = 0
    total_discount = 0

    for golfer in booking.golfers:
        member_discount = 0
        if isinstance(golfer, Member):
            if golfer.tier == Tier.PLATINUM: member_discount = green_fee * 0.20
            elif golfer.tier == Tier.GOLD: member_discount = green_fee * 0.10
            elif golfer.tier == Tier.SILVER: member_discount = green_fee * 0.05
            
        caddy_fee = 0
        my_caddy = booking.caddy_assignments.get(golfer.user_id)
        if my_caddy:
            caddy_fee = my_caddy.price
            
        cart_fee = 0
        if booking.carts:
            cart_fee = round(sum(c.price for c in booking.carts) / golfers_count, 2)

        rc_discount = 0
        rc_code = raincheck_map.get(golfer.user_id)
        
        # 📌 เช็คความถูกต้องของคูปองโดยอ้างอิงเบอร์โทรศัพท์
        if rc_code: 
            rc_discount = sys.validate_and_use_raincheck(rc_code, golfer.phone)
            if rc_discount == -1:
                raise HTTPException(400, f"คูปอง '{rc_code}' ไม่ถูกต้อง หรือไม่ได้เป็นสิทธิ์ของเบอร์โทร {golfer.phone}")
        
        net_total = max(0, green_fee - member_discount + caddy_fee + cart_fee - rc_discount)
        
        sub_total_amount += net_total
        total_discount += (member_discount + rc_discount)
        
        individual_bills.append({
            "name": golfer.name,
            "green_fee": green_fee,
            "member_discount": -member_discount,
            "caddy_fee": caddy_fee,
            "cart_fee": cart_fee,
            "raincheck_discount": -rc_discount,
            "net_total": net_total
        })
        
    breakdown = {
        "Session": "MORNING" if hour < 12 else "AFTERNOON",
        "Total_Discount_And_Vouchers": -total_discount,
        "Caddy_Fee_Total": sum(c.price for c in booking.caddy_assignments.values()),
        "Cart_Fee_Total": sum(c.price for c in booking.carts),
        "Grand_Total": sub_total_amount
    }
        
    pay_suffix = request.booking_id.split('-')[1] if '-' in request.booking_id else len(sys.payments) + 1
    pay_id = f"PAY-{pay_suffix}"
    
    sys.payments.append(Payment(pay_id, request.booking_id, sub_total_amount, breakdown, individual_bills))
    
    return {"paymentID": pay_id, "breakdown": breakdown, "individual_bills": individual_bills}

@app.post("/user/booking/pay", tags=["User"])
def pay_booking(
    payment_id: str = Query(..., description="รหัสชำระเงิน เช่น PAY-001"),
    method: PaymentMethod = Query(PaymentMethod.QR_CODE, description="เลือกช่องทางการชำระเงิน") # 📌 ตัวนี้จะกลายเป็น Dropdown
):
    """ยืนยันการชำระเงินสำหรับการจองสนามกอล์ฟ"""
    # เรียกใช้ Method ที่สร้างไว้ใน system
    result = sys.process_booking_payment(payment_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    if result["status"] == "FAILED":
        raise HTTPException(status_code=400, detail=result.get("message"))
        
    return result

@app.post("/user/booking/confirm", tags=["User"])
def confirm_booking(booking_id: str):
    booking = sys.find_booking_by_id(booking_id)
    if not booking: raise HTTPException(404, "Booking not found")
        
    payment = next((p for p in sys.payments if p.booking_id == booking_id), None)
    if not payment or payment.status != PaymentStatus.SUCCESS:
        raise HTTPException(400, "กรุณาชำระเงินก่อนยืนยัน")
        
    booking.set_status(BookingStatus.CONFIRMED_PAID)

    course_type = booking.slot.course.type.value
    msg = f"✅ ยืนยันสำเร็จ! คิวออกรอบสนาม {course_type} วันที่ {booking.slot.play_date} เวลา {booking.slot.time}"
            
    for golfer in booking.golfers:
        sys.create_notification(golfer, msg)
        
    return {"message": "Booking Confirmed!"}

@app.get("/user/notifications", tags=["User"])
def view_user_notifications(member_id: str = "M-001"):
    """User: เช็คกล่องข้อความแจ้งเตือนของตัวเองผ่าน Member ID"""
    
    # 1. ค้นหาตัวตนของผู้ใช้ในระบบ
    member = sys.find_user_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # 2. เรียกใช้เมธอด view_notifications() ตามที่ออกแบบไว้ใน Class Diagram
    if not isinstance(member, Member): #***เพิ่มเช็คว่าเป็น member ไม่ใช่ guest
        raise HTTPException(status_code=400, detail="Member not found")
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
def admin_create_tournament(name: str = "Green Valley Masters", date: str = "2024-12-01", fee: float = 2500.0):
    """Admin (Phase 0): สร้างรายการแข่งขันใหม่"""
    t_id = sys.create_tournament(name, date, fee)
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

# 🌧️ RAINCHECK -------------------------------------------------

@app.post("/admin/issue-raincheck", tags=["Admin"])
def issue_raincheck_by_booking(
    booking_id: str = Query(..., description="รหัส Booking (เช่น WK-001 หรือ BK-001)"),
    holes_played: int = Query(..., description="จำนวนหลุมที่เล่นไปแล้ว", ge=0, le=18)
):
    # ค้นหา Booking จากระบบ
    booking = next((b for b in sys.bookings if b.booking_id == booking_id), None)
    
    if not booking:
        raise HTTPException(status_code=404, detail=f"ไม่พบข้อมูล Booking รหัส '{booking_id}'")

    # ดึงค่า Green Fee จาก Booking โดยตรง
    base_green_fee = booking.slot.course.get_price_by_time(booking.slot.time)

    # คำนวณสัดส่วนการชดเชยตามกฎ
    if holes_played < 3:
        refund_rate = 1.00  # คืน 100%
    elif 3 <= holes_played <= 9:
        refund_rate = 0.50  # คืน 50%
    else:
        # มากกว่า 9 หลุม ไม่ออกสิทธิ์ชดเชย
        return {
            "message": "ลูกค้าเล่นไปมากกว่า 9 หลุมแล้ว ไม่เข้าเงื่อนไขการได้รับ Rain Check",
            "booking_id": booking.booking_id,
            "holes_played": holes_played,
            "refund_amount": 0
        }

    # คำนวณยอดเงินที่จะออกเป็นคูปองให้แต่ละคน
    amount_per_person = base_green_fee * refund_rate

    # วนลูปแจกคูปองให้ "ทุกคน" ใน Booking นี้
    issued_coupons = []
    
    for golfer in booking.golfers:
        # ระบบจะผูกเบอร์โทร และสร้าง Code ให้อัตโนมัติ
        new_rc = sys.issue_raincheck_to_user(golfer.user_id, amount_per_person)
        
        if new_rc:
            issued_coupons.append({
                "user_id": golfer.user_id,
                "name": golfer.name,
                "phone_linked": new_rc.phone, # ดึงเบอร์จากคูปอง
                "coupon_code": new_rc.code,   # รหัสคูปองเฉพาะบุคคล
                "amount": new_rc.amount       # มูลค่าคูปอง
            })

    return {
        "message": f"ออกคูปอง Rain Check สำเร็จ (ชดเชย {int(refund_rate * 100)}%)",
        "booking_id": booking.booking_id,
        "holes_played": holes_played,
        "base_green_fee": base_green_fee,
        "refund_per_person": amount_per_person,
        "total_golfers": len(issued_coupons),
        "coupons": issued_coupons
    }
    
# ==========================================
# หมวด System (ข้อมูลในระบบ)
# ==========================================

@app.get("/system/users", tags=["System"])
def get_all_users():
    """ดึงรายชื่อผู้ใช้งานทั้งหมดในระบบ (Member & Guest)"""
    user_list = []
    now = datetime.now()
    
    for u in sys.users:
        info = {
            "user_id": u.user_id,
            "name": u.name,
            "phone": u.phone
        }
        # 1. ถ้าเป็น Member ให้ดึง status, tier, strikes และอัปเดตแบน
        if isinstance(u, Member):
            # โค้ดเช็คเวลาปลดแบน
            if u.status == UserStatus.BANNED:
                if u.suspended_until and now >= u.suspended_until:
                    u.status = UserStatus.ACTIVE
            elif u.status == UserStatus.WEEKEND_BAN:
                if u.weekend_ban_until and now >= u.weekend_ban_until:
                    u.status = UserStatus.ACTIVE
            info.update({
                "role": "Member",
                "status": u.status.value,
                "tier": u.tier.value,
                "strikes": u.strikes,
                "my_rainchecks": [rc.code for rc in u.my_rainchecks] # แสดงคูปองที่มี
            })
        # 2. ถ้าเป็น Guest ให้แสดงค่าเป็น N/A
        else:
            info.update({
                "role": "Guest (Walk-in)",
                "status": "ACTIVE",
                "tier": "-",
                "strikes": 0,
                "my_rainchecks": [rc.code for rc in u.my_rainchecks] if hasattr(u, 'my_rainchecks') else []
            })
        user_list.append(info)
    
    return {
        "total_users": len(user_list),
        "data": user_list
    }
    
@app.get("/system/caddies", tags=["System"])
def get_caddy_profiles(date: str = Query(..., description="ระบุวันที่ (DD-MM-YYYY)"),
                       time: str = Query(..., description="ระบุเวลา (HH:MM)")):
    
    validate_search_date_range(date, time)
    
    if date and time:
        available_caddies = sys.find_available_caddies(date, time)
        return {"date_time": f"{date} {time}", "available_caddies": [{"id": c.id, "name": c.name, "level": c.level.value} for c in available_caddies]}
    return {"caddies": [{"id": c.id, "name": c.name, "level": c.level.value} for c in sys.caddies]}

@app.get("/system/golfcarts", tags=["System"])
def get_cart_profiles(date: str = Query(..., description="ระบุวันที่ (DD-MM-YYYY)"),
                      time: str = Query(..., description="ระบุเวลา (HH:MM)")):
    
    validate_search_date_range(date, time)
    
    if date and time:
        available_carts = sys.find_available_carts(date, time)
        return {"date_time": f"{date} {time}", "available_carts": [{"id": c.id, "type": c.type.value} for c in available_carts]}
    return {"carts": [{"id": c.id, "type": c.type.value} for c in sys.carts]}

@app.get("/system/bookings-history", tags=["System"])
def view_all_bookings():
    all_bookings = []
    for b in sys.bookings:
        all_bookings.append({
            "booking_id": b.booking_id,
            "status": b.status.value,
            "course": b.slot.course.name,
            "date": b.slot.play_date,
            "time": b.slot.time,
            "requester": f"{b.requester.name} ({b.requester.phone})",
            "golfers": [f"{g.name} ({g.phone})" for g in b.golfers],
            "assigned_caddies": [c.name for c in b.caddy_assignments.values()],
            "assigned_carts": [c.id for c in b.carts]
        })
    return {"total_bookings": len(all_bookings), "bookings": all_bookings}
    
