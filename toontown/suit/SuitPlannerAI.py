from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from toontown.building import SuitBuildingGlobals
from toontown.building.BuildingAI import BuildingAI
from toontown.battle import SuitBattleGlobals
from toontown.suit.BattleSuitAI import BattleSuitAI
from toontown.suit import SuitPoints
from toontown.suit import SuitDNA
import random

class SuitPlannerAI(DirectObject):
    notify = directNotify.newCategory('SuitPlannerAI')
    notify.setInfo(True)
    SuitHoodInfo = {
        1100: (4,
            8,
            0,
            0,
            0,
            1,
            (5,
            5,
            45,
            45),
            (1, 3),
            (0, 0)
        ),
        1200: (4,
            8,
            0,
            1,
            0,
            1,
            (40,
            40,
            10,
            10),
            (2, 4),
            (0, 1)
        ),
        2100: (4,
            8,
            0,
            3,
            1,
            2,
            (10,
            40,
            40,
            10),
            (3, 5),
            (1, 2)
        ),
        2200: (4,
            8,
            0,
            3,
            1,
            2,
            (40,
            10,
            10,
            40),
            (4, 6),
            (2, 3)
        ),
        3100: (4,
            8,
            0,
            3,
            1,
            2,
            (10,
            70,
            10,
            10),
            (5, 7),
            (3, 4)
        ),
        3200: (4,
            8,
            0,
            3,
            1,
            2,
            (30,
            10,
            30,
            30),
            (6, 8),
            (4, 5)
        ),
        3300: (4,
            8,
            0,
            3,
            1,
            2,
            (25,
            25,
            25,
            25),
            (6, 8),
            (5, 6)
        ),
        4100: (4,
            8,
            0,
            3,
            1,
            2,
            (40,
            10,
            40,
            10),
            (7, 9),
            (6, 7)
        ),
        4200: (4,
            8,
            0,
            3,
            1,
            2,
            (10,
            40,
            10,
            40),
            (8, 10),
            (6, 8)
        ),
    }
    SUIT_HOOD_INFO_MIN = 0 # min number of active suits
    SUIT_HOOD_INFO_MAX = 1 # max number of active suits
    SUIT_HOOD_INFO_BMIN = 2 # min number of suit buildings
    SUIT_HOOD_INFO_BMAX = 3 # max number of suit buildings
    SUIT_HOOD_INFO_ELITE = 4 # elite buildings yes or no
    SUIT_HOOD_INFO_SMAX = 5 # max number of suits in a battle
    SUIT_HOOD_INFO_TRACK = 6 # suit dept probabilities
    SUIT_HOOD_INFO_LVL = 7 # possible suit levels (min, max)
    SUIT_HOOD_INFO_HEIGHTS = 8 # possible bldg difficulties (min, max)
    MAX_SUIT_TYPES = 8
    POP_UPKEEP_DELAY = 10
    POP_ADJUST_DELAY = 120
    BLDG_ADJUST_DELAY = 240
    BCHANCE_ELITE = 50
    # for zoneId in list(SuitHoodInfo.keys()):
    #     currHoodInfo = SuitHoodInfo[zoneId]
    #     levels = currHoodInfo[SUIT_HOOD_INFO_LVL]
    #     heights = [0,
    #      0,
    #      0,
    #      0,
    #      0]
    #     for level in levels:
    #         minFloors, maxFloors = SuitBuildingGlobals.SuitBuildingInfo[level - 1][0]
    #         for i in range(minFloors - 1, maxFloors):
    #             heights[i] += 1
    #     currHoodInfo[SUIT_HOOD_INFO_HEIGHTS] = heights

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.activeSuits = {}
        self.buildingMap = {}
        self.toonBuildings = None
        self.setBattlesJoinable()

    def generate(self):
        self.createSuits()
        self.createBuildings()
        self.initTasks()
        self.accept('createNewSuit-%d' % self.zoneId, self.createNewSuit)
        self.accept('upkeepPopulation-%d' % self.zoneId, self.upkeepPopulation)
        self.accept('requestBattle-%d' % self.zoneId, self.requestBattle)
        self.accept('spawnBuilding-%d' % self.zoneId, self.spawnBuilding)
        self.accept('collapseBuilding-%d' % self.zoneId, self.collapseBuilding)

    def setBattlesJoinable(self):
        self.battlesJoinable = 0
        if self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_SMAX] > 1:
            self.battlesJoinable = 1

    def createSuits(self):
        hoodInfo = self.SuitHoodInfo[self.zoneId]
        suitMin = hoodInfo[self.SUIT_HOOD_INFO_MIN]
        suitMax = hoodInfo[self.SUIT_HOOD_INFO_MAX]
        for i in range(0, random.randint(suitMin, suitMax)):
            self.createNewSuit()

    def createBuildings(self):
        # Randomly generates some suit buildings on the street (or none at all).
        # Algorithm may be adjusted as I see fit.
        for block in SuitPoints.BuildingBlocks[self.zoneId]:
            self.buildingMap[block] = BuildingAI(self.zoneId, block)
        self.toonBuildings = list(self.buildingMap.keys())[:]
        hoodInfo = self.SuitHoodInfo[self.zoneId]
        bldgMin = hoodInfo[self.SUIT_HOOD_INFO_BMIN]
        bldgMax = hoodInfo[self.SUIT_HOOD_INFO_BMAX]
        bldgRange = [0, 0, 0]
        bldgRange.extend(range(bldgMin, bldgMax + 1))
        spawn = random.choice(bldgRange)
        if spawn > 0:
            for i in range(spawn):
                self.spawnBuilding()

    def createNewSuit(self, type=None, level=None):
        # Currently just generates a random suit based on the hood info.
        # We can add arguments to create specific suits later, if needed.
        newSuit = BattleSuitAI(self)
        newSuit.setDoId(base.air.getNextSuitIndex())
        newSuit.setZoneId(self.zoneId)
        level, type, track = self.pickLevelTypeAndTrack()
        newSuit.setupSuitDNA(type, track)
        newSuit.setLevel(level)
        newSuit.generate()
        self.activeSuits[newSuit.doId] = newSuit
        self.notify.debug('Creating suit %d in zone (%d)' % (newSuit.doId, self.zoneId))

    def removeSuit(self, doId):
        # Removes both AI and client presence
        self.removeSuitAI(doId)
        messenger.send('removeSuit', [doId])

    def removeSuitAI(self, doId):
        # Removes only the AI presence
        if doId in list(self.activeSuits.keys()):
            suit = self.activeSuits[doId]
            suit.delete()
            self.activeSuits.pop(doId)

    def requestSuits(self):
        # SuitPlanner asked what suits are on its street; give it all the info it might need
        suits = []
        for doId in list(self.activeSuits.keys()):
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
        # Now request the current time of the suit's walking task
        # so it can accurately place it in the right spot.
        if doId in list(self.activeSuits.keys()):
            suit = self.activeSuits[doId]
            if taskMgr.hasTaskNamed(suit.uniqueName('move')):
                task = taskMgr.getTasksNamed(suit.uniqueName('move'))[0]
                # TODO: DIAGNOSE WHY task.time is returning a negative!
                return abs(task.time)
            return 0

    def pickLevelTypeAndTrack(self):
        actualLevel = random.randint(*self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_LVL]) - 1
        minType = max(actualLevel - 4, 1)
        maxType = min(actualLevel, self.MAX_SUIT_TYPES) + 1
        type = random.randint(minType, maxType)
        level = actualLevel
        track = SuitDNA.suitDepts[SuitBattleGlobals.pickFromFreqList(self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_TRACK])]
        self.notify.debug('pickLevelTypeAndTrack: %d %d %s' % (level, type, track))
        return (level, type, track)

    def spawnBuilding(self, block=None):
        # Generates a random suit building on the given block,
        # or on a random block if not provided.
        track, difficulty, numFloors = self.pickBuildingStats()
        if not block:
            block = random.choice(self.toonBuildings)
        bldg = self.buildingMap[block]
        if self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_ELITE]:
            elite = int(random.randint(1, 100) >= BCHANCE_ELITE)
            if elite:
                bldg.eliteTakeOver(track)
            else:
                bldg.suitTakeOver(track, difficulty, numFloors)
        else:
            bldg.suitTakeOver(track, difficulty, numFloors)
        if block in self.toonBuildings:
            self.toonBuildings.remove(block)
        self.notify.debug('spawning suit building in zone %d, block %d' % (self.zoneId, block))

    def collapseBuilding(self, block):
        bldg = self.buildingMap[block]
        if bldg.mode == 'toon':
            self.notify.warning('Unable to collapse toon building. Block: %d' % block)
            return
        bldg.toonTakeOver()
        if block not in self.toonBuildings:
            self.toonBuildings.append(block)

    def pickBuildingStats(self):
        track = SuitDNA.suitDepts[SuitBattleGlobals.pickFromFreqList(self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_TRACK])]
        difficulty = random.randint(*self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_HEIGHTS])
        numFloors = random.randint(*SuitBuildingGlobals.SuitBuildingInfo[difficulty][0])
        return (track, difficulty, numFloors)

    def requestBuildings(self):
        buildings = []
        for block in list(self.buildingMap.keys()):
            bldg = self.buildingMap[block]
            if bldg.mode != 'toon':
                buildings.append({'block': block,
                 'track': bldg.track,
                 'difficulty': bldg.difficulty,
                 'numFloors': bldg.numFloors,
                 'elite': bldg.mode == 'elite'})
        return buildings

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
        adjustment = random.choice((-1, 0, 0, 1))
        self.notify.debug('adjustment: %d' % adjustment)
        # Calculate the total suits we'd have on the street with the adjustment
        suitCount += adjustment
        if suitCount < min or suitCount > max:
            # The total is not within the range of suits for this street, try again later.
            self.__waitForNextAdjust()
            return task.done
        if adjustment < 0:
            # Negative adjustment, take away a suit
            doId = list(self.activeSuits.keys())[0]
            self.notify.debug('Removing suit (%d)' % doId)
            self.removeSuit(doId)
        else:
            # Positive adjustment, create a new suit
            self.createNewSuit()
        self.__waitForNextAdjust()
        return task.done

    def upkeepPopulation(self, task=None):
        # Considers adding another suit to upkeep the population
        suitCount = len(self.activeSuits)
        maxSuits = self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_MAX]
        minSuits = self.SuitHoodInfo[self.zoneId][self.SUIT_HOOD_INFO_MIN]
        if suitCount >= maxSuits or suitCount < minSuits:
            choice = int(suitCount < minSuits)
        else:
            choice = random.choice((0, 0, 0, 1, 1, 1))
        if choice:
            self.createNewSuit()
        if task:
            return task.done

    def requestBattle(self, suitId, pos):
        if suitId not in list(self.activeSuits.keys()):
            return
        toon = None
        if hasattr(base, "localAvatar"):
            toon = base.localAvatar
        if not toon:
            return
        if not toon.getWantBattles():
            return
        # Don't need the suit AI anymore, the battle will take it from here
        self.removeSuitAI(suitId)
        # Find the nearest battle cell
        distances = []
        for cell in SuitPoints.BattleCells[self.zoneId]:
            dist = (pos - cell[0]).lengthSquared()
            distances.append(dist)
        choice = min(distances)
        index = distances.index(choice)
        cell = SuitPoints.BattleCells[self.zoneId][index]
        # Send it over to the client!
        messenger.send('sptRequestBattle-%d' % self.zoneId, [suitId, cell])
