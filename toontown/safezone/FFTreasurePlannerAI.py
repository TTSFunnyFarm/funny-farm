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
            (25, -95, 0.025),
            (60, -88.5, 0.025),
            (-25, -88.5, 0.025),
            (-60, -95, 0.025),
            (-55, 0, 0.025),
            (0, -2, 0.536),
            (-24, 30, 0.536),
            (35, 18, 0.536),
            (57, 69, 0.536),
            (-47, 83, 0.536),
            (45, -45, 0.025),
            (55, 0, 0.025),
            (108, -32, 0.025),
            (-118, -10, 0.025),
            (-118, -50, 0.025),
            (-75, 45, 0.025),
            (21, 64, 0.536),
            (30, -130, 0.025),
            (70, -180, 0.025),
            (-25, -192.5, 0.025),
            (-98, -165, 0.025)
        ]
        return self.spawnPoints
