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
        self.accept('removeActiveSuit', self.removeActiveSuit)
        taskMgr.add(self.__checkBattleRange, 'checkBattleRange')

    def delete(self):
        self.ignoreAll()
        taskMgr.remove('checkBattleRange')
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
        if not base.cr.playGame.getActiveZone().place:
            newSuit.addActive()
        newSuit.reparentTo(base.cr.playGame.street.geom)
        newSuit.enterFromSky(requestStatus['posA'], requestStatus['posB'])
        newSuit.startUpdatePosition()
        self.activeSuits[newSuit.doId] = newSuit
        taskMgr.doMethodLater(SuitTimings.fromSky, self.__handleCreateSuit, '%d-sptCreateSuit' % self.zoneId, [newSuit])

    def __handleCreateSuit(self, suit):
        suit.exitFromSky()

    def deleteSuit(self, suit):
        # Instantly removes the suit from the scene graph
        suit.disable()
        suit.delete()
        self.removeActiveSuit(suit.doId)

    def removeSuit(self, doId):
        # Makes the suit fly away first, then deletes it
        if doId in self.activeSuits.keys():
            suit = self.activeSuits[doId]
            suit.exitWalk()
            suit.enterToSky()
            taskMgr.doMethodLater(SuitTimings.toSky, self.__handleRemoveSuit, '%d-sptRemoveSuit' % self.zoneId, [suit])

    def __handleRemoveSuit(self, suit):
        suit.exitToSky()
        self.deleteSuit(suit)

    def removeActiveSuit(self, doId):
        # Simply removes the suit from the list of active suits
        if doId in self.activeSuits.keys():
            self.activeSuits.pop(doId)

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
            suit = self.activeSuits[doId]
            self.deleteSuit(suit)

    def __checkBattleRange(self, task):
        # Checks for suits walking into our battle
        cell = render.find('**/battleCell')
        if cell.isEmpty():
            return task.cont
        for doId in self.activeSuits:
            suit = self.activeSuits[doId]
            dist = (suit.getPos() - cell.getPos()).length()
            if dist <= 12:
                ai = base.air.suitPlanners[self.zoneId]
                ai.removeSuit(doId)
                # Make inactive right away so we don't check him again
                self.removeActiveSuit(doId)
                taskMgr.doMethodLater(SuitTimings.toSky, ai.upkeepPopulation, suit.uniqueName('upkeepDelay'))
                return task.cont
        return task.cont
