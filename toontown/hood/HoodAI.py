from toontown.toonbase import FunnyFarmGlobals

class HoodAI:
    notify = directNotify.newCategory('HoodAI')
    notify.setInfo(True)

    def __init__(self, air, zoneId):
        self.air = air
        self.zoneId = zoneId

    def getLocationName(self, zoneId):
        lookupTable = FunnyFarmGlobals.HoodNameDict
        isStreet = (self.zoneId % 1000) != 0
        name = lookupTable.get(self.zoneId, '')
        if isStreet:
            hoodId = FunnyFarmGlobals.getHoodId(self.zoneId)
            hoodName = lookupTable.get(hoodId, '')
            return '%s, %s' % (hoodName, name)
        return name

    def createZone(self):
        self.notify.info('Creating objects... %s' % self.getLocationName(self.zoneId))
        self.createObjects()

    def createTreasurePlanner(self):
        pass

    def createObjects(self):
        fileRoot = FunnyFarmGlobals.phaseMap[self.zoneId]
        if self.air.holidayMgr.isWinter():
            model = loader.loadModel(fileRoot + '_winter')
        elif self.air.holidayMgr.isHalloween():
            model = loader.loadModel(fileRoot + '_halloween')
        else:
            model = loader.loadModel(fileRoot)
        self.air.preloaded.append(model)
        self.createTreasurePlanner()
