from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.RegenTreasurePlannerAI import RegenTreasurePlannerAI


class FFTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('FFTreasurePlannerAI')

    def __init__(self, zoneId):
        pass
