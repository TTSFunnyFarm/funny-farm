from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.TreasureAI import TreasureAI


class SZTreasureAI(TreasureAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZTreasure')

    def __init__(self, air, treasurePlanner, x, y, z):
        TreasureAI.__init__(self, air, treasurePlanner, x, y, z)
        self.healAmount = treasurePlanner.healAmount
