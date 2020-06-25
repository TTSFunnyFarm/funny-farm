from toontown.safezone import ButterflyGlobals
from toontown.suit.SuitPlannerAI import SuitPlannerAI
from toontown.safezone.ButterflyAI import ButterflyAI
from toontown.toonbase import FunnyFarmGlobals


class HoodAI:
    notify = directNotify.newCategory('HoodAI')
    notify.setInfo(True)

    def __init__(self, air, zoneId):
        self.air = air
        self.zoneId = zoneId
        self.butterflies = []

        for zoneId in self.getZoneTable():
            self.notify.info('Creating objects... %s' % self.getLocationName(zoneId))
            filename = FunnyFarmGlobals.phaseMap[zoneId]
            model = loader.loadModel(filename)
            self.air.modelMap[zoneId] = model

        self.createTreasurePlanner()
        self.createSuitPlanners()

    def getZoneTable(self):
        zoneTable = [self.zoneId]
        zoneTable.extend(FunnyFarmGlobals.HoodHierarchy.get(self.zoneId, []))
        return zoneTable

    def getLocationName(self, zoneId):
        lookupTable = FunnyFarmGlobals.hoodNameMap
        isStreet = (zoneId % 1000) != 0
        if isStreet:
            lookupTable = FunnyFarmGlobals.StreetNames
        name = lookupTable.get(zoneId, '')
        if isStreet:
            return '%s, %s' % (self.getLocationName(self.zoneId), name)
        return name

    def createTreasurePlanner(self):
        raise NotImplementedError('createTreasurePlanner')  # Must be overridden by subclass.

    def createSuitPlanners(self):
        for zoneId in FunnyFarmGlobals.HoodHierarchy.get(self.zoneId, []):
            sp = SuitPlannerAI(zoneId)
            # TEMPORARY pls undo after you do SuitPoints
            if zoneId != FunnyFarmGlobals.BarnyardBoulevard:
                sp.generate()
            self.air.suitPlanners[zoneId] = sp

    def createButterflies(self, playground):
        ButterflyGlobals.generateIndexes(self.zoneId, playground)
        for i in range(0, ButterflyGlobals.NUM_BUTTERFLY_AREAS[playground]):
            for j in range(0, ButterflyGlobals.NUM_BUTTERFLIES[playground]):
                bfly = ButterflyAI(self.air, playground, i, self.zoneId)
                bfly.generate()
                bfly.start()
                self.butterflies.append(bfly)
