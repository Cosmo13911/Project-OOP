from pydantic import BaseModel, Field
from typing import List
from course import CourseType

class RaincheckInput(BaseModel):
    user_id: str = Field(..., description="รหัสผู้เล่นที่ต้องการใช้คูปอง")
    code: str = Field(..., description="รหัสคูปอง")

class BillRequest(BaseModel):
    booking_id: str = Field(default="XK-000", description="รหัสใบจอง")
    rainchecks: List[RaincheckInput] = Field(
        default=[RaincheckInput(user_id="string", code="RC-000")], 
        description="รายการคูปองที่ต้องการใช้ (ถ้าไม่มีให้ปล่อยว่าง [])"
    )
    
class WalkInRequest(BaseModel):
    guest_name: str = Field(..., description="ชื่อหัวหน้าก๊วน")
    phone: str = Field(..., description="เบอร์โทรศัพท์หัวหน้าก๊วน")
    course_type: CourseType = CourseType.CHAMPIONSHIP
    date: str = Field(..., description="วันที่ (DD-MM-YYYY)")
    time: str = Field(..., description="เวลาที่ต้องการออกรอบ")
    companion_phones: List[str] = Field(default=[], description="เบอร์โทรศัพท์เพื่อนร่วมก๊วน (ถ้ามี)")