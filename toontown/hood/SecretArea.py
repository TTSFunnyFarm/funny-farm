from panda3d.core import *
from direct.interval.IntervalGlobal import *
from otp.nametag.NametagConstants import *
from toontown.toon import NPCToons
from toontown.toonbase import FunnyFarmGlobals, TTLocalizer
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
        self.titleColor = (0.5, 0.5, 0.5, 1.0)
        self.townBattle = None
        self.battle = None
        self.bear = None

    def enter(self):
        ToonHood.enter(self)
        base.avatarData.setLastHood = FunnyFarmGlobals.FunnyFarmCentral
        dataMgr.saveToonData(base.avatarData)
        self.suit.enableBattleDetect(self.enterBattle)

    def exit(self):
        ToonHood.exit(self)
        if self.suit:
            self.suit.disableBattleDetect()

    def load(self):
        ToonHood.load(self)
        self.townBattle = TownBattle('townbattle-done')
        self.townBattle.load()
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
        if self.suit:
            self.suit.delete()
        if self.bear:
            self.bear.removeActive()
            self.bear.delete()
        del self.suit
        del self.townBattle
        del self.battle

    def enterBattle(self, collEvent):
        base.localAvatar.disable()
        self.suit.disableBattleDetect()
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
        self.suit = None
        if base.localAvatar.hp > 0:
            # Uh ohhhh! Hax!!!!!
            musicMgr.stopMusic()
            self.bear = NPCToons.createLocalNPC(6001)
            self.bear.reparentTo(hidden)
            self.bear.setPosHpr(0, 60, 0, 180, 0, 0)
            self.bear.initializeBodyCollisions('toon')
            self.bear.useLOD(1000)
            self.bear.startBlink()
            self.teleportInSeq = Sequence(
                Wait(4),
                Func(self.bear.reparentTo, render),
                Func(self.bear.setAnimState, 'neutral'),
                Func(self.bear.addActive),
                Wait(0.01),
                Func(self.bear.setAnimState, 'TeleportIn', callback = self.bearGiveSpeech),
            )
            self.teleportInSeq.start()

    def bearChat(self, pageNumber):
        if pageNumber >= len(TTLocalizer.SecretAreaHacked) - 1:
            self.bear.setChatAbsolute(TTLocalizer.SecretAreaHacked[-1], CFSpeech | CFTimeout)
            base.localAvatar.stopUpdateSmartCamera()
            base.localAvatar.takeDamage(base.localAvatar.maxHp)
            base.localAvatar.disableAvatarControls()
        else:
            self.bear.setLocalPageChat(TTLocalizer.SecretAreaHacked[pageNumber], None)
            self.acceptOnce('Nametag-nextChat', self.bearChat, [pageNumber + 1])

    def bearGiveSpeech(self):
            self.startSpeech = Sequence(
                Func(musicMgr.playMusic, base.loadMusic('phase_14/audio/bgm/SKP_enctr_bg.ogg'), True),
                Func(self.bear.setAnimState, 'neutral'),
                Wait(1),
                Func(self.bearChat, 0),
            )
            self.startSpeech.start()
