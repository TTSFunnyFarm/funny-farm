from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.hood.ToonHood import ToonHood
from toontown.building.Building import Building
from toontown.building import Door
from toontown.suit.SuitPlanner import SuitPlanner
from toontown.town.TownBattle import TownBattle
from toontown.battle.Battle import Battle
from toontown.town.TownLoader import TownLoader

class Street(ToonHood):
    notify = directNotify.newCategory('Street')

    def __init__(self):
        ToonHood.__init__(self)
        self.townLoader = TownLoader(self)
        self.sp = SuitPlanner()
        self.battle = None
        self.battleCell = None
        self.townBattleDoneEvent = 'town-battle-done'

    def enter(self, shop=None, tunnel=None):
        base.localAvatar.setZoneId(self.zoneId)
        musicMgr.playCurrentZoneMusic()
        self.townLoader.enter()
        self.setupLandmarkBuildings()
        self.sp.loadBuildings()
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
                    self.townLoader.setCurrentGroup(int(linkTunnel.getAncestor(2).getName()))
                    tunnelOrigin = linkTunnel.find('**/tunnel_origin')
                    base.localAvatar.tunnelIn(tunnelOrigin)
            self.startActive()

        hoodId = FunnyFarmGlobals.getHoodId(self.zoneId)
        if base.avatarData.setLastHood != hoodId:
            base.avatarData.setLastHood = hoodId
            dataMgr.saveToonData(base.avatarData)

        self.spawnTitleText()
        self.sp.generate()

    def exit(self):
        ToonHood.exit(self)
        self.townLoader.exit()
        for doId in self.sp.activeSuits.keys():
            suit = self.sp.activeSuits[doId]
            suit.removeActive()

    def load(self):
        ToonHood.load(self)
        self.townLoader.setZoneId(self.zoneId)
        self.townLoader.load()
        self.sp.setZoneId(self.zoneId)
        self.sp.loadSuits()
        self.battleMusic = base.loader.loadMusic('phase_3.5/audio/bgm/encntr_general_bg.ogg')
        self.townBattle = TownBattle(self.townBattleDoneEvent)
        self.townBattle.load()

    def unload(self):
        ToonHood.unload(self)
        self.townLoader.unload()
        self.sp.unloadSuits()
        self.sp.delete()
        self.townBattle.unload()
        self.townBattle.cleanup()
        del self.townLoader
        del self.sp
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
        self.battleCell.reparentTo(self.geom)
        self.battleCell.setPos(pos[0])
        self.battleCell.setH(pos[1])
        self.battle = Battle(self.townBattle, toons=[base.localAvatar], suits=[suit])
        self.battle.reparentTo(self.battleCell)
        self.battle.enter()
        musicMgr.stopMusic()
        musicMgr.playMusic(self.battleMusic, looping=1, volume=0.75)
        self.sp.startCheckBattleRange()
        self.accept(self.townBattle.doneEvent, self.exitBattle)

    def exitBattle(self, doneStatus):
        self.ignore(self.townBattle.doneEvent)
        self.sp.stopCheckBattleRange()
        self.battleMusic.stop()
        musicMgr.playCurrentZoneMusic()
        self.battle.cleanupBattle()
        self.battle.delete()
        self.battle = None
        self.battleCell.removeNode()
        self.battleCell = None
        base.localAvatar.experienceBar.show()
        if doneStatus == 'victory':
            base.localAvatar.enable()
        elif doneStatus == 'defeat':
            base.localAvatar.reparentTo(render)
            base.localAvatar.died()

    def setupLandmarkBuildings(self):
        # Overrides ToonHood because we don't want to load the nametags right away
        for block in FunnyFarmGlobals.BuildingIds[self.zoneId]:
            zoneId = self.zoneId + 500 + block
            self.buildings.append(Building(zoneId))
        for building in self.buildings:
            building.setToToon()
        self.refreshQuestIcons()
