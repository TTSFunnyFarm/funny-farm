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
            (-24.24, 28.452, 0.025),
            (1.491, 46.153, 0.025),
            (-49.741, 72.806, 0.025),
            (-71.685, -3.537, 0.025),
            (11.157, -86.375, 0.025),
            (86.543, -74.432, 0.025),
            (54.748, -14.38, 0.025),
            (57.265, -139.102, 0.025),
            (56.261, -183.354, 0.025),
            (-45.574, -151.719, 0.025),
            (-106.276, -166.895, 0.025),
            (-79.49, -121.77, 0.025),
            (11.88, 18.449, 0.025),
            (45.976, -5.008, 0.025),
            (14.083, -17.564, 0.025),
            (-33.324, -184.393, 0.025),
            (-10.912, -173.996, 0.575),
            (41.692, -182.643, 0.025),
            (25.457, -103.143, 0.025),
            (108.956, -33.419, 0.025),
            (-96.03, -65.568, 0.025),
        ]
        return self.spawnPoints
