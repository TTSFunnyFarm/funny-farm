from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.hood.ToonHood import ToonHood
from toontown.building import Door
from toontown.suit.SuitPlanner import SuitPlanner
from toontown.town.TownBattle import TownBattle
from toontown.battle.Battle import Battle

class Street(ToonHood):
    notify = directNotify.newCategory('Street')

    def __init__(self):
        ToonHood.__init__(self)
        self.sp = SuitPlanner()
        self.battle = None
        self.battleCell = None
        self.townBattleDoneEvent = 'town-battle-done'

    def enter(self, shop=None, tunnel=None):
        base.localAvatar.setZoneId(self.zoneId)
        musicMgr.playCurrentZoneMusic()
        if shop:
            building = self.geom.find('**/tb%s:toon_landmark*' % shop[2:])
            if building.isEmpty():
                building = self.geom.find('**/%s' % shop)
            door = Door.Door(building, shop)
            door.avatarExit(base.localAvatar)
            self.acceptOnce('avatarExitDone', self.startActive)
            return
        if tunnel:
            for linkTunnel in self.geom.findAllMatches('**/linktunnel*'):
                name = linkTunnel.getName().split('_')
                hoodStr = name[1]
                if tunnel == hoodStr:
                    tunnelOrigin = linkTunnel.find('**/tunnel_origin')
                    base.localAvatar.tunnelIn(tunnelOrigin)
        base.avatarData.setLastHood = FunnyFarmGlobals.getHoodId(self.zoneId)
        dataMgr.saveToonData(base.avatarData)
        self.spawnTitleText()
        self.startActive()
        self.sp.generate()

    def exit(self):
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)
        self.sp.setZoneId(self.zoneId)
        self.sp.loadSuits()
        self.battleMusic = base.loadMusic('phase_3.5/audio/bgm/encntr_general_bg.ogg')
        self.townBattle = TownBattle(self.townBattleDoneEvent)
        self.townBattle.load()

    def unload(self):
        ToonHood.unload(self)
        self.sp.unloadSuits()
        self.sp.delete()
        self.townBattle.unload()
        self.townBattle.cleanup()
        del self.townBattle
        del self.battleMusic

    def enterHood(self, zoneId):
        tunnel = str(self.zoneId)
        base.cr.playGame.enterHood(zoneId, tunnel=tunnel)

    def enterPlace(self, shopId, zoneId):
        ToonHood.enterPlace(self, shopId, zoneId)
        for doId in self.sp.activeSuits.keys():
            suit = self.sp.activeSuits[doId]
            suit.removeActive()

    def exitPlace(self):
        ToonHood.exitPlace(self)
        for doId in self.sp.activeSuits.keys():
            suit = self.sp.activeSuits[doId]
            suit.addActive()

    def startActive(self):
        ToonHood.startActive(self)
        self.accept('sptRequestBattle-%d' % self.zoneId, self.enterBattle)

    def enterBattle(self, suitId, pos):
        base.localAvatar.disable()
        suit = self.sp.activeSuits[suitId]
        self.sp.removeActiveSuit(suitId)
        self.battleCell = NodePath('battleCell')
        self.battleCell.reparentTo(render)
        self.battleCell.setPos(pos[0])
        self.battleCell.setH(pos[1])
        self.battle = Battle(self.townBattle, toons=[base.localAvatar], suits=[suit])
        self.battle.reparentTo(self.battleCell)
        self.battle.enter()
        musicMgr.stopMusic()
        base.playMusic(self.battleMusic, looping=1)
        self.accept(self.townBattle.doneEvent, self.exitBattle)

    def exitBattle(self, *args):
        self.ignore(self.townBattle.doneEvent)
        self.battleMusic.stop()
        musicMgr.playCurrentZoneMusic()
        base.localAvatar.enable()
        self.battle.cleanupBattle()
        self.battle.delete()
        self.battle = None
        self.battleCell.removeNode()
        self.battleCell = None
