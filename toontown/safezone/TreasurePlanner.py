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

    def delete(self):
        self.ignoreAll()
        del self.zoneId
        del self.treasures

    def setZoneId(self, zoneId):
        self.zoneId = zoneId

    def getZoneId(self):
        return self.zoneId

    def generateTreasure(self, requestStatus):
        treasure = self.treasureConstructor()
        treasure.announceGenerate()
        treasure.setPosition(*requestStatus['pos'])
        treasure.setDoId(requestStatus['doId'])
        self.treasures.append(treasure)

    def loadTreasures(self):
        ai = base.air.treasurePlanners.get(self.zoneId)
        if not ai:
            return

        currentTreasures = ai.treasures[:]
        for currentTreasure in currentTreasures:
            if currentTreasure:
                self.generateTreasure({'pos': currentTreasure.getPosition(),
                                       'doId': currentTreasure.getDoId()})

    def unloadTreasures(self):
        for treasure in self.treasures:
            treasure.disable()
            treasure.delete()

        self.treasures = []
