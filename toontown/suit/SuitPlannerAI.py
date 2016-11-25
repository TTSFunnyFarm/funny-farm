from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from toontown.building import SuitBuildingGlobals
from toontown.battle import SuitBattleGlobals
from BattleSuitAI import BattleSuitAI
import SuitDNA
import random

class SuitPlannerAI(DirectObject):
    notify = directNotify.newCategory('SuitPlannerAI')
    notify.setInfo(True)
    SuitHoodInfo = {
        1100: [4,
            8,
            0,
            3,
            1,
            (10,
            10,
            40,
            40),
            (1, 2, 3, 4),
            []
        ]
    }
    SUIT_HOOD_INFO_MIN = 0
    SUIT_HOOD_INFO_MAX = 1
    SUIT_HOOD_INFO_BMIN = 2
    SUIT_HOOD_INFO_BMAX = 3
    SUIT_HOOD_INFO_SMAX = 4
    SUIT_HOOD_INFO_TRACK = 5
    SUIT_HOOD_INFO_LVL = 6
    SUIT_HOOD_INFO_HEIGHTS = 7
    MAX_SUIT_TYPES = 6
    POP_ADJUST_DELAY = 120
    for zoneId in SuitHoodInfo.keys():
        currHoodInfo = SuitHoodInfo[zoneId]
        levels = currHoodInfo[SUIT_HOOD_INFO_LVL]
        heights = [0,
         0,
         0,
         0,
         0]
        for level in levels:
            minFloors, maxFloors = SuitBuildingGlobals.SuitBuildingInfo[level - 1][0]
            for i in range(minFloors - 1, maxFloors):
                heights[i] += 1
        currHoodInfo[SUIT_HOOD_INFO_HEIGHTS] = heights

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.activeSuits = {}

    def generate(self):
        self.createSuits()
        self.initTasks()
        self.accept('removeSuitAI', self.removeSuit)

    def createSuits(self):
        hoodInfo = self.SuitHoodInfo[self.zoneId]
        suitMin = hoodInfo[0]
        suitMax = hoodInfo[1]
        for i in xrange(0, random.randint(suitMin, suitMax)):
            self.createNewSuit()

    def createNewSuit(self):
        # Currently just generates a random suit based on the hood info. 
        # We can add arguments to create specific suits later, if needed.
        newSuit = BattleSuitAI(self)
        newSuit.setZoneId(self.zoneId)
        level, type, track = self.pickLevelTypeAndTrack()
        newSuit.setupSuitDNA(level, type, track)
        newSuit.generate()
        self.activeSuits[newSuit.doId] = newSuit
        self.notify.info('creating suit in zone %d' % self.zoneId)

    def removeSuit(self, doId):
        if doId in self.activeSuits.keys():
            suit = self.activeSuits[doId]
            suit.delete()
            self.activeSuits.pop(doId)
            messenger.send('removeSuit', [doId])

    def requestSuits(self):
        # SuitPlanner asked what suits are on its street; give it all the info
        suits = []
        for doId in self.activeSuits.keys():
            suit = self.activeSuits[doId]
            suits.append({'doId': doId,
             'zoneId': suit.zoneId,
             'dna': suit.dna,
             'level': suit.level,
             'elite': suit.isElite,
             'posA': suit.point[-1],
             'posB': suit.getNextPoint(suit.point)[-1]})
        return suits

    def requestTime(self, doId):
        # Now it requested the task time of a suit's walking task
        # so it can accurately place him in the right spot.
        # * Can't confirm that this is working properly yet; needs some work
        if doId in self.activeSuits.keys():
            suit = self.activeSuits[doId]
            if taskMgr.hasTaskNamed(suit.uniqueName('move')):
                task = taskMgr.getTasksNamed(suit.uniqueName('move'))[0]
                return task.time
            return 0

    def pickLevelTypeAndTrack(self):
        actualLevel = random.choice(self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_LVL])
        typeChoices = range(max(actualLevel - 4, 1), min(actualLevel, self.MAX_SUIT_TYPES) + 1)
        type = random.choice(typeChoices)
        level = actualLevel - type
        track = SuitDNA.suitDepts[SuitBattleGlobals.pickFromFreqList(self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_TRACK])]
        self.notify.debug('pickLevelTypeAndTrack: %d %d %s' % (level, type, track))
        return (level, type, track)

    def initTasks(self):
        self.__waitForNextAdjust()

    def __waitForNextAdjust(self):
        t = random.random() * 4.0 + self.POP_ADJUST_DELAY
        taskMgr.doMethodLater(t, self.adjustSuitPopulation, '%d-sptAdjustPopulation' % self.zoneId)

    def adjustSuitPopulation(self, task):
        hoodInfo = self.SuitHoodInfo[self.zoneId]
        min = hoodInfo[self.SUIT_HOOD_INFO_MIN]
        max = hoodInfo[self.SUIT_HOOD_INFO_MAX]
        suitCount = len(self.activeSuits)
        # See how many suits we should add / remove
        adjustment = random.choice((-1, -1, 0, 0, 0, 1, 1))
        self.notify.info('adjustment: %d' % adjustment)
        # Calculate the total suits we'd have on the street with the adjustment
        suitCount += adjustment
        if suitCount < min or suitCount > max:
            # The total is not within the range of suits for this street, try again later.
            self.__waitForNextAdjust()
            return task.done
        for i in xrange(abs(adjustment)):
            if adjustment < 0:
                # Negative adjustment, take away a suit
                doId = random.choice(self.activeSuits.keys())
                self.notify.info('removing suit %d' % doId)
                self.removeSuit(doId)
            else:
                # Positive adjustment, create a new suit
                self.createNewSuit()
        self.__waitForNextAdjust()
        return task.done
