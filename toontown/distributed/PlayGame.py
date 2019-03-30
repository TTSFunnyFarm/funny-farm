from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from toontown.estate import EstateHood
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.hood import ZoneUtil
from toontown.hood import FFHood
from toontown.hood import SSHood
from toontown.town import FFStreet
from toontown.tutorial import Tutorial
from toontown.minigame import Purchase
from toontown.minigame import RingGame
from toontown.minigame import CannonGame
from toontown.minigame import CatchGame
from toontown.minigame import TugOfWarGame
from toontown.minigame import MazeGame
from toontown.minigame import DivingGame
from toontown.minigame import CogThiefGame
import random

class PlayGame(DirectObject):
    notify = directNotify.newCategory('PlayGame')
    Hood2ClassDict = {
        FunnyFarmGlobals.FunnyFarm: FFHood.FFHood,
        FunnyFarmGlobals.SillySprings: SSHood.SSHood,
        FunnyFarmGlobals.Estate: EstateHood.EstateHood
    }
    Street2ClassDict = {
        FunnyFarmGlobals.FunnyFarm: FFStreet.FFStreet
    }
    MINIGAMES = [
        RingGame.RingGame,
        CannonGame.CannonGame,
        CatchGame.CatchGame,
        TugOfWarGame.TugOfWarGame,
        MazeGame.MazeGame,
        DivingGame.DivingGame,
        CogThiefGame.CogThiefGame
    ]

    def __init__(self):
        self.hood = None
        self.street = None
        self.minigame = None
        self.purchase = None
        self.lastGame = None

    def enterHood(self, zoneId, tunnel=None, init=0):
        if zoneId not in self.Hood2ClassDict.keys():
            return
        name = FunnyFarmGlobals.hoodNameMap[zoneId]
        count = FunnyFarmGlobals.safeZoneCountMap[zoneId]
        loader.beginBulkLoad('hood', TTLocalizer.HeadingToHood % name, count, TTLocalizer.TIP_GENERAL)
        self.hood = self.Hood2ClassDict[zoneId]()
        self.hood.load()
        loader.endBulkLoad('hood')
        self.hood.enter(tunnel=tunnel, init=init)

    def exitHood(self):
        if self.hood.place:
            self.hood.exitPlace()
        self.hood.exit()
        self.hood.unload()
        self.hood = None
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()

    def enterStreet(self, zoneId, tunnel=None):
        hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
        if hoodId not in self.Street2ClassDict.keys():
            self.notify.warning('No streets available in zone %d.' % hoodId)
            return
        if zoneId not in FunnyFarmGlobals.HoodHierarchy[hoodId]:
            self.notify.warning('Street %d is currently unavailable.' % zoneId)
            self.enterHood(hoodId, tunnel=str(zoneId))
            return
        name = FunnyFarmGlobals.StreetNames[zoneId]
        count = FunnyFarmGlobals.townCountMap[hoodId]
        loader.beginBulkLoad('street', TTLocalizer.HeadingToHood % name, count, TTLocalizer.TIP_STREET)
        self.street = self.Street2ClassDict[hoodId](zoneId)
        self.street.load()
        loader.endBulkLoad('street')
        self.street.enter(tunnel=tunnel)

    def exitStreet(self):
        if self.street.place:
            self.street.exitPlace()
        self.street.exit()
        self.street.unload()
        self.street = None
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()

    def exitActiveZone(self):
        if self.hood:
            self.exitHood()
        elif self.street:
            self.exitStreet()

    def getActiveZone(self):
        if self.hood:
            return self.hood
        elif self.street:
            return self.street

    def enterTutorial(self):
        name = TTLocalizer.Tutorial
        count = FunnyFarmGlobals.townCountMap[FunnyFarmGlobals.Tutorial]
        loader.beginBulkLoad('hood', TTLocalizer.HeadingToHood % name, count, TTLocalizer.TIP_GENERAL)
        self.hood = Tutorial.Tutorial()
        self.hood.load()
        loader.endBulkLoad('hood')
        self.hood.enter()

    def enterRandomMinigame(self):
        if hasattr(self.hood, 'geom'):
            self.hood.exit()
            self.hood.unload()
            ModelPool.garbageCollect()
            TexturePool.garbageCollect()
        game = random.choice(self.MINIGAMES)()
        if self.lastGame:
            if game.getTitle() == self.lastGame:
                del game
                self.enterRandomMinigame()
            else:
                self.enterMinigame(game)
        else:
            self.enterMinigame(game)

    def enterMinigame(self, minigame):
        self.minigame = minigame
        self.minigame.generate()
        self.minigame.announceGenerate()
        self.lastGame = self.minigame.getTitle()

    def exitMinigame(self):
        self.minigame.delete()
        self.minigame = None
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()

    def enterMinigamePurchase(self, toon, pointsArray, playerMoney, ids, states, remain, doneEvent):
        self.purchase = Purchase.Purchase(toon, pointsArray, playerMoney, ids, states, remain, doneEvent)
        self.purchase.load()
        self.purchase.enter()

    def exitMinigamePurchase(self):
        self.purchase.exitPurchase()
        self.purchase.exit()
        self.purchase.unload()
        self.purchase = None
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
