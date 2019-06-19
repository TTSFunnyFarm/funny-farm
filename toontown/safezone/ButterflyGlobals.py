import random

from panda3d.core import *

OFF = 0
FLYING = 1
LANDED = 2
states = {
    OFF: 'off',
    FLYING: 'Flying',
    LANDED: 'Landed'
}
NUM_BUTTERFLIES = (3,)
NUM_BUTTERFLY_AREAS = (4,)
BUTTERFLY_SPEED = 2.0
BUTTERFLY_HEIGHT = (2.2,)
BUTTERFLY_TAKEOFF = (1.4,)
BUTTERFLY_LANDING = (1.4,)
MAX_LANDED_TIME = 20.0
FF = 0
ButterflyPoints = (
    ((Point3(13, -110, 4.4),
      Point3(37, -120, 0.1),
      Point3(56, -120, 0.1),
      Point3(74, -110, 4.4),
      Point3(45, -130, 0.1),
      Point3(65, -145, 0.1),
      Point3(55, -160, 0.1),
      Point3(45, -170, 0.1),
      Point3(60, -170, 0.1),
      Point3(75, -170, 0.1),
      Point3(86.58, -171.2, 4.4),
      Point3(80, -155, 0.1),
      Point3(75, -140, 0.1),
      Point3(65, -130, 0.1),
      Point3(50, -125, 0.1),
      Point3(30, -120, 0.1)),
     (Point3(-13.35, -110, 4.4),
      Point3(-37, -120, 0.1),
      Point3(-56, -120, 0.1),
      Point3(-61.85, -110, 4.4),
      Point3(-45, -130, 0.1),
      Point3(-65, -145, 0.1),
      Point3(-55, -160, 0.1),
      Point3(-45, -170, 0.1),
      Point3(-60, -170, 0.1),
      Point3(-75, -170, 0.1),
      Point3(-86.95, -170.5, 4.4),
      Point3(-80, -155, 0.1),
      Point3(-75, -140, 0.1),
      Point3(-65, -130, 0.1),
      Point3(-50, -125, 0.1),
      Point3(-30, -120, 0.1)),
     (Point3(-53.0, 3.0, -1.8),
      Point3(-58.0, 2.0, -1.8),
      Point3(-58.0, 2.0, -1.8),
      Point3(-76.0, 2.0, -1.8),
      Point3(-69.0, 11.0, -1.8),
      Point3(-100.0, 14.0, -4.1),
      Point3(-104.0, 17.0, -2.6),
      Point3(-125.0, 34.0, 0.1),
      Point3(-124.0, 30.0, 0.1),
      Point3(-113.0, 73.0, 0.6),
      Point3(-33.0, 78.0, 0.1),
      Point3(-65.0, 48.0, -3.0),
      Point3(-51.0, 33.0, -3.0),
      Point3(-30.0, 71.0, 0.1),
      Point3(-26.0, 71.0, 0.1),
      Point3(-23.0, 69.0, 0.1),
      Point3(-23.0, 64.0, 0.1),
      Point3(-5.0, 42.0, 0.1),
      Point3(-22.0, 22.0, 0.1),
      Point3(-27.0, 22.0, 0.1)),
     (Point3(14.0, 93.0, 3.1),
      Point3(17.0, 93.0, 3.1),
      Point3(20.0, 122.0, 2.6),
      Point3(21.0, 127.0, 2.6),
      Point3(23.0, 123.0, 2.6),
      Point3(32.0, 130.0, 2.6),
      Point3(48.0, 148.0, 2.6),
      Point3(64.0, 111.0, 2.6),
      Point3(32.0, 82.0, 2.6),
      Point3(63.0, 90.0, 3.1),
      Point3(68.0, 85.0, 3.1),
      Point3(65.0, 85.0, 3.1),
      Point3(70.0, 95.0, 3.1))),
    ((Point3(-7.9, 22.9, 0.05),
      Point3(-8.0, 17.0, 2.1),
      Point3(-7.5, 18.0, 2.1),
      Point3(-27.5, 70.7, 0.05),
      Point3(-30.0, 70.0, 1.0),
      Point3(-31.0, 69.0, 1.0),
      Point3(-1.0, 53.0, 2.2),
      Point3(-0.5, 53.0, 2.2),
      Point3(35.0, 71.5, 1.0),
      Point3(33.0, 69.0, 0.05),
      Point3(45.0, 61.0, 0.05),
      Point3(55.0, 62.0, 0.05),
      Point3(80.0, 74.0, 0.05),
      Point3(80.0, 73.0, 0.05),
      Point3(76.0, 46.0, 0.05),
      Point3(76.0, 45.0, 0.05),
      Point3(77.0, 41.0, 0.05),
      Point3(62.0, 28.0, 0.05),
      Point3(48.0, 24.0, 0.05),
      Point3(83.0, 122.0, 0.05),
      Point3(82.0, 123.0, 0.05),
      Point3(81.0, 81.0, 0.05),
      Point3(38.0, 77.0, 0.05),
      Point3(-26.0, 69.0, 0.05),
      Point3(-26.0, 70.0, 0.05),
      Point3(-61.0, 71.0, 0.05),
      Point3(-61.0, 70.0, 0.05),
      Point3(-78.0, 79.0, 0.05),
      Point3(-99.0, 106.0, 0.05),
      Point3(-99.0, 108.0, 0.05),
      Point3(-80.0, 123.0, 0.05),
      Point3(-77.0, 125.0, 0.05),
      Point3(-32.0, 162.0, 0.05),
      Point3(-3.0, 186.5, 2.2),
      Point3(-3.2, 186.8, 2.2),
      Point3(-1.0, 185.0, 2.2),
      Point3(39.0, 165.0, 0.05),
      Point3(42.0, 162.0, 0.05),
      Point3(62.0, 145.0, 0.05),
      Point3(64.0, 145.0, 0.05),
      Point3(59.0, 102.0, 0.05),
      Point3(32.7, 93.7, 0.05),
      Point3(31.2, 90.8, 0.05),
      Point3(29.8, 140.1, 0.05),
      Point3(16.5, 146.3, 0.05),
      Point3(15.3, 146.9, 0.05),
      Point3(-24.3, 128.6, 0.05),
      Point3(-67.9, 117.9, 0.05),
      Point3(-41.6, 88.4, 0.05),
      Point3(-13.6, 120.3, 0.05),
      Point3(26.0, 117.8, 0.05),
      Point3(22.6, 112.3, 0.05),
      Point3(-8.2, 107.9, 0.05),
      Point3(-18.1, 97.0, 0.05),
      Point3(-21.4, 92.9, 0.05),
      Point3(-2.1, 74.0, 0.05),
      Point3(19.8, 93.5, 0.05),
      Point3(21.4, 95.4, 0.05),
      Point3(19.2, 97.5, 0.05),
      Point3(-10.7, 143.3, 0.05),
      Point3(38.2, 120.7, 0.05),
      Point3(34.1, 101.5, 0.05),
      Point3(32.4, 96.5, 0.05),
      Point3(72.9, 121.8, 0.05)),)
)
allocatedIndexes = {}


def generateIndexes(doId, playground):
    usedI = []
    unusedI = []
    for area in ButterflyPoints[playground]:
        usedI.append(range(0, len(area)))
        unusedI.append([])

    allocatedIndexes[doId] = (usedI, unusedI)


def clearIndexes(doId):
    if doId in allocatedIndexes:
        del allocatedIndexes[doId]


def getFirstRoute(playground, area, doId):
    curPos, curIndex = __getCurrentPos(playground, area, doId)
    destPos, destIndex, time = getNextPos(curPos, playground, area, doId)
    return curPos, curIndex, destPos, destIndex, time


def __getCurrentPos(playground, area, doId):
    if doId in allocatedIndexes:
        unusedI = allocatedIndexes[doId][0][area]
        usedI = allocatedIndexes[doId][1][area]
    else:
        return ButterflyPoints[playground][area][0], 0
    if len(unusedI) == 0:
        index = random.choice(usedI)
        return ButterflyPoints[playground][area][index], index
    index = random.choice(unusedI)
    unusedI.remove(index)
    usedI.append(index)
    return ButterflyPoints[playground][area][index], index


def getNextPos(currentPos, playground, area, doId):
    if doId in allocatedIndexes:
        unusedI = allocatedIndexes[doId][0][area]
        usedI = allocatedIndexes[doId][1][area]
    else:
        return ButterflyPoints[playground][area][0], 0, 4.0
    nextPos = currentPos
    while nextPos == currentPos:
        if len(unusedI) == 0:
            index = random.choice(usedI)
            nextPos = ButterflyPoints[playground][area][index]
        else:
            index = random.choice(unusedI)
            nextPos = ButterflyPoints[playground][area][index]
            if nextPos != currentPos:
                unusedI.remove(index)
                usedI.append(index)

    dist = Vec3(nextPos - currentPos).length()
    time = dist / BUTTERFLY_SPEED + BUTTERFLY_TAKEOFF[playground] + BUTTERFLY_LANDING[playground]
    return nextPos, index, time


def recycleIndex(index, playground, area, doId):
    if doId in allocatedIndexes:
        unusedI = allocatedIndexes[doId][0][area]
        usedI = allocatedIndexes[doId][1][area]
    else:
        return None
    if usedI.count(index) > 0:
        usedI.remove(index)
    if unusedI.count(index) == 0:
        unusedI.append(index)
    return None
