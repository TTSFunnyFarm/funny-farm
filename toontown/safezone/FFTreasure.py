from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.SZTreasure import SZTreasure


class FFTreasure(SZTreasure):
    notify = DirectNotifyGlobal.directNotify.newCategory('FFTreasure')

    def __init__(self, air, treasurePlanner, x, y, z):
        SZTreasure.__init__(self, air, treasurePlanner, x, y, z)
