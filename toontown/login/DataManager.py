from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toon import ToonDNA
from toontown.toon.LocalToon import LocalToon
from toontown.login.Account import Account
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
import __builtin__
import yaml.dist as yaml
import os

# NOTE: The encrypt() and decrypt() functions should only be called in THIS FILE to avoid confusion and repitition.

class DataManager:
	notify = directNotify.newCategory('DataManager')

	def __init__(self):
		self.account = None
		self.maxAccounts = False
		self.fileExt = '.yaml'
		self.oldDir = Filename.getUserAppdataDirectory() + '/FunnyFarm/'
		self.newDir = Filename.getUserAppdataDirectory() + '/FunnyFarm' + '/db/'
		self.accounts = [
			1000000, 
			2000000, 
			3000000, 
			4000000, 
			5000000
		]
		self.toons = {
			'1000000' : [1100000, 1200000, 1300000, 1400000, 1500000, 1600000],
			'2000000' : [2100000, 2200000, 2300000, 2400000, 2500000, 2600000],
			'3000000' : [3100000, 3200000, 3300000, 3400000, 3500000, 3600000],
			'4000000' : [4100000, 4200000, 4300000, 4400000, 4500000, 4600000],
			'5000000' : [5100000, 5200000, 5300000, 5400000, 5500000, 5600000]
		}
		self.removeOldData()
		return

	def removeOldData(self):
		filename = Filename(self.oldDir + 'data.json')
		if os.path.exists(filename.toOsSpecific()):
			self.notify.warning('Deprecated data found. Removing...')
			os.remove(filename.toOsSpecific())

	def getAccountFilename(self, playToken):
		for file in self.accounts:
			filename = Filename(self.newDir + str(file) + self.fileExt)
			if os.path.exists(filename.toOsSpecific()):
				with open(filename.toOsSpecific(), 'r') as accFile:
					account = yaml.load(accFile)
					account.decrypt()
					if account.username == playToken:
						return filename
		return None

	def getToonFilename(self, index, playToken):
		accFile = self.getAccountFilename(playToken).getBasenameWoExtension()
		filename = Filename(self.newDir + str(self.toons[accFile][index - 1]) + self.fileExt)
		if os.path.exists(filename.toOsSpecific()):
			return filename
		return None

	def checkToonFiles(self, playToken):
		accFile = self.getAccountFilename(playToken).getBasenameWoExtension()
		for file in self.toons[accFile]:
			filename = Filename(self.newDir + str(file) + self.fileExt)
			if os.path.exists(filename.toOsSpecific()):
				return True
		return False

	def saveToonData(self, data, playToken):
		accFile = self.getAccountFilename(playToken).getBasenameWoExtension()
		index = data.index
		filename = Filename(self.newDir + str(self.toons[accFile][index - 1]) + self.fileExt)
		if not os.path.exists(filename.toOsSpecific()):
			filename.makeDir()
		with open(filename.toOsSpecific(), 'w') as toonData:
			data.encrypt()
			yaml.dump(data, toonData, default_flow_style=False)
			data.decrypt()
		return

	def loadToonData(self, index, playToken):
		accFile = self.getAccountFilename(playToken).getBasenameWoExtension()
		filename = Filename(self.newDir + str(self.toons[accFile][index - 1]) + self.fileExt)
		if os.path.exists(filename.toOsSpecific()):
			with open(filename.toOsSpecific(), 'r') as toonData:
				data = yaml.load(toonData)
				data.decrypt()
			return data
		return None

	def deleteToonData(self, index, playToken):
		accFile = self.getAccountFilename(playToken).getBasenameWoExtension()
		filename = Filename(self.newDir + str(self.toons[accFile][index - 1]) + self.fileExt)
		if os.path.exists(filename.toOsSpecific()):
			os.remove(filename.toOsSpecific())

	def createAccount(self, playToken):
		self.account = Account()
		self.account.setUsername(playToken)
		self.account.setAccessLevel(1250935)
		for file in self.accounts:
			filename = Filename(self.newDir + str(file) + self.fileExt)
			if not os.path.exists(filename.toOsSpecific()):
				filename.makeDir()
				with open(filename.toOsSpecific(), 'w') as accFile:
					self.account.encrypt()
					yaml.dump(self.account, accFile, default_flow_style=False)
				return
		self.notify.warning('Cannot create account. Maximum number of accounts exist. Notifying user..')
		self.maxAccounts = True
		messenger.send('accountError')

	def loadAccount(self, playToken):
		self.maxAccounts = False
		accFile = self.getAccountFilename(playToken).getBasename()
		filename = Filename(self.newDir + accFile)
		if os.path.exists(filename.toOsSpecific()):
			with open(filename.toOsSpecific(), 'r') as account:
				self.account = yaml.load(account)
				self.account.decrypt()
			return self.account

	def loadAccountByIndex(self, index):
		filename = Filename(self.newDir + str(index) + self.fileExt)
		if os.path.exists(filename.toOsSpecific()):
			with open(filename.toOsSpecific(), 'r') as account:
				account = yaml.load(account)
				account.decrypt()
			return account

	def createLocalAvatar(self, data):
		base.localAvatar = LocalToon()
		base.avatarData = data
		__builtin__.localAvatar = base.localAvatar
		dna = ToonDNA.ToonDNA()
		dna.newToonFromProperties(*data.setDNA)
		base.localAvatar.setDNA(dna)
		base.localAvatar.setName(data.setName)
		base.localAvatar.startBlink()
		base.localAvatar.setHealth(data.setHp, data.setMaxHp)
		# Each update is gonna mean a new try statement, so try to fit in as much data values that we have planned for the future.
		try:
			base.localAvatar.setMoney(data.setMoney)
			base.localAvatar.setMaxMoney(data.setMaxMoney)
			base.localAvatar.setBankMoney(data.setBankMoney)
			base.localAvatar.setMaxBankMoney(data.setMaxBankMoney)
			base.localAvatar.setNametagFont(FunnyFarmGlobals.getVar(data.setNametagStyle))
			base.localAvatar.setCheesyEffect(data.setCheesyEffect)
		except:
			base.localAvatar.setMoney(0)
			base.localAvatar.setMaxMoney(40)
			base.localAvatar.setBankMoney(0)
			base.localAvatar.setMaxBankMoney(12000)
			base.localAvatar.setNametagFont(ToontownGlobals.getSignFont())
			base.localAvatar.setCheesyEffect(ToontownGlobals.CENormal)
		base.localAvatar.setHat(*data.setHat)
		base.localAvatar.setGlasses(*data.setGlasses)
		base.localAvatar.setBackpack(*data.setBackpack)
		base.localAvatar.setShoes(*data.setShoes)
		base.localAvatar.setAccessLevel(self.account.getAccessLevel())
		if self.account.getAccessLevel() in [100, 200, 300]:
			base.localAvatar.setGMIcon()


