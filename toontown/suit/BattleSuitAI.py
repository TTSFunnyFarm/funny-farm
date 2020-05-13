from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.suit.SuitBase import SuitBase
from toontown.suit import SuitDNA
from toontown.suit import SuitPoints
from toontown.suit import SuitTimings
import random

class BattleSuitAI(SuitBase):
    notify = directNotify.newCategory('BattleSuitAI')

    def __init__(self, suitPlanner):
        SuitBase.__init__(self)
        self.doId = 0
        self.sp = suitPlanner
        self.name = ''
        self.zoneId = 0
        self.legList = None
        self.point = None

    def setDoId(self, doId):
        self.doId = doId

    def getDoId(self):
        return self.doId

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, self.doId))

    def generate(self):
        self.initializePath()
        # Sends the info over to SuitPlanner
        messenger.send('generateSuit', [{'doId': self.doId,
         'zoneId': self.zoneId,
         'dna': self.dna,
         'level': self.level,
         'elite': self.isElite,
         'posA': self.point[-1],
         'posB': self.getNextPoint(self.point)[-1]}])
        # Waits until BattleSuit finishes landing, then starts the walking task.
        taskMgr.doMethodLater(SuitTimings.fromSky + 0.1, self.nextPoint, self.uniqueName('fromSky'))

    def delete(self):
        SuitBase.delete(self)
        taskMgr.remove(self.uniqueName('move'))

    def setZoneId(self, zoneId):
        self.zoneId = zoneId

    def getZoneId(self):
        return self.zoneId

    def setupSuitDNA(self, level, type, track):
        dna = SuitDNA.SuitDNA()
        dna.newSuitRandom(type, track)
        self.dna = dna
        self.setLevel(level)

    def initializePath(self):
        self.legList = SuitPoints.SuitPoints.get(self.zoneId, [])
        # First try picking a random point
        self.point = random.choice(self.legList)
        for doId in self.sp.activeSuits:
            suit = self.sp.activeSuits[doId]
            # If the suit is within 40 units of any other suit, try again.
            # We don't want any suits spawning on top of each other.
            if (self.point[-1] - suit.point[-1]).length() < 40:
                self.initializePath()
                return
        # We don't want suits spawning on top of our battles either!
        if not render.find('**/battleCell').isEmpty():
            cell = render.find('**/battleCell')
            if (self.point[-1] - cell.getPos()).length() <= 12:
                self.initializePath()

    def nextPoint(self, task):
        prevPoint = self.point
        self.point = self.getNextPoint(prevPoint)
        # Send the positions to BattleSuit. We don't just keep in check with it, we literally control where it goes.
        messenger.send('updatePos-%d' % self.doId, [prevPoint[-1], self.point[-1]])
        taskMgr.remove(self.uniqueName('move'))
        delay = self.getLegTime(prevPoint[-1], self.point[-1])
        print(delay)
        taskMgr.doMethodLater(delay, self.nextPoint, self.uniqueName('move'))
        return task.done

    def getNextPoint(self, point):
        try:
            # Go to the next point in the list
            point = self.legList[self.legList.index(point) + 1]
        except IndexError:
            # We got to the end of the list, start over.
            point = self.legList[0]
        return point

    def getLegTime(self, posA, posB):
        return (posA - posB).length() / ToontownGlobals.SuitWalkSpeed
