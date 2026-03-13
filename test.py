from system import GreenValleySystem
from models.enum import BookingStatus

def run_raincheck_test_2_players():
    sys = GreenValleySystem()
    sys.create_data()
    
    print("--- Phase: Rain Check Test with 2 Players ---")

    # 1. ค้นหาผู้ใช้ (M-001 เป็นคนจอง, M-002 เป็นเพื่อนร่วมก๊วน)
    jennie = sys.find_user("M-001")
    praw = sys.find_user("M-002")

    # 2. ออก Rain Check ให้ Jennie เตรียมไว้ 1,000 บาท
    # (สมมติว่า Jennie เคยมาจองแล้วฝนตก เลยได้รับคูปองผูกกับเบอร์โทรของเธอ)
    print("\n[1] Issuing Rain Check to Jennie (M-001)...")
    rc_voucher = sys.issue_raincheck_to_user("M-001", 1000.0)
    print(f"Issued Voucher: {rc_voucher.code} | Value: {rc_voucher.amount:,.2f} THB")

    # 3. สร้างการจองใหม่สำหรับ 2 คน (Jennie และ Praw)
    print("\n[2] Creating a NEW booking for 2 golfers (Jennie & Praw)...")
    # ใส่ companion_ids=["M-002"] เพื่อให้มี 2 คนในก๊วน
    new_booking = sys.create_booking(
        requester_id="M-001", 
        course_id="C-002", 
        date="2026-03-15", 
        time="08:00", 
        companion_ids=["M-002"]
    )
    print(f"Booking ID: {new_booking.booking_id} | Golfers: {[g.name for g in new_booking.golfers]}")

    # 4. ประมวลผลการชำระเงินโดยใช้ Rain Check ของ Jennie
    print("\n[3] Processing payment using Jennie's Rain Check...")
    
    # เรียกใช้ process_payment ซึ่งภายในจะไปเรียก calculate_total_price
    # ยอดรวมจะคำนวณจาก (ราคา Jennie + ราคา Praw + Add-ons) - 1000
    payment_result = sys.process_payment(
        booking=new_booking, 
        rain_check_code=rc_voucher.code
    )
    
    # แตกค่า Tuple ที่ได้กลับมา (total_price, msg_details)
    total_to_pay, details = payment_result    

    for pay in sys.payments:
        print(f"{pay.get_transaction_details()}")

    # 5. ตรวจสอบใน List Payments ของระบบ
    print("\n[4] Verifying Payment Record in System:")
    for payment in sys.payments:
        if payment.payment_id.startswith("PAY-") and "BOOKING" in payment.get_type:
            print(f"Payment ID: {payment.payment_id} | Amount: {payment.amount:,.2f} THB | Status: {payment.status}")

    print("\n--- Test Completed ---")

if __name__ == "__main__":
    run_raincheck_test_2_players()