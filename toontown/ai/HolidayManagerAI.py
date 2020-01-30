from datetime import datetime

class HolidayManagerAI:
    date = datetime.today()

    def isHalloween(self):
        if config.GetBool('want-halloween', False):
            return True
        return self.date.month == 10 and self.date.day >= 19

    def isWinter(self):
        if config.GetBool('want-winter', False):
            return True
        return self.date.month == 12 or self.date.month == 1 and self.date.day <= 13

    def isAprilToons(self):
        if config.GetBool('want-april-toons', False):
            return True
        return self.date.month == 4 and self.date.day <= 7
