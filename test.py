# test.py pull test
from system import GreenValleySystem

def run_test():
    # 1. เริ่มต้นระบบและโหลดข้อมูล (John และ Mary จะถูกสร้างอัตโนมัติ)
    sys = GreenValleySystem()
    sys.create_data()
    
    print("\n" + "="*40)
    print(" STEP 1: VERIFYING GOLFER DATA")
    print("="*40)
    for u in sys.users:
        print(f"Name: {u.name} | Handicap: {u.current_handicap} | Tier: {u.tier.name}")

    print("\n" + "="*40)
    print(" STEP 2: BOOKING PROCESS")
    print("="*40)
    
    # ทดสอบการจองที่ 1: John Doe จอง Slot แรก
    print("[Action] John Doe is trying to book Slot 1...")
    sys.create_booking(member_index=0, course_index=0, slot_index=0) 

    # ทดสอบการจองที่ 2: Mary Jane ลองจอง Slot แรก (ซ้ำกับ John)
    print("\n[Action] Mary Jane is trying to book Slot 1 (Double Booking Test)...")
    sys.create_booking(member_index=1, course_index=0, slot_index=0)

    # ทดสอบการจองที่ 3: Mary Jane เปลี่ยนไปจอง Slot ที่สอง
    # (หมายเหตุ: ใน data.py ต้องสร้าง slot ไว้ 2 อันนะถึงจะจองอันที่สองได้)
    if len(sys.courses[0].slots) > 1:
        print("\n[Action] Mary Jane is trying to book Slot 2...")
        sys.create_booking(member_index=1, course_index=0, slot_index=1)

    print("\n" + "="*40)
    print(" STEP 3: SYSTEM SUMMARY (WHO BOOKED WHAT?)")
    print("="*40)
    
    if not sys.bookings:
        print("No bookings found in the system.")
    else:
        for b in sys.bookings:
            # ดึงข้อมูลจาก object Booking มาโชว์
            print(f"Booking ID: {b.booking_id}")
            print(f" - Player: {b.requester.name} (Tier: {b.requester.tier.name})")
            print(f" - Course: {b.slot.course.name}")
            print(f" - Tee Time: {b.slot.play_date}")
            print(f" - Booking Status: {b.slot.status.name}")
            print("-" * 20)

    for b in sys.bookings:
        print(f"Booking ID: {b.booking_id} | Requester: {b.requester.name} | Slot: {b.slot.play_date} | Golfers in Booking: {[g.name for g in b.golfers]}")
    
    # test.py (ส่วนต่อจากเดิม)

    print("\n" + "="*50)
    print(" TEST #4: MEMBER PLACING FOOD ORDER")
    print(" (Using Dependency Injection via Member Object)")
    print("="*50)

    # 1. เตรียมข้อมูลที่จำเป็น
    john = sys.users[0]             # ดึงออบเจกต์ Member (John Doe)
    fried_rice = sys.find_product_by_id("P001")    # ดึงออบเจกต์ Product (Fried Rice)
    b_id = sys.bookings[0].booking_id # ดึงเลขที่การจองที่ John ทำไว้

    # 2. เริ่มการสั่งอาหารผ่านตัวออบเจกต์ Member โดยตรง
    # สังเกตว่าเราส่ง 'sys' เข้าไปเป็นตัวแปรแรก เพื่อให้ john นำไปสั่งงานต่อได้
    print(f"[Request] {john.name} wants to order {fried_rice.name}...")

    order_success = john.place_order(
        system=sys,          # ส่งออบเจกต์ System เข้าไป (นี่คือหัวใจสำคัญ)
        booking_id=b_id,     # เลขที่การจอง
        product=fried_rice,  # ออบเจกต์สินค้า
        quantity=1           # จำนวน
    )

    # 3. ตรวจสอบผลลัพธ์ที่เกิดขึ้นในระบบหลัก (sys)
    if order_success:
        print("\n--- Current System State After Test #4 ---")
        # ตรวจสอบว่า Order ล่าสุดถูกเพิ่มเข้าไปในลิสต์ของระบบหรือไม่
        latest_order = sys.bookings[0].view_orders[-1] if sys.bookings[0].view_orders else None
        if latest_order:
            print(sys.bookings[0].view_orders[-1].total_price)  # แสดงรายละเอียด Order ล่าสุด
        else:
            print("Error: No orders found in the booking.")
    else:
        print("Test #4 Failed: Order could not be placed.")

    print("\n" + "="*50)
    print(" TEST #5: VIEW MEMBER NOTIFICATIONS")
    print(" (Using Dependency Injection via Member Object)")
    print("="*50)

    print(f"Notifications for {john.name}:")
    for n in john.view_notifications():
        print(f" - {n}")

    print("\n" + "="*50)
    print(" TEST #6: TOURNAMENT REGISTRATION & PAIRING")
    print("="*50)
    
    # ดึง Tournament ID จากระบบ (สร้างไว้แล้วใน create_data)
    tour_id = "T-001" 
    print(f"[System] Initiating Tournament: {tour_id}")

    # ให้สมาชิก 4 คนแรกสมัครแข่ง
    competitors = ["M-001", "M-002", "M-003", "M-004"]
    for member_id in competitors:
        # 1. กดสมัครรับบิล
        res = sys.register_tournament_get_payment(member_id, tour_id)
        if "paymentID" in res:
            # 2. จ่ายเงิน
            sys.process_payment(res["paymentID"])
            print(f"✅ Player {member_id} registered & paid successfully.")
        else:
            print(f"❌ Error for {member_id}: {res}")

    # ปิดรับสมัครและจัดก๊วน
    print("\n[Action] Closing Registration and generating Pairings...")
    close_result = sys.close_registration_and_pairing(tour_id)
    print(close_result)


    print("\n" + "="*50)
    print(" TEST #7: SIMULATING 18-HOLES SCORES & LEADERBOARD")
    print("="*50)
    
    print("[System] Auto-generating fixed scores for 18 holes...")
    # จำลองการตี 18 หลุม (ใส่คะแนนแบบตายตัว ไม่ใช้ random)
    for hole in range(1, 19):
        # Tiger Woods (M-001) ตีเก่งมาก ให้หลุมละ 3 สโตรก (รวม 18 หลุม = 54)
        sys.record_tournament_score(tour_id, "M-001", hole, 3) 
        
        # John Doe (M-002) ตีกลางๆ ให้หลุมละ 4 สโตรก (รวม 18 หลุม = 72)
        sys.record_tournament_score(tour_id, "M-002", hole, 4) 
        
        # Mary Jane (M-003) มือใหม่ ให้หลุมละ 6 สโตรก (รวม 18 หลุม = 108)
        sys.record_tournament_score(tour_id, "M-003", hole, 6) 
        
        # Arthit (M-004) ให้หลุมละ 5 สโตรก (รวม 18 หลุม = 90)
        sys.record_tournament_score(tour_id, "M-004", hole, 5) 

    print("✅ All 18 holes recorded successfully!\n")

    # ดึง Leaderboard
    leaderboard = sys.get_tournament_leaderboard(tour_id)
    
    # พิมพ์ตาราง Leaderboard โชว์
    print(f"{'RANK':<6} | {'PLAYER NAME':<20} | {'HCP':<5} | {'GROSS':<6} | {'NET SCORE':<10}")
    print("-" * 60)
    if leaderboard:
        for row in leaderboard:
            rank = row.get("rank_no", "-")
            name = row.get("member_name", "Unknown")
            hcp = row.get("handicap", 0)
            gross = row.get("gross_score", 0)
            net = row.get("net_score", 0)
            print(f"{rank:<6} | {name:<20} | {hcp:<5} | {gross:<6} | {net:<10}")
    else:
        print("Leaderboard is empty or error generating.")

    print("\n" + "="*40)
    print(" TEST COMPLETED")
    print("="*40)

if __name__ == "__main__":
    run_test()
