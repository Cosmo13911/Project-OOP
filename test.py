# แยกไฟล์ตามข้อกำหนด: Code ต้องอยู่ในไฟล์ 2 ไฟล์ขึ้นไป [cite: 21
from system import GreenValleySystem

def run_system_test():
    # 1. เริ่มต้น Controller (Controller Class เพียง 1 Class ตามเกณฑ์) [cite: 9]
    system = GreenValleySystem()
    
    print("--- Phase A: Data Initialization & Discovery ---")
    # สร้างข้อมูลเริ่มต้น (Users 8 คน, 2 สนาม, สินค้า/บริการ)
    system.create_data()

    jennie = system.find_user("M-001")
    praw = system.find_user("M-002")
    
    # 2. ทดสอบการดูข้อมูล User (Entity Class ต้องมี ID) [cite: 10, 11]
    print("\n[1] user in system:")
    users = system.users # Method ใน Controller
    for u in users:
        print(f"ID: {u.id} | Name: {u.name} | Tier: {u.tier}")

    # 3. ทดสอบการดูข้อมูลสนามและสินค้า (Entity Class ที่ระบุจำนวนที่เหลือได้) [cite: 11]
    print("\n[2] Golf Courses:")
    for course in system.get_all_courses:
        print(f"Course: {course.name} ({course.type})")

    print("\n[3] Products (Limited Quantity):")
    for prod in system.products:
        print(f"Product: {prod.name} | Price: {prod.price} | Remaining: {prod.stock}")

    print("\n--- Phase B: Booking Operations (Logic Test) ---")
    # 4. ทดสอบการจอง (Transaction Class) [cite: 8]
    # Scenario: Jennie (M-001) จองสนาม Championship ช่วงเช้า
    print("[4] Booking for Jennie...")
    booking1 = system.create_booking("M-001", "C-001", "2026-03-10", "08:00")
    print(f"testsssssssss {len(booking1.golfers)}")
    print(f"testsssssssss {(booking1.golfers)}")
    if not booking1: print("Booking failed for Jennie.")
    for noti in jennie.get_notifications:
        print(f"{noti.time} | Notification for Jennie: {noti.message}")    
    # 5. ทดสอบ Error Handling & Validation (Input Validation) [cite: 19, 20]
    # Scenario: Praw (M-002) พยายามจองเวลาเดียวกับ Jennie (Slot ไม่ว่าง)
    print("\n[5] Test booking same time (Error Handling Test):")
    try:
        booking2 = system.create_booking("M-002", "C-001", "2026-03-10", "08:00") 
    except ValueError as e:
        print(f"Error: {e}")
    # ระบบควรแจ้งว่า SlotStatus.RESERVED แล้ว และใช้ Try-Except จัดการ 

    print("\n--- Phase C: Billing & Status Tracking ---")
    # 6. ตรวจสอบรายละเอียดการจองและสถานะ (Status Tracking > 3 สถานะ) [cite: 12]
    if booking1:
        print(f"[6] Booking details ID: {booking1.booking_id}")
        print(f"Status: {booking1.status}") # เช่น PENDING -> CONFIRMED [cite: 12]
        
        # แสดงองค์ประกอบค่าใช้จ่าย (อย่างน้อย 4 รายการ) 
        print(booking1.get_all_addons)
        

    print("--- Phase D: Personal Booking & Notifications ---")
    
    # 7. ทดสอบการดูการจองส่วนตัว (User ควรดูการจองของตัวเองได้)
    # Jennie (M-001) ดูรายการจองของตนเอง
    print("\n[7] View Bookings for Jennie (M-001):")
    jennie_bookings = system.find_booking("BK-001")
    if jennie_bookings:
            # ตรวจสอบสถานะการจอง (สถานะต้องมีอย่างน้อย 3 สถานะตามเกณฑ์)
        print(f"Booking ID: {jennie_bookings.booking_id} | Status: {jennie_bookings.status}")
    else:
        print("No bookings found for Jennie.")

    # 8. ทดสอบระบบ Notification (Class Notification & Object Storage)
    # จำลองเหตุการณ์: มีการสั่งสินค้าและระบบส่งแจ้งเตือน
    print("\n[8] Test Ordering & Notifications:")
    # ตรวจสอบก่อนสั่งซื้อ (Entity Class ที่ระบุจำนวนที่เหลือได้)
    prod = system.find_product("P-001")
    if prod:
        print(f"Before Order - {prod.name} Stock: {prod.stock}")
        
    # สั่งซื้อสินค้าผ่าน Controller (ใช้ Try-Except ตามเกณฑ์)
    order_result = system.place_order("BK-001", "P-001", 2)
    print(f"Order Result: {order_result}")
    
    # ตรวจสอบสต็อกหลังสั่งซื้อ
    if prod:
        print(f"After Order - {prod.name} Stock: {prod.stock}")

    # ตรวจสอบ Notification ของ Jennie (ต้องเก็บเป็น Object Notification)
    print("\nNotifications for Jennie:")
    notifications = jennie.get_notifications
    for noti in notifications:
        # แสดงรายละเอียดจาก Object Notification (Message + Timestamp)
        print(f"[{noti.time}] Message: {noti.message}")

    print("\n--- Phase E: Advanced Error Handling & Validation ---")

    # 9. ทดสอบ Input Validation (Guard Clauses)
    print("\n[9] Test Invalid Inputs:")
    try:
        # เคส: ไม่ระบุข้อมูลสำคัญ (Input Validation ทุกแห่งตามเกณฑ์)
        system.create_booking("", "C-001", "2026-03-10", "08:00")
    except ValueError as e:
        print(f"Caught Expected Error (Validation): {e}")

    # 10. ทดสอบการจำกัดจำนวน (Business Rules - สต็อกสินค้าไม่พอ)
    print("\n[10] Test Out of Stock Scenario:")
    # พยายามสั่งน้ำดื่ม 5000 ขวด (เกินสต็อกที่มี 1000)
    try:
        out_of_stock_test = system.place_order("BK-001", "P-002", 5000)
    except ValueError as e:
        print(f"Caught Expected Error (Out of Stock): {e}")

    print("\n--- Phase F: Full Tournament Operations ---")
    # 11. สร้าง Tournament (Entity Class)
    print("[11] Creating Tournament...")
    tour_info = system.create_tournament("Singha Open 2026", "2026-03-15", 1500, "C-001")
    tour_id = tour_info["tournamentID"]
    print(f"Tournament Created: {tour_id} at {tour_info['course_assigned']}")

    # 12. จำลองการสมัครและจ่ายเงินครบ 8 คน (M-001 ถึง M-008)
    print("\n[12] Registering 8 players and processing payments...")
    member_ids = [f"M-00{i}" for i in range(1, 9)]
    for m_id in member_ids:
        # จำลอง Payment ID สำหรับ Tournament
        payment_id = f"PAY-{m_id}-{tour_id}"
        payment_result = system.process_payment(payment_id)
        # ตรวจสอบ Notification การจ่ายเงิน (Requirement: แจ้งเตือนการชำระเงินเสร็จสิ้น)
        member = system.find_user(m_id)
        last_noti = member.get_notifications[-1]
        print(f"Player {member.name}: {payment_result['message']} | Noti: {last_noti.message}")

    # 13. ปิดรับสมัครและจับคู่พร้อมระบุเวลาแข่ง (Requirement: close_and_pair พร้อมเวลา)
    print("\n[13] Closing registration and generating pairings with Tee Times...")
    pairing_result = system.close_registration_and_pairing(tour_id)
    print(f"Pairing Result: {pairing_result}")

    # ตรวจสอบการแจ้งเตือนรอบเวลาแข่ง (Requirement: ส่งบอกใน Notification ว่าแข่งรอบไหน)
    print("\n[Checking Tee Time Notifications for Group 1]:")
    for i in range(1, 5):
        m = system.find_user(f"M-00{i}")
        # ดึง Notification ล่าสุดที่เป็นเรื่องเวลาแข่ง
        tee_time_noti = m.get_notifications[-1]
        print(f"Player: {m.name} | Notification: {tee_time_noti.message}")

    # 14. บันทึกคะแนนแบบสุ่ม 18 หลุม (Requirement: ใส่คะแนนแบบสุ่มให้ทุกคนครบ)
    # เปลี่ยนสถานะเป็น IN_PROGRESS เพื่อเริ่มบันทึกคะแนน
    tour = system.find_tournament(tour_id)
    from models.enum import TournamentStatus
    tour.update_status(TournamentStatus.IN_PROGRESS)

    print("\n[14] Recording random scores for 18 holes (List of ScoreRecord Objects)...")
    import random
    for m_id in member_ids:
        for hole in range(1, 19):
            random_stroke = random.randint(1, 8)
            # บันทึกคะแนนลงใน List ภายใน Scorecard
            system.record_tournament_score(tour_id, m_id, hole, random_stroke)
    print("Scoring completed for all players.")

    # # 15. แสดง Leaderboard (Requirement: แสดงบน leaderboard)
    # print("\n[15] Tournament Leaderboard:")
    # leaderboard = system.get_tournament_leaderboard(tour_id)
    # print(f"Status: {leaderboard['status']}")
    # print(f"{'Name':<10} | {'Gross':<6} | {'Net':<6}")
    # print("-" * 35)
    # for entry in leaderboard['leaderboard']:
    #     print(f"{entry['name']:<10} | {entry['gross']:<6} | {entry['net']:<6}")

    # 16. จบการแข่งขันและอัปเดต Handicap
    print("\n[16] Ending Tournament and Updating Handicaps...")
    # เปลี่ยนสถานะกลับเป็น DRAW_PUBLISHED ตามเงื่อนไข end_tournament ดั้งเดิม
    tour.update_status(TournamentStatus.DRAW_PUBLISHED)
    end_summary = system.end_tournament(tour_id)
    print(f"Result: {end_summary['message']}")
    for update in end_summary['players_updated']:
        print(f"Handicap Update: {update}")

    print("\n--- All Tournament Phases Completed ---")

    print("\n--- Test Completed ---")

if __name__ == "__main__":
    run_system_test()