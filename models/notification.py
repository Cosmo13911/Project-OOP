from datetime import datetime

class Notification:
    def __init__(self, message: str):
        # Attribute เป็น Private ตามข้อกำหนด
        self.__message = message
        self.__timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def message(self):
        return self.__message

    @property
    def time(self):
        return self.__timestamp
