from toontown.toonbase import FunnyFarmGlobals
from toontown.hood.HoodAI import HoodAI

class StreetAI(HoodAI):

    def __init__(self, air, zoneId):
        HoodAI.__init__(self, air, zoneId)

    def createZone(self):
        self.notify.info('Creating objects... %s, %s' % (FunnyFarmGlobals.getHoodNameFromId(self.zoneId)[0], FunnyFarmGlobals.getHoodNameFromId(self.zoneId)[1]))
        self.createObjects()

    def createJellybeanPlanner(self):
        pass

    def createSuitPlanner(self):
        pass

    def createBuildingPlanner(self):
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
        self.createJellybeanPlanner()
        self.createSuitPlanner()
        self.createBuildingPlanner()