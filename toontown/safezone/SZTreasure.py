from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.Treasure import Treasure


class SZTreasure(Treasure):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZTreasure')

    def __init__(self):
        Treasure.__init__(self)
