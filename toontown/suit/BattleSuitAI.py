from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from SuitBase import SuitBase
import SuitDNA
import SuitPoints
import SuitTimings
import random

class BattleSuitAI(SuitBase):
    notify = directNotify.newCategory('BattleSuitAI')

    def __init__(self):
        SuitBase.__init__(self)
        self.doId = id(self)
        self.name = ''
        self.zoneId = 0
        self.legList = None
        self.point = None

    def getDoId(self):
        return self.doId

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, self.doId))

    def generate(self):
        # Initialize the suit's position
        self.legList = SuitPoints.SuitPoints.get(self.zoneId, [])
        # TODO Figure out another way to choose a position; too many suits spawning 
        # in the same spot / extremely close together
        self.point = random.choice(self.legList)
        # Send our info over to SuitPlanner
        messenger.send('generateSuit', [{'doId': self.doId,
         'zoneId': self.zoneId,
         'dna': self.dna,
         'level': self.level,
         'elite': self.isElite,
         'posA': self.point[-1],
         'posB': self.getNextPoint(self.point)[-1]}])
        # This task waits until BattleSuit finishes landing, then starts the walking task.
        # It's important that we add the 0.1 second delay, otherwise the AI's "fromSky" often 
        # finishes before the client does, resulting in no update event being received.
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

    def nextPoint(self, task):
        prevPoint = self.point
        self.point = self.getNextPoint(prevPoint)
        # Send the positions to BattleSuit. We don't just keep in check with it, we literally control where it goes.
        messenger.send('updatePos-%d' % self.doId, [prevPoint[-1], self.point[-1]])
        taskMgr.remove(self.uniqueName('move'))
        delay = self.getLegTime(prevPoint[-1], self.point[-1])
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

    def enterBattle(self):
        taskMgr.remove(self.uniqueName('move'))
