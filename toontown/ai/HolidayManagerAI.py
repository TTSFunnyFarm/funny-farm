from datetime import datetime

class HolidayManagerAI:

    def isHalloween(self):
        if config.GetBool('want-halloween', False):
            return True
        date = datetime.today()
        if date.month == 10 and date.day >= 18:
            return True
        return False

    def isWinter(self):
        if config.GetBool('want-winter', False):
            return True
        date = datetime.today()
        if date.month == 12 or date.month == 1 and date.day <= 10:
            return True
        return False
