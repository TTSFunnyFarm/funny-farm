from pandac.PandaModules import *
from direct.actor import Actor
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from Interior import Interior
import ToonInteriorColors
import random
import Door

class MickeyInterior(Interior):

	def __init__(self, zoneId):
		Interior.__init__(self)
		self.zoneId = zoneId
		self.interiorFile = 'phase_14/models/modules/mickey_interior'

	def load(self):
		Interior.load(self)
		self.randomGenerator = random.Random()
		self.randomGenerator.seed(self.zoneId)
		self.colors = ToonInteriorColors.colors[self.zoneId]
		self.interior.find('**/door_origin').setScale(0.8, 0.8, 0.8)
		self.interior.find('**/door_origin').setH(180)
		self.door = self.setupDoor('door_double_round_ur', 'door_origin')
		doorColor = self.colors['TI_door'][1]
		self.door.setColor(doorColor)
		self.fixDoor(self.door)
		self.acceptOnce('avatarExitDone', self.startActive)
		del self.colors
		del self.randomGenerator
		self.interior.flattenMedium()

	def unload(self):
		Interior.unload(self)

	def startActive(self):
		self.acceptOnce('enterdoor_double_round_ur_trigger', self.__handleDoor)

	def __handleDoor(self, entry):
		door = Door.Door(self.door, 'mc_int', self.zoneId)
		door.avatarEnter(base.localAvatar)
		self.acceptOnce('avatarEnterDone', self.__handleEnterFF)

	def __handleEnterFF(self):
		base.cr.playGame.exitPlace()
		base.cr.playGame.enterFFHood(shop='mc')