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
        suitDna.newSuit('ym')
        self.suit = BattleSuit.BattleSuit()
        self.suit.setDNA(suitDna)
        self.suit.reparentTo(render)
        self.suit.setPosHpr(0, 20, 0, 180, 0, 0)
        self.suit.initializeBodyCollisions('suit')
        self.suit.loop('neutral')

    def enter(self):
        base.playMusic(self.bgm, looping=1)
        base.localAvatar.enterTeleportIn(1, 0, callback=self.__handleTeleport)
        self.suit.beginSupaFlyMove(Point3(0, 20, 0), True, 'trackName', walkAfterLanding=False).start()
        self.suit.enableBattleDetect(self.__handleEnterBattle)

    def __handleEnterBattle(self, collEntry):
        self.bgm.stop()
        base.playMusic(self.battleBgm, looping=1)
        tb = TownBattle.TownBattle('townbattle-done')
        b = Battle.Battle(tb, toons=[base.localAvatar], suits=[self.suit])
        b.reparentTo(render)
        b.setPosHpr(0, 0, 0, 0, 0, 0) # battle cell goes here
        b.enter()

    def __handleTeleport(self):
        base.localAvatar.exitTeleportIn()
        base.localAvatar.book.showButton()
        base.localAvatar.beginAllowPies()
