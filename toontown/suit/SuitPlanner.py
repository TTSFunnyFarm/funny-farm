from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from BattleSuit import BattleSuit
import SuitTimings

class SuitPlanner(DirectObject):

    def __init__(self):
        self.zoneId = 0
        self.activeSuits = {}

    def generate(self):
        self.accept('generateSuit', self.createNewSuit)
        self.accept('removeSuit', self.removeSuit)

    def delete(self):
        self.ignoreAll()
        taskMgr.remove('%d-sptCreateSuit' % self.zoneId)
        taskMgr.remove('%d-sptRemoveSuit' % self.zoneId)
        del self.zoneId
        del self.activeSuits

    def setZoneId(self, zoneId):
        self.zoneId = zoneId

    def getZoneId(self):
        return self.zoneId

    def createNewSuit(self, requestStatus):
        if requestStatus['zoneId'] != self.zoneId:
            return
        newSuit = BattleSuit()
        doId = requestStatus['doId']
        newSuit.setDoId(doId)
        newSuit.setDNA(requestStatus['dna'])
        newSuit.setLevel(requestStatus['level'])
        newSuit.setElite(requestStatus['elite'])
        newSuit.initializeBodyCollisions('suit')
        newSuit.addActive()
        newSuit.reparentTo(base.cr.playGame.street.geom)
        newSuit.enterFromSky(requestStatus['posA'], requestStatus['posB'])
        newSuit.startUpdatePosition()
        self.activeSuits[newSuit.doId] = newSuit
        taskMgr.doMethodLater(SuitTimings.fromSky, self.__handleCreateSuit, '%d-sptCreateSuit' % self.zoneId, [doId])

    def __handleCreateSuit(self, doId):
        suit = self.activeSuits[doId]
        suit.exitFromSky()

    def deleteSuit(self, doId):
        # Instantly removes the suit from the scene graph
        if doId in self.activeSuits.keys():
            suit = self.activeSuits[doId]
            suit.disable()
            suit.delete()
            self.activeSuits.pop(doId)

    def removeSuit(self, doId):
        # Makes the suit fly away first, then deletes it
        if doId in self.activeSuits.keys():
            suit = self.activeSuits[doId]
            suit.exitWalk()
            suit.enterToSky()
            taskMgr.doMethodLater(SuitTimings.toSky, self.__handleRemoveSuit, '%d-sptRemoveSuit' % self.zoneId, [doId])
    
    def __handleRemoveSuit(self, doId):
        suit = self.activeSuits[doId]
        suit.exitToSky()
        self.deleteSuit(doId)

    def loadSuits(self):
        ai = base.air.suitPlanners[self.zoneId]
        suits = ai.requestSuits()
        for status in suits:
            suit = BattleSuit()
            suit.setDoId(status['doId'])
            suit.setDNA(status['dna'])
            suit.setLevel(status['level'])
            suit.setElite(status['elite'])
            suit.initializeBodyCollisions('suit')
            suit.addActive()
            suit.reparentTo(base.cr.playGame.street.geom)
            suit.startUpdatePosition()
            self.activeSuits[suit.doId] = suit
            time = ai.requestTime(suit.doId)
            if time == 0:
                continue
            suit.enterWalk(status['posA'], status['posB'], time)

    def unloadSuits(self):
        for doId in self.activeSuits.keys():
            self.deleteSuit(doId)
