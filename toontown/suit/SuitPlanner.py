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
        self.accept('suitTakeOver', self.spawnSuitBuilding)
        self.accept('eliteTakeOver', self.spawnEliteBuilding)
        self.accept('toonTakeOver', self.collapseBuilding)

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
        self.activeSuits[newSuit.doId] = newSuit
        newSuit.setDNA(requestStatus['dna'])
        newSuit.setLevel(requestStatus['level'])
        newSuit.setElite(requestStatus['elite'])
        newSuit.initializeBodyCollisions('suit')
        newSuit.enableRaycast(1)
        newSuit.reparentTo(base.cr.playGame.street.geom)
        newSuit.enterFromSky(requestStatus['posA'], requestStatus['posB'])
        newSuit.startUpdatePosition()
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

    def spawnSuitBuilding(self, requestStatus):
        if requestStatus['zoneId'] != self.zoneId:
            return
        bldg = None
        townBuildings = base.cr.playGame.getActiveZone().buildings
        for tb in townBuildings:
            if requestStatus['block'] == tb.getBlock():
                bldg = tb
                break
        if bldg:
            bldg.suitTakeOver(requestStatus['track'], requestStatus['difficulty'], requestStatus['numFloors'] - 1)

    def spawnEliteBuilding(self, requestStatus):
        if requestStatus['zoneId'] != self.zoneId:
            return
        bldg = None
        townBuildings = base.cr.playGame.getActiveZone().buildings
        for tb in townBuildings:
            if requestStatus['block'] == tb.getBlock():
                bldg = tb
                break
        if bldg:
            bldg.eliteTakeOver(requestStatus['track'])

    def collapseBuilding(self, requestStatus):
        if requestStatus['zoneId'] != self.zoneId:
            return
        bldg = None
        townBuildings = base.cr.playGame.getActiveZone().buildings
        for tb in townBuildings:
            if requestStatus['block'] == tb.getBlock():
                bldg = tb
                break
        if bldg:
            bldg.toonTakeOver()

    def loadSuits(self):
        # Loads the current batch of suits active on the AI
        ai = base.air.suitPlanners[self.zoneId]
        suits = ai.requestSuits()
        for status in suits:
            suit = BattleSuit()
            suit.setDoId(status['doId'])
            suit.setDNA(status['dna'])
            suit.setLevel(status['level'])
            suit.setElite(status['elite'])
            suit.initializeBodyCollisions('suit')
            suit.enableRaycast(1)
            suit.getGeomNode().setName('suit-%d' % suit.doId)
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

    def loadBuildings(self):
        # Loads the current batch of suit buildings active on the AI
        ai = base.air.suitPlanners[self.zoneId]
        buildings = ai.requestBuildings()
        townBuildings = base.cr.playGame.getActiveZone().buildings
        for status in buildings:
            bldg = None
            for tb in townBuildings:
                if status['block'] == tb.getBlock():
                    bldg = tb
                    break
            if bldg:
                bldg.track = status['track']
                bldg.difficulty = status['difficulty']
                bldg.numFloors = status['numFloors']
                if status['elite']:
                    bldg.setToElite()
                else:
                    bldg.setToSuit()

    def startCheckBattleRange(self):
        taskMgr.add(self.__checkBattleRange, 'checkBattleRange')

    def stopCheckBattleRange(self):
        taskMgr.remove('checkBattleRange')

    def __checkBattleRange(self, task):
        # Checks for suits walking into our battle
        cell = render.find('**/battleCell')
        if cell.isEmpty():
            return task.cont
        for doId in self.activeSuits.keys()[:]: # Iterate over a COPY of activeSuits instead of the original since it'll be constantly changing as this task continues.
            suit = self.activeSuits[doId]
            dist = (suit.getPos() - cell.getPos()).length()
            if dist <= 12:
                ai = base.air.suitPlanners[self.zoneId]
                battle = base.cr.playGame.street.battle
                if battle.suitRequestJoin(suit):
                    # Yay, the suit can join!
                    suit.exitWalk()
                    self.removeActiveSuit(doId)
                    ai.removeSuitAI(doId)
                else:
                    # Gotta blast!
                    ai.removeSuit(doId)
                    # Make inactive right away so we don't check him again
                    self.removeActiveSuit(doId)
                    suit.removeActive()
                    taskMgr.doMethodLater(SuitTimings.toSky, ai.upkeepPopulation, suit.uniqueName('upkeepDelay'))
                return task.cont
        return task.cont
