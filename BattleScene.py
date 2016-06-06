# this scene is for testing purposes

from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.suit import BattleSuit
from toontown.suit import SuitDNA
from toontown.battle import Battle
from toontown.town import TownBattle

class BattleScene(DirectObject):

    def load(self):
        self.environ = loader.loadModel('phase_4/models/minigames/tag_arena')
        self.environ.reparentTo(render)
        self.environ.flattenMedium()
        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')
        self.sky.reparentTo(render)
        self.sky.flattenMedium()
        self.bgm = base.loadMusic('phase_3.5/audio/bgm/TC_SZ.ogg')
        self.battleBgm = base.loadMusic('phase_3.5/audio/bgm/encntr_general_bg.ogg')
        suitDna = SuitDNA.SuitDNA()
        suitDna.newSuit('cc')
        self.suit = BattleSuit.BattleSuit()
        self.suit.setDNA(suitDna)
        self.suit.setLevel(0)
        self.suit.setElite(1)
        self.suit.reparentTo(render)
        self.suit.setPosHpr(0, 20, 0, 180, 0, 0)
        self.suit.initializeBodyCollisions('suit')
        self.suit.loop('neutral')
        self.battle = None
        self.townBattle = None

    def unload(self):
        self.environ.removeNode()
        self.sky.removeNode()
        del self.environ
        del self.sky
        del self.bgm
        del self.battleBgm
        del self.suit

    def enter(self):
        base.playMusic(self.bgm, looping=1)
        base.localAvatar.enterTeleportIn(1, 0, callback=self.__handleTeleport)
        Sequence(
            self.suit.beginSupaFlyMove(Point3(0, 20, 0), True, 'trackName', walkAfterLanding=False),
            Func(self.suit.enableBattleDetect, self.__handleEnterBattle)
        ).start()

    def exit(self):
        self.ignoreAll()
        self.bgm.stop()
        self.battleBgm.stop()

    def __handleEnterBattle(self, collEntry):
        self.townBattle = TownBattle.TownBattle('townbattle-done')
        self.battle = Battle.Battle(self.townBattle, toons=[base.localAvatar], suits=[self.suit])
        self.battle.reparentTo(render)
        self.battle.setPosHpr(0, 0, 0, 0, 0, 0) # battle cell goes here
        self.battle.enter()
        self.bgm.stop()
        base.playMusic(self.battleBgm, looping=1)
        self.accept(self.townBattle.doneEvent, self.__battleDone)

    def __battleDone(self, doneStatus):
        self.ignore(self.townBattle.doneEvent)
        self.battleBgm.stop()
        if doneStatus == 'victory':
            self.bgm.play()
        self.townBattle.unload()
        self.townBattle.cleanup()
        self.townBattle = None
        self.battle.cleanupBattle()
        self.battle.delete()
        self.battle = None

    def __handleTeleport(self):
        base.localAvatar.exitTeleportIn()
        base.localAvatar.book.showButton()
        base.localAvatar.beginAllowPies()
