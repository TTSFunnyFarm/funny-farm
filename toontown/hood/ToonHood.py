from panda3d.core import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.building.Building import Building
from toontown.building import GagShopInterior
from toontown.building import PetShopInterior
from toontown.building import HQInterior
from toontown.building import ToonHallInterior
from toontown.building import LoonyLabsInterior
from toontown.building import ToonInterior
from toontown.building import Door
from toontown.estate import EstateInterior
from toontown.trolley.Trolley import Trolley
from Hood import Hood

class ToonHood(Hood):
    Shop2ClassDict = {
        'gag_shop': GagShopInterior.GagShopInterior,
        'pet_shop': PetShopInterior.PetShopInterior,
        'door_0': HQInterior.HQInterior,
        'door_1': HQInterior.HQInterior,
        'toonhall': ToonHallInterior.ToonHallInterior,
        'estate': EstateInterior.EstateInterior,
        'loonylabs': LoonyLabsInterior.LoonyLabsInterior,
        'default': ToonInterior.ToonInterior
    }

    def __init__(self):
        Hood.__init__(self)
        self.fish = None
        self.trolley = None
        self.telescope = None
        self.animSeq = None
        self.buildings = None

    def enter(self, shop=None, tunnel=None, init=0):
        base.localAvatar.setZoneId(self.zoneId)
        musicMgr.playCurrentZoneMusic()
        self.setupLandmarkBuildings()
        if shop:
            building = self.geom.find('**/tb%s:toon_landmark*' % shop[2:])
            if building.isEmpty():
                building = self.geom.find('**/%s' % shop)
            door = Door.Door(building, shop)
            door.avatarExit(base.localAvatar)
            self.acceptOnce('avatarExitDone', self.startActive)
            return
        Hood.enter(self, shop=shop, tunnel=tunnel, init=init)

    def exit(self):
        Hood.exit(self)
        if self.buildings:
            self.destroyLandmarkBuildings()

    def load(self):
        Hood.load(self)
        if not self.geom.find('**/fish_origin').isEmpty():
            self.fish = Actor('phase_4/models/props/exteriorfish-zero', {'chan': 'phase_4/models/props/exteriorfish-swim'})
            self.fish.reparentTo(self.geom.find('**/fish_origin'))
            self.fish.setBlend(frameBlend=True)
            self.fish.loop('chan')
        if not self.geom.find('**/*trolley_station*').isEmpty():
            self.trolley = Trolley()
            self.trolley.setup()

    def unload(self):
        Hood.unload(self)
        if self.fish:
            self.fish.stop()
            self.fish.cleanup()
            self.fish.removeNode()
            del self.fish
        if self.trolley:
            self.trolley.removeActive()
            self.trolley.delete()
            del self.trolley

    def startActive(self):
        Hood.startActive(self)
        if self.trolley:
            self.trolley.addActive()

    def setupLandmarkBuildings(self):
        self.buildings = []
        for building in self.geom.findAllMatches('**/tb*toon_landmark*'):
            zoneStr = building.getName().split(':')
            block = int(zoneStr[0][2:])
            zoneId = self.zoneId + 500 + block
            self.buildings.append(Building(zoneId))
        for building in self.buildings:
            building.load()

    def destroyLandmarkBuildings(self):
        for building in self.buildings:
            building.unload()
            del building
        self.buildings = None

    def handleDoorTrigger(self, collEntry):
        building = collEntry.getIntoNodePath().getParent()
        for shopId in self.Shop2ClassDict.keys():
            if shopId in building.getName():
                door = Door.Door(building, shopId)
                door.avatarEnter(base.localAvatar)
                if 'door' in building.getName():
                    building = self.geom.find('**/*toon_landmark_hq*')
                zoneStr = building.getName().split(':')
                block = int(zoneStr[0][2:])
                zoneId = self.zoneId + 500 + block
                self.acceptOnce('avatarEnterDone', self.enterPlace, [shopId, zoneId])
                return
        door = Door.Door(building, 'default')
        door.avatarEnter(base.localAvatar)
        try:
            zoneStr = building.getName()[2:4]
            zoneId = self.zoneId + 500 + int(zoneStr)
        except:
            zoneStr = building.getName()[2]
            zoneId = self.zoneId + 500 + int(zoneStr)
        self.acceptOnce('avatarEnterDone', self.enterPlace, ['default', zoneId])

    def enterPlace(self, shopId, zoneId):
        self.exit()
        self.geom.reparentTo(hidden)
        self.geom.stash()
        if shopId not in self.Shop2ClassDict.keys():
            self.notify.warning('Could not find shopId: %s' % shopId)
            return
        self.place = self.Shop2ClassDict[shopId](shopId, zoneId)
        self.place.load()
        if shopId == 'door_1':
            door = Door.Door(self.place.door2, shopId + '_int')
        else:
            door = Door.Door(self.place.door, shopId + '_int')
        door.avatarExit(base.localAvatar)

    def exitPlace(self):
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
        self.place.unload()
        self.place = None
        self.geom.unstash()
        self.geom.reparentTo(render)
