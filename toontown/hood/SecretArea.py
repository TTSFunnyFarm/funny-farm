from pandac.PandaModules import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.suit import SuitDNA
from toontown.suit.BattleSuit import BattleSuit
from ToonHood import ToonHood
from toontown.town.TownBattle import TownBattle
from toontown.battle.Battle import Battle

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
        ToonHood.enter(self)
        base.avatarData.setLastHood = FunnyFarmGlobals.FunnyFarmCentral
        dataMgr.saveToonData(base.avatarData)
        self.suit.enableBattleDetect(self.enterBattle)

    def exit(self):
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('tbc')
        self.suit = BattleSuit()
        self.suit.setDNA(suitDNA)
        self.suit.reparentTo(render)
        self.suit.setPosHpr(0, 60, 0, 180, 0, 0)
        self.suit.setLevel(4)
        self.suit.setElite(1)
        self.suit.initializeBodyCollisions('suit')
        self.suit.loop('neutral')
        self.battleCell = NodePath('battle_cell_1')
        self.battleCell.reparentTo(self.geom)
        self.battleCell.setPosHpr(0, 40, 0, 0, 0, 0)

    def unload(self):
        ToonHood.unload(self)
        # Usually the battle doesn't end in time for us to unload (assuming the player dies)
        if self.townBattle:
            self.__battleDone()
        del self.suit
        del self.townBattle
        del self.battle

    def enterBattle(self, collEvent):
        base.localAvatar.disable()
        self.townBattle = TownBattle('townbattle-done')
        self.battle = Battle(self.townBattle, toons=[base.localAvatar], suits=[self.suit], secretArea=1)
        self.battle.reparentTo(self.battleCell)
        self.battle.enter()
        self.accept(self.townBattle.doneEvent, self.__battleDone)

    def __battleDone(self, *args):
        base.localAvatar.enable()
        self.ignore(self.townBattle.doneEvent)
        self.townBattle.unload()
        self.townBattle.cleanup()
        self.townBattle = None
        self.battle.cleanupBattle()
        self.battle.delete()
        self.battle = None
