from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.hood.ToonHood import ToonHood
from toontown.building.Building import Building
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
        self.setupLandmarkBuildings()
        self.startNametagTask()
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
        self.stopNametagTask()
        for doId in self.sp.activeSuits.keys():
            suit = self.sp.activeSuits[doId]
            suit.removeActive()

    def load(self):
        ToonHood.load(self)
        self.sp.setZoneId(self.zoneId)
        self.sp.loadSuits()
        self.battleMusic = base.loader.loadMusic('phase_3.5/audio/bgm/encntr_general_bg.ogg')
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

    def startActive(self):
        ToonHood.startActive(self)
        self.accept('sptRequestBattle-%d' % self.zoneId, self.enterBattle)

    def enterBattle(self, suitId, pos):
        base.localAvatar.disable()
        base.localAvatar.experienceBar.hide()
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
        base.localAvatar.experienceBar.show()
        self.battle.cleanupBattle()
        self.battle.delete()
        self.battle = None
        self.battleCell.removeNode()
        self.battleCell = None

    def setupLandmarkBuildings(self):
        self.buildings = []
        for building in self.geom.findAllMatches('**/tb*toon_landmark*'):
            zoneStr = building.getName().split(':')
            block = int(zoneStr[0][2:])
            zoneId = self.zoneId + 500 + block
            self.buildings.append(Building(zoneId))

    def startNametagTask(self):
        taskMgr.add(self.__nametagTask, '%d-nametagTask' % self.zoneId)

    def stopNametagTask(self):
        taskMgr.remove('%d-nametagTask' % self.zoneId)

    def __nametagTask(self, task):
        for bldg in self.buildings:
            origin = bldg.getBuildingNodePath().find('**/*door_origin*')
            dist = (base.localAvatar.getPos(self.geom) - origin.getPos(self.geom)).length()
            if dist <= 75:
                bldg.setupNametag()
            else:
                bldg.clearNametag()
        for doId in self.sp.activeSuits.keys():
            suit = self.sp.activeSuits[doId]
            dist = (base.localAvatar.getPos() - suit.getPos()).length()
            if dist <= 120:
                suit.addActive()
            else:
                suit.removeActive()
        return task.cont
