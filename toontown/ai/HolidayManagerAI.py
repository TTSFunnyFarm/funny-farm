from datetime import datetime

class HolidayManagerAI:

    def isHalloween(self):
        date = datetime.today()
        if date.month == 10 and date.day >= 18:
            return True
        return False

    def isWinter(self):
        date = datetime.today()
        if date.month == 12 or date.month == 1 and date.day <= 10:
            return True
        return False
