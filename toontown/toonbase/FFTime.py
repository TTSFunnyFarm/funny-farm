from datetime import datetime

def isHalloween():
	date = datetime.today()
	if date.month == 10 and date.day >= 18:
		return True
	return False

def isWinter():
	date = datetime.today()	
	if date.month == 12 or date.month == 1 and date.day <= 10:
		return True
	return False

def isValentines():
	date = datetime.today()
	if date.month == 2 and date.day >= 1 and date.day <= 14:
		return True
	return False
