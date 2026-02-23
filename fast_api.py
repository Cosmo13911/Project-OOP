from system import GreenValleySystem
from fastapi import FastAPI

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

@app.get("/view/notibooking", tags=["User"])
def view_notification():
    john.view_notifications()[0] if john.view_notifications() else "No notifications"
    return {"Notification":    john.view_notifications()[0] if john.view_notifications() else "No notifications"
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
