# test.py
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

    print("\n" + "="*40)
    print(" TEST COMPLETED")
    print("="*40)

if __name__ == "__main__":
    run_test()