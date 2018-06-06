from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


class TreasurePlannerAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('TreasurePlannerAI')

    def __init__(self, zoneId, treasureConstructor, callback=None):
        DirectObject.__init__(self)
        self.zoneId = zoneId
        self.treasureConstructor = treasureConstructor
        self.callback = callback
        self.spawnPoints = self.initSpawnPoints()
        self.treasures = []
        for _ in self.spawnPoints:
            self.treasures.append(None)

        self.deleteTaskNames = set()
        self.lastRequestId = None
        self.requestStartTime = None
        self.requestCount = None

    def initSpawnPoints(self):
        raise NotImplementedError('initSpawnPoints')  # Must be overridden by subclass.

    def nthEmptyIndex(self, n):
        emptyCounter = -1
        spawnPointCounter = -1
        while emptyCounter < n:
            spawnPointCounter += 1
            if self.treasures[spawnPointCounter] is None:
                emptyCounter += 1

        return spawnPointCounter

    def countEmptySpawnPoints(self):
        counter = 0
        for treasure in self.treasures:
            if treasure is None:
                counter += 1

        return counter

    def placeTreasure(self, index):
        pass

    def numTreasures(self):
        counter = 0
        for treasure in self.treasures:
            if treasure:
                counter += 1

        return counter
