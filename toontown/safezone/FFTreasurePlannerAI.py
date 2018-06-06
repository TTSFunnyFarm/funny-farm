from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.FFTreasure import FFTreasure
from toontown.safezone.RegenTreasurePlannerAI import RegenTreasurePlannerAI


class FFTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('FFTreasurePlannerAI')

    def __init__(self, air, zoneId):
        RegenTreasurePlannerAI.__init__(self, air, zoneId, FFTreasure, 'FFTreasurePlanner', 20, 5)

    def initSpawnPoints(self):
        return [(0, 0, 0)]  # TODO
