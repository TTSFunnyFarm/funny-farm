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
NUM_BUTTERFLIES = ()  # TODO
NUM_BUTTERFLY_AREAS = ()  # TODO
BUTTERFLY_SPEED = 2.0
BUTTERFLY_HEIGHT = ()  # TODO
BUTTERFLY_TAKEOFF = ()  # TODO
BUTTERFLY_LANDING = ()  # TODO
MAX_LANDED_TIME = 20.0
FF = 0
ButterflyPoints = (
    # TODO
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
