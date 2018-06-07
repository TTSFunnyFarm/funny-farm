from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


class TreasureAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('Treasure')

    def __init__(self, air, treasurePlanner, x, y, z):
        DirectObject.__init__(self)
        self.air = air
        self.treasurePlanner = treasurePlanner
        self.pos = (x, y, z)

    def getPosition(self):
        return self.pos

    def generate(self, zoneId):
        pass  # TODO
