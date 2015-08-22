from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
import random
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.tutorial import Tutorial
from toontown.hood import FFHood
from toontown.hood import FCHood
from toontown.hood import SSHood
from toontown.hood import SecretArea
from toontown.town import SSStreet
from toontown.building import Door
from toontown.building import PetShopInterior
from toontown.building import GagShopInterior
from toontown.building import HQInterior
from toontown.building import ToonHallInterior
from toontown.building import MickeyInterior, MinnieInterior
from toontown.building import EliteInterior
from toontown.minigame import Purchase
from toontown.minigame import RingGame
from toontown.minigame import CannonGame
from toontown.minigame import CatchGame
from toontown.minigame import TugOfWarGame

class PlayGame(DirectObject):
	notify = directNotify.newCategory('PlayGame')
	MINIGAMES = [CatchGame.CatchGame]

	def __init__(self):
		self.hood = None
		self.street = None
		self.place = None
		self.minigame = None
		self.purchase = None

	def enterHood(self, hood, name, loadCount, tunnel=None):
		self.hood = hood
		loader.beginBulkLoad(name, 'Heading to ' + name + '. . .', loadCount, TTLocalizer.TIP_GENERAL)
		self.hood.load()
		loader.endBulkLoad(name)
		self.hood.enter(tunnel=tunnel)

	def enterHoodFromShop(self, hood, shop=None):
		self.hood = hood
		self.hood.load()
		self.hood.enter(shop=shop)

	def exitHood(self):
		ModelPool.garbageCollect()
		TexturePool.garbageCollect()
		self.hood.exit()
		self.hood.unload()
		self.hood = None

	def enterStreet(self, street, name, loadCount, tunnel=None):
		self.street = street
		loader.beginBulkLoad(name, 'Heading to ' + name + '. . .', loadCount, TTLocalizer.TIP_GENERAL)
		self.street.load()
		loader.endBulkLoad(name)
		self.street.enter(tunnel=tunnel)

	def exitStreet(self):
		ModelPool.garbageCollect()
		TexturePool.garbageCollect()
		self.street.exit()
		self.street.unload()
		self.street = None

	def enterPlace(self, place, code, zoneId):
		self.place = place
		self.place.load()
		door = Door.Door(self.place.door, code, zoneId)
		door.avatarExit(base.localAvatar)

	def exitPlace(self):
		ModelPool.garbageCollect()
		TexturePool.garbageCollect()
		self.place.unload()
		self.place = None

	def enterSuitPlace(self, place):
		self.place = place
		self.place.loadNextFloor()

	def enterSecretArea(self):
		self.hood = SecretArea.SecretArea()
		loader.beginBulkLoad('???', '???', 400, TTLocalizer.TIP_GENERAL)
		self.hood.load()
		loader.endBulkLoad('???')
		self.hood.enter()

	def enterRandomMinigame(self):
		if hasattr(self.hood, 'geom'):
			ModelPool.garbageCollect()
			TexturePool.garbageCollect()
			self.hood.exit()
			self.hood.unload()
		game = random.choice(self.MINIGAMES)
		self.minigame = game()
		self.minigame.load()
		self.minigame.generate()
		self.minigame.announceGenerate()

	def exitMinigame(self):
		ModelPool.garbageCollect()
		TexturePool.garbageCollect()
		self.minigame.delete()
		self.minigame = None

	def enterMinigamePurchase(self, toon, pointsArray, playerMoney, ids, states, remain, doneEvent):
		self.purchase = Purchase.Purchase(toon, pointsArray, playerMoney, ids, states, remain, doneEvent)
		self.purchase.load()
		self.purchase.enter()

	def exitMinigamePurchase(self):
		ModelPool.garbageCollect()
		TexturePool.garbageCollect()
		self.purchase.exitPurchase()
		self.purchase.exit()
		self.purchase.unload()
		self.purchase = None

	def enterTutorial(self):
		hood = Tutorial.Tutorial()
		self.enterHood(hood, 'The Toontorial', 300)

	def enterFFHood(self, shop=None, tunnel=None):
		hood = FFHood.FFHood()
		if shop:
			self.enterHoodFromShop(hood, shop=shop)
		else:
			self.enterHood(hood, 'Funny Farm', 200, tunnel=tunnel)

	def enterFCHood(self, shop=None, tunnel=None):
		hood = FCHood.FCHood()
		self.enterHood(hood, 'Funny Farm Central', 100, tunnel=tunnel)

	def enterSSHood(self, shop=None, tunnel=None):
		hood = SSHood.SSHood()
		if shop:
			self.enterHoodFromShop(hood, shop=shop)
		else:
			self.enterHood(hood, 'Silly Springs', 100, tunnel=tunnel)

	def enterSSStreet(self, tunnel=None):
		street = SSStreet.SSStreet()
		self.enterStreet(street, 'Rickety Road', 100, tunnel=tunnel)

	def enterPetShop(self, zoneId):
		place = PetShopInterior.PetShopInterior(zoneId)
		self.enterPlace(place, 'ps_int', zoneId)

	def enterGagShop(self, zoneId):
		place = GagShopInterior.GagShopInterior(zoneId)
		self.enterPlace(place, 'gs_int', zoneId)

	def enterHQDoor0(self, zoneId):
		place = HQInterior.HQInterior(zoneId)
		self.place = place
		self.place.load()
		door = Door.Door(self.place.door, 'hq_int0', zoneId)
		door.avatarExit(base.localAvatar)

	def enterHQDoor1(self, zoneId):
		place = HQInterior.HQInterior(zoneId)
		self.place = place
		self.place.load()
		door = Door.Door(self.place.door2, 'hq_int1', zoneId)
		door.avatarExit(base.localAvatar)

	def enterToonHall(self, zoneId):
		place = ToonHallInterior.ToonHallInterior(zoneId)
		self.enterPlace(place, 'th_int', zoneId)

	def enterMickeyHouse(self, zoneId):
		place = MickeyInterior.MickeyInterior(zoneId)
		self.enterPlace(place, 'mc_int', zoneId)

	def enterMinnieHouse(self, zoneId):
		place = MinnieInterior.MinnieInterior(zoneId)
		self.enterPlace(place, 'mn_int', zoneId)

	def enterEliteInterior(self, zoneId):
		place = EliteInterior.EliteInterior(zoneId)
		self.enterSuitPlace(place)
