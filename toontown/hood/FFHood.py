from pandac.PandaModules import *
from direct.actor.Actor import Actor
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from ToonHood import ToonHood
from toontown.toonbase import FFTime
from toontown.building import Door
from toontown.battle import BattleParticles
from toontown.toon import NPCToons
from otp.nametag.NametagConstants import *
from toontown.trolley import Trolley
from direct.interval.IntervalGlobal import *

class FFHood(ToonHood):

	def __init__(self):
		ToonHood.__init__(self)
		self.zoneId = FunnyFarmGlobals.FunnyFarm
		self.TTZoneId = ToontownGlobals.ToontownCentral
		self.hoodFile = 'phase_14/models/neighborhoods/funny_farm'
		self.spookyHoodFile = 'phase_14/models/neighborhoods/funny_farm_halloween'
		self.winterHoodFile = 'phase_14/models/neighborhoods/funny_farm_winter'
		self.skyFile = 'phase_3.5/models/props/TT_sky'
		self.titleText = FunnyFarmGlobals.FFHoodText
		self.titleColor = (1.0, 0.5, 0.4, 1.0)

	def enter(self, shop=None, tunnel=None):
		soundMgr.startFFNbrhood()
		ToonHood.enter(self, shop=shop, tunnel=tunnel)
		if shop:
			if shop == 'ps':
				doorNP = self.geom.find('**/PetShopDoor')
			elif shop == 'gs':
				doorNP = self.geom.find('**/GagShopDoor')
			elif shop == 'hq0':
				doorNP = self.geom.find('**/door_0')
			elif shop == 'th':
				doorNP = self.geom.find('**/ToonHallDoor')
			elif shop == 'mc':
				doorNP = self.geom.find('**/MickeyDoor')
			elif shop == 'mn':
				doorNP = self.geom.find('**/MinnieDoor')
			door = Door.Door(doorNP, shop, self.zoneId)
			door.avatarExit(base.localAvatar)
			self.acceptOnce('avatarExitDone', self.startActive)
			return
		if tunnel:
			tunnelOrigin = self.geom.find('**/outdoor_zone_entrance.egg').find('**/tunnel_origin')
			base.localAvatar.tunnelIn(tunnelOrigin)
		if FFTime.isWinter():
			self.snow.start(camera, self.snowRender)
		self.startActive()

	def exit(self):
		soundMgr.stopFFNbrhood()
		ToonHood.exit(self)
		if FFTime.isWinter():
			self.snow.cleanup()

	def load(self):
		ToonHood.load(self)
		self.sky.setScale(1.5)
		self.fish = Actor('phase_4/models/props/exteriorfish-zero', {'chan': 'phase_4/models/props/exteriorfish-swim'})
		self.fish.reparentTo(self.geom.find('**/PetShopExterior_TT.egg'))
		self.fish.loop('chan')
		self.trolley = Trolley.Trolley()
		self.trolley.setup()
		self.restockSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_pies_restock.ogg')
		self.leroy = NPCToons.createLocalNPC(91917)
		self.leroy.reparentTo(render)
		self.leroy.setPosHpr(45, 80, 0.025, 135, 0, 0)
		self.leroy.initializeBodyCollisions('toon')
		self.leroy.addActive()
		if not FFTime.isWinter() and not FFTime.isHalloween():
			self.startSkyTrack()
		if FFTime.isWinter():
			self.snow = BattleParticles.loadParticleFile('snowdisk.ptf')
			self.snow.setPos(0, 0, 5)
			self.snowRender = render.attachNewNode('snowRender')
			self.snowRender.setDepthWrite(0)
			self.snowRender.setBin('fixed', 1)

	def unload(self):
		if not FFTime.isWinter() and not FFTime.isHalloween():
			self.stopSkyTrack()
		ToonHood.unload(self)
		self.fish.stop()
		self.fish.cleanup()
		self.fish.removeNode()
		self.trolley.removeActive()
		self.trolley.delete()
		self.leroy.removeActive()
		self.leroy.delete()
		del self.fish
		del self.trolley
		del self.leroy

	def startActive(self):
		self.accept('enter' + self.leroy.collNodePath.node().getName(), self.__givePies)
		self.acceptOnce('enteroutdoor_zone_entrance_collision_floor', self.__handleFCTunnel)
		self.acceptOnce('enterPetShopDoorTrigger', self.__handlePetShop)
		self.acceptOnce('enterGagShopDoorTrigger', self.__handleGagShop)
		self.acceptOnce('enterdoor_trigger_0', self.__handleHQ)
		self.acceptOnce('enterToonHallDoorTrigger', self.__handleToonHall)
		self.acceptOnce('enterMickeyDoorTrigger', self.__handleMickeyHouse)
		self.acceptOnce('enterMinnieDoorTrigger', self.__handleMinnieHouse)
		self.trolley.addActive()

	def __givePies(self, entry):
		if base.localAvatar.numPies < 20:
			base.playSfx(self.restockSfx)
			base.localAvatar.givePies(4, 20)
			self.leroy.setChatAbsolute('Hey, %s! Have some pies!' % base.localAvatar.getName(), CFSpeech|CFTimeout)

	def __handlePetShop(self, entry):
		petDoor = self.geom.find('**/PetShopDoor')
		door = Door.Door(petDoor, 'ps', self.zoneId)
		door.avatarEnter(base.localAvatar)
		self.acceptOnce('avatarEnterDone', self.__handleEnterPetShop)

	def __handleEnterPetShop(self):
		base.cr.playGame.exitHood()
		base.cr.playGame.enterPetShop(self.zoneId)

	def __handleGagShop(self, entry):
		gagDoor = self.geom.find('**/GagShopDoor')
		door = Door.Door(gagDoor, 'gs', self.zoneId)
		door.avatarEnter(base.localAvatar)
		self.acceptOnce('avatarEnterDone', self.__handleEnterGagShop)

	def __handleEnterGagShop(self):
		base.cr.playGame.exitHood()
		base.cr.playGame.enterGagShop(self.zoneId)

	def __handleHQ(self, entry):
		hqDoor = self.geom.find('**/door_0')
		door = Door.Door(hqDoor, 'hq0', self.zoneId)
		door.avatarEnter(base.localAvatar)
		self.acceptOnce('avatarEnterDone', self.__handleEnterHQ)

	def __handleEnterHQ(self):
		base.cr.playGame.exitHood()
		base.cr.playGame.enterHQDoor0(self.zoneId)

	def __handleToonHall(self, entry):
		hallDoor = self.geom.find('**/ToonHallDoor')
		door = Door.Door(hallDoor, 'th', self.zoneId)
		door.avatarEnter(base.localAvatar)
		self.acceptOnce('avatarEnterDone', self.__handleEnterToonHall)

	def __handleEnterToonHall(self):
		base.cr.playGame.exitHood()
		base.cr.playGame.enterToonHall(self.zoneId)

	def __handleMickeyHouse(self, entry):
		mickeyDoor = self.geom.find('**/MickeyDoor')
		door = Door.Door(mickeyDoor, 'mc', self.zoneId)
		door.avatarEnter(base.localAvatar)
		self.acceptOnce('avatarEnterDone', self.__handleEnterMickeyHouse)

	def __handleEnterMickeyHouse(self):
		base.cr.playGame.exitHood()
		base.cr.playGame.enterMickeyHouse(self.zoneId)

	def __handleMinnieHouse(self, entry):
		minnieDoor = self.geom.find('**/MinnieDoor')
		door = Door.Door(minnieDoor, 'mn', self.zoneId)
		door.avatarEnter(base.localAvatar)
		self.acceptOnce('avatarEnterDone', self.__handleEnterMinnieHouse)

	def __handleEnterMinnieHouse(self):
		base.cr.playGame.exitHood()
		base.cr.playGame.enterMinnieHouse(self.zoneId)

	def __handleFCTunnel(self, entry):
		tunnelOrigin = self.geom.find('**/outdoor_zone_entrance.egg').find('**/tunnel_origin')
		base.localAvatar.tunnelOut(tunnelOrigin)
		self.acceptOnce('tunnelOutMovieDone', self.__handleEnterFC)

	def __handleEnterFC(self):
		base.cr.playGame.exitHood()
		base.cr.playGame.enterFCHood(tunnel='ff')