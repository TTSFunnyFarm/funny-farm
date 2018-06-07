from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.FFTreasureAI import FFTreasureAI
from toontown.safezone.RegenTreasurePlannerAI import RegenTreasurePlannerAI


class FFTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('FFTreasurePlannerAI')

    def __init__(self, air, zoneId):
        self.healAmount = 3
        RegenTreasurePlannerAI.__init__(self, air, zoneId, FFTreasureAI, 'FFTreasurePlanner', 20, 5)

    def initSpawnPoints(self):
        self.spawnPoints = [
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ]
        return self.spawnPoints
