from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.hood.ToonHood import ToonHood
from toontown.building import Door

class Street(ToonHood):
    notify = directNotify.newCategory('Street')

    def __init__(self):
        ToonHood.__init__(self)

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

    def exit(self):
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)

    def unload(self):
        ToonHood.unload(self)

    def enterHood(self, zoneId):
        tunnel = str(self.zoneId)
        base.cr.playGame.enterHood(zoneId, tunnel=tunnel)
