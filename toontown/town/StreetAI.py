from toontown.toonbase import FunnyFarmGlobals
from toontown.hood.HoodAI import HoodAI
from toontown.toonbase import FFTime

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
        if FFTime.isWinter():
            model = loader.loadModel(fileRoot + '_winter')
        elif FFTime.isHalloween():
            model = loader.loadModel(fileRoot + '_halloween')
        else:
            model = loader.loadModel(fileRoot)
        self.air.preloaded.append(model)
        self.createJellybeanPlanner()
        self.createSuitPlanner()
        self.createBuildingPlanner()