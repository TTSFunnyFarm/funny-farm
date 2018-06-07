from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


class TreasurePlanner(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('TreasurePlanner')

    def __init__(self, treasureConstructor):
        DirectObject.__init__(self)
        self.treasureConstructor = treasureConstructor
        self.zoneId = 0
        self.treasures = []

    def generate(self):
        self.accept('generateTreasure', self.generateTreasure)
        self.accept('removeTreasure', self.removeTreasure)

    def delete(self):
        self.ignoreAll()
        del self.zoneId
        del self.treasures

    def setZoneId(self, zoneId):
        self.zoneId = zoneId

    def getZoneId(self):
        return self.zoneId

    def generateTreasure(self, requestStatus):
        pass  # TODO

    def removeTreasure(self, objId):
        pass  # TODO

    def loadTreasures(self):
        pass  # TODO

    def unloadTreasures(self):
        pass  # TODO
