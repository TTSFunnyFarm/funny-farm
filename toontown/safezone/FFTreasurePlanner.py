from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.FFTreasure import FFTreasure
from toontown.safezone.TreasurePlanner import TreasurePlanner


class FFTreasurePlanner(TreasurePlanner):
    notify = DirectNotifyGlobal.directNotify.newCategory('FFTreasurePlanner')

    def __init__(self):
        TreasurePlanner.__init__(self, FFTreasure)
