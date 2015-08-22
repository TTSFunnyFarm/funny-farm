from pandac.PandaModules import *
from direct.distributed.ClientRepository import ClientRepository
from direct.interval.IntervalGlobal import *
from toontown.login.PickAToon import PickAToon
from toontown.toontowngui import TTDialog
from toontown.toonbase import FunnyFarmGlobals
from otp.otpbase import OTPLocalizer
from toontown.login import Login
import PlayGame
import os
import sys

class FFClientRepository(ClientRepository):
	dcFiles = ['dc/direct.dc']

	def __init__(self):
		ClientRepository.__init__(self, dcFileNames=self.dcFiles, connectMethod=self.CM_NET)
		self.setTcpHeaderSize(4)
		self.notify.setInfo(True)
		self.connectDialog = None
		self.login = None
		self.avChooser = None
		self.playGame = PlayGame.PlayGame()
		self.notify.info('Running game on localhost.')
		#self.url = URLSpec('http://127.0.0.1:12070')
		#self.connect([self.url], successCallback=self.connectSuccessMsg, failureCallback=self.connectFailureMsg)

	def fakeConnect(self):
		Sequence(
			Func(self.showConnectDialog),
			Wait(2),
			Func(self.destroyConnectDialog),
			Func(self.enterPAT)
		).start()

	def showConnectDialog(self):
		self.connectDialog = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.NoButtons, text=OTPLocalizer.CRConnecting)
		self.connectDialog.show()

	def destroyConnectDialog(self):
		if self.connectDialog:
			self.connectDialog.destroy()
			self.connectDialog = None
		
	def connectSuccessMsg(self):
		self.notify.info('Successfully connected to gameserver.')
		self.setInterestZones([1])

	def connectFailureMsg(self, statusCode, statusString):
		self.notify.info('Failed to connect to gameserver.')
		print statusCode
		print statusString
		self.lostConnection()

	def lostConnection(self):
		if self.avChooser:
			self.exitPAT()
		if loader.inBulkBlock:
			loader.abortBulkLoad()

		self.notify.warning('Lost connection to gameserver. Notifying user.')
		soundMgr.stopAllMusic()
		render.hide()
		aspect2d.hide()
		dialog = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.Acknowledge, text=OTPLocalizer.CRLostConnection, text_wordwrap=18, fadeScreen=0.5, command=sys.exit)
		dialog.show()

	def enterLogin(self):
		self.login = Login.Login()
		self.login.load()
		self.login.enter()

	def loadPAT(self):
		self.avChooser = PickAToon()
		self.avChooser.load()

	def enterPAT(self):
		base.transitions.noTransitions()
		if not self.avChooser:
			self.loadPAT()
		self.avChooser.enter()

	def exitPAT(self):
		base.transitions.noTransitions()
		self.avChooser.exit()
		self.avChooser = None

	def finishMAT(self, tutorial):
		if tutorial:
			self.exitPAT()
			self.playGame.enterTutorial()
			base.localAvatar.reparentTo(render)
			base.localAvatar.setupControls()
			base.localAvatar.initInterface()
			base.localAvatar.addActive()
		else:
			self.enterTheTooniverse(FunnyFarmGlobals.FunnyFarm)

	def enterHood(self, zoneId):
		if zoneId == FunnyFarmGlobals.FunnyFarm:
			self.playGame.enterFFHood()
		elif zoneId == FunnyFarmGlobals.FunnyFarmCentral:
			self.playGame.enterFCHood()
		elif zoneId == FunnyFarmGlobals.SillySprings:
			self.playGame.enterSSHood()
		elif zoneId == FunnyFarmGlobals.SecretArea:
			self.playGame.enterSecretArea()
		else:
			self.playGame.notify.warning('zoneId ' + str(zoneId) + ' does not exist. Going to Funny Farm..')
			self.playGame.enterFFHood()

	def teleportTo(self, zoneId):
		base.localAvatar.enterTeleportOut(callback=self.__handleTeleport, extraArgs=[zoneId])
		Sequence(Wait(3.2), Func(base.localAvatar.hide)).start()

	def __handleTeleport(self, zoneId):
		base.localAvatar.exitTeleportOut()
		if self.playGame.hood:
			self.playGame.exitHood()
		elif self.playGame.street:
			self.playGame.exitStreet()
		elif self.playGame.place:
			self.playGame.exitPlace()
		self.enterHood(zoneId)

	def enterTheTooniverse(self, zoneId):
		self.exitPAT()
		self.enterHood(zoneId)
		base.localAvatar.reparentTo(render)
		base.localAvatar.setupControls()
		base.localAvatar.setupSmartCamera()
		base.localAvatar.initInterface()
		base.localAvatar.book.showButton()
		base.localAvatar.laffMeter.start()
		base.localAvatar.startChat()
		base.localAvatar.addActive()

	def exitTheTooniverse(self):
		base.localAvatar.enterTeleportOut(callback=self.__handleExit)
		Sequence(Wait(3.2), Func(base.localAvatar.hide)).start()

	def __handleExit(self):
		if self.playGame.hood:
			self.playGame.exitHood()
		elif self.playGame.street:
			self.playGame.exitStreet()
		elif self.playGame.place:
			self.playGame.exitPlace()
		base.localAvatar.destroy()
		base.localAvatar = None
		camera.reparentTo(render)
		soundMgr.startPAT()
		self.enterPAT()

	def isPaid(self):
		return True