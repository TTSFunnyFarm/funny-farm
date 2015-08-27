from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import FFTime

class HoodAI:
    notify = directNotify.newCategory('HoodAI')
    notify.setInfo(True)

    def __init__(self, air, zoneId):
        self.air = air
        self.zoneId = zoneId

    def createZone(self):
        self.notify.info('Creating objects... %s' % FunnyFarmGlobals.getHoodNameFromId(self.zoneId)[0])
        self.createObjects()

    def createTreasurePlanner(self):
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
        self.createTreasurePlanner()
