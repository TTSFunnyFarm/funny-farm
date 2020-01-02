import random

from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.TreasurePlannerAI import TreasurePlannerAI


class RegenTreasurePlannerAI(TreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('RegenTreasurePlannerAI')

    def __init__(self, air, zoneId, treasureConstructor, taskName, spawnInterval, maxTreasures, callback=None):
        TreasurePlannerAI.__init__(self, air, zoneId, treasureConstructor, callback)
        self.taskName = '%s-%s' % (taskName, zoneId)
        self.spawnInterval = spawnInterval
        self.maxTreasures = maxTreasures

    def start(self):
        self.preSpawnTreasures()
        self.startSpawning()

    def preSpawnTreasures(self):
        for i in range(self.maxTreasures):
            self.placeRandomTreasure()

    def placeRandomTreasure(self):
        self.notify.debug('Placing a Treasure...')
        spawnPointIndex = self.nthEmptyIndex(random.randrange(self.countEmptySpawnPoints()))
        self.placeTreasure(spawnPointIndex)

    def startSpawning(self):
        self.stopSpawning()
        taskMgr.doMethodLater(self.spawnInterval, self.upkeepTreasurePopulation, self.taskName)

    def stopSpawning(self):
        taskMgr.remove(self.taskName)

    def upkeepTreasurePopulation(self, task):
        if self.numTreasures() < self.maxTreasures:
            self.placeRandomTreasure()
        taskMgr.doMethodLater(self.spawnInterval, self.upkeepTreasurePopulation, self.taskName)
        return task.done
