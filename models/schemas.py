from fastapi import Query

class ScoreSubmission:
    def __init__(
        self,
        # ช่องกรอกหลุม 1: เริ่มต้นที่ 0, ห้ามติดลบ, ห้ามเกิน 15
        hole1: int = Query(0, ge=0, le=15, description="คะแนนหลุม 1"),
        hole2: int = Query(0, ge=0, le=15, description="คะแนนหลุม 2"),
        hole3: int = Query(0, ge=0, le=15, description="คะแนนหลุม 3"),
        hole4: int = Query(0, ge=0, le=15, description="คะแนนหลุม 4"),
        hole5: int = Query(0, ge=0, le=15, description="คะแนนหลุม 5"),
        hole6: int = Query(0, ge=0, le=15, description="คะแนนหลุม 6"),
        hole7: int = Query(0, ge=0, le=15, description="คะแนนหลุม 7"),
        hole8: int = Query(0, ge=0, le=15, description="คะแนนหลุม 8"),
        hole9: int = Query(0, ge=0, le=15, description="คะแนนหลุม 9"),
        hole10: int = Query(0, ge=0, le=15, description="คะแนนหลุม 10"),
        hole11: int = Query(0, ge=0, le=15, description="คะแนนหลุม 11"),
        hole12: int = Query(0, ge=0, le=15, description="คะแนนหลุม 12"),
        hole13: int = Query(0, ge=0, le=15, description="คะแนนหลุม 13"),
        hole14: int = Query(0, ge=0, le=15, description="คะแนนหลุม 14"),
        hole15: int = Query(0, ge=0, le=15, description="คะแนนหลุม 15"),
        hole16: int = Query(0, ge=0, le=15, description="คะแนนหลุม 16"),
        hole17: int = Query(0, ge=0, le=15, description="คะแนนหลุม 17"),
        hole18: int = Query(0, ge=0, le=15, description="คะแนนหลุม 18")
    ):
        # เก็บใส่ Dictionary ไว้ให้หลังบ้าน (System) วนลูปใช้ง่ายๆ
        self.scores = {
            1: hole1, 2: hole2, 3: hole3, 4: hole4, 5: hole5, 6: hole6,
            7: hole7, 8: hole8, 9: hole9, 10: hole10, 11: hole11, 12: hole12,
            13: hole13, 14: hole14, 15: hole15, 16: hole16, 17: hole17, 18: hole18
        }

    def get_score(self, hole_num):
        return self.scores.get(hole_num, 0)