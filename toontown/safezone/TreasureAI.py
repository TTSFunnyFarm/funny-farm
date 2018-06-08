from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


class TreasureAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('Treasure')

    def __init__(self, air, treasurePlanner, x, y, z):
        DirectObject.__init__(self)
        self.air = air
        self.treasurePlanner = treasurePlanner
        self.pos = (x, y, z)

    def delete(self):
        self.deleteClientTreasure()
        del self.air
        del self.treasurePlanner
        del self.pos

    def getPosition(self):
        return self.pos

    def getDoId(self):
        return id(self)

    def validAvatar(self):
        return 1

    def getClientTreasure(self):
        if not hasattr(base.cr.playGame.hood, 'treasurePlanner'):
            return

        treasurePlanner = base.cr.playGame.hood.treasurePlanner
        if not treasurePlanner:
            return

        clientTreasure = None
        for treasure in treasurePlanner.treasures:
            if treasure and treasure.getDoId() == self.getDoId():
                clientTreasure = treasure
                break

        return clientTreasure

    def setReject(self):
        clientTreasure = self.getClientTreasure()
        if clientTreasure:
            clientTreasure.setReject()

    def setGrab(self):
        clientTreasure = self.getClientTreasure()
        if clientTreasure:
            clientTreasure.setGrab()

    def deleteClientTreasure(self):
        clientTreasure = self.getClientTreasure()
        if clientTreasure:
            clientTreasure.disable()
            clientTreasure.delete()

    def generate(self, zoneId):
        pass  # TODO

    def uniqueName(self, idString):
        return '%s-%s' % (idString, str(id(self)))
