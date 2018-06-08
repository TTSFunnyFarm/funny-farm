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

    def getDoId(self):
        return id(self)

    def validAvatar(self):
        return 1

    def setReject(self):
        if not hasattr(base.cr.playGame.hood, 'treasurePlanner'):
            return

        treasurePlanner = base.cr.playGame.hood.treasurePlanner
        if not treasurePlanner:
            return

        currentTreasure = None
        for treasure in treasurePlanner.treasures:
            if treasure and treasure.getDoId() == self.getDoId():
                currentTreasure = treasure
                break

        if currentTreasure:
            currentTreasure.setReject()

    def generate(self, zoneId):
        pass  # TODO
