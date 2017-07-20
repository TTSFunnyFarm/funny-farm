from panda3d.core import *
from toontown.building import Door
from toontown.hood import SkyUtil, Hood
from toontown.hood.ToonHood import ToonHood
from toontown.toonbase import ToontownGlobals, FunnyFarmGlobals
import House

HOUSE_POSITIONS = [(-56.7788, -42.8756, 4.06471, -90, 0, 0),
 (83.3909, -77.5085, 0.0708361, 116.565, 0, 0),
 (-69.077, -119.496, 0.025, 77.1957, 0, 0),
 (63.4545, 11.0656, 8.05158, 356.6, 0, 0),
 (43.9315, 76.72, 0.0377455, 248.962, 0, 0),
 (-36.9122, 36.3429, 2.49382, 36.8699, 0, 0)]

class EstateHood(ToonHood):

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.Estate
        self.TTZoneId = ToontownGlobals.MyEstate
        self.hoodFile = 'phase_14/models/neighborhoods/estate_1'
        self.spookyHoodFile = self.hoodFile
        self.winterHoodFile = self.hoodFile
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.overwriteLastHood = False
        self.houses = []

    def enter(self, shop=None, tunnel=None, init=0):
        base.localAvatar.setZoneId(self.zoneId)
        musicMgr.playCurrentZoneMusic()
        self.setupLandmarkBuildings()
        if shop:
            house = self.houses[int(shop[2:]) - 1]
            door = Door.Door(house.door, 'estate')
            door.avatarExit(base.localAvatar)
            self.acceptOnce('avatarExitDone', self.startActive)
            return
        Hood.Hood.enter(self, shop=shop, tunnel=tunnel, init=init)

    def exit(self):
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)
        self.geom.setTransparency(TransparencyAttrib.MBinary, 1)
        self.geom.find('**/water').setColorScale(1, 1, 1, 0.75)
        for housePosIdx in xrange(len(HOUSE_POSITIONS)):
            zoneId = self.zoneId + 500 + housePosIdx + 1
            house = House.House(zoneId, housePosIdx + 1)
            house.load()
            house.model.reparentTo(self.geom)
            house.model.setPosHpr(*HOUSE_POSITIONS[housePosIdx])
            self.houses.append(house)

    def unload(self):
        ToonHood.unload(self)
        for house in self.houses:
            house.unload()
        self.houses = []

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)

    def handleDoorTrigger(self, collEntry):
        building = collEntry.getIntoNodePath().getParent().getParent().getParent().getParent().getParent() # ew
        zoneStr = building.getName().split(':')
        block = int(zoneStr[0][2:])
        doorNP = self.houses[block - 1].door
        door = Door.Door(doorNP, 'estate')
        door.avatarEnter(base.localAvatar)
        if 'door' in building.getName():
            building = self.geom.find('**/*toon_landmark_hq*')
        zoneId = self.zoneId + 500 + block
        self.acceptOnce('avatarEnterDone', self.enterPlace, ['estate', zoneId])
        return

    def setupLandmarkBuildings(self):
        return
