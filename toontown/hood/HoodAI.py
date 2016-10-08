from toontown.toonbase import FunnyFarmGlobals

class HoodAI:
    notify = directNotify.newCategory('HoodAI')
    notify.setInfo(True)

    def __init__(self, air, zoneId):
        self.air = air
        self.zoneId = zoneId

        for zoneId in self.getZoneTable():
            self.notify.info('Creating objects... %s' % self.getLocationName(zoneId))
            filename = FunnyFarmGlobals.phaseMap[zoneId]
            model = loader.loadModel(filename)
            self.air.modelMap[zoneId] = model

        self.createTreasurePlanner()
        self.createSuitPlanners()
        self.createBuildingManagers()

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
        pass

    def createSuitPlanners(self):
        pass

    def createBuildingManagers(self):
        pass
