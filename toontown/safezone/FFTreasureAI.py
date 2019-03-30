from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.SZTreasureAI import SZTreasureAI


class FFTreasureAI(SZTreasureAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('FFTreasure')

    def __init__(self, air, treasurePlanner, x, y, z):
        SZTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
