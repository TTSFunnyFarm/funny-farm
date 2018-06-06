from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.TreasurePlannerAI import TreasurePlannerAI


class RegenTreasurePlannerAI(TreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('RegenTreasurePlannerAI')

    def __init__(self, zoneId, treasureConstructor, taskName, spawnInterval, maxTreasures, callback=None):
        TreasurePlannerAI.__init__(self, zoneId, treasureConstructor, callback)
        self.taskName = '%s-%s' % (taskName, zoneId)
        self.spawnInterval = spawnInterval
        self.maxTreasures = maxTreasures

    def start(self):
        pass
