from pandac.PandaModules import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.suit import SuitDNA
from toontown.suit import Suit
from ToonHood import ToonHood

class SecretArea(ToonHood):

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.SecretArea
        self.hoodFile = 'phase_14/models/modules/secret_area'
        self.spookyHoodFile = 'phase_14/models/modules/secret_area'
        self.winterHoodFile = 'phase_14/models/modules/secret_area'
        self.skyFile = 'phase_9/models/cogHQ/cog_sky'
        self.titleText = FunnyFarmGlobals.SecretAreaText
        self.titleColor = (0.5, 0.5, 0.5, 1.0)

    def enter(self):
        musicMgr.startSecretArea()
        ToonHood.enter(self)
        base.avatarData.setLastHood = FunnyFarmGlobals.FunnyFarmCentral
        dataMgr.saveToonData(base.avatarData)

    def exit(self):
        musicMgr.stopSecretArea()
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)
        self.suit = Suit.Suit()
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('tbc')
        self.suit.setDNA(suitDNA)
        self.suit.makeElite()
        self.suit.initializeBodyCollisions('cog')
        self.suit.setDisplayName('The Big Cheese\nBossbot\nLevel 12 Elite')
        self.suit.setPickable(0)
        self.suit.reparentTo(render)
        self.suit.setPosHpr(0, 60, 0, 180, 0, 0)
        self.suit.loop('neutral')

    def unload(self):
        ToonHood.unload(self)
        self.suit.stop()
        self.suit.delete()
        del self.suit
