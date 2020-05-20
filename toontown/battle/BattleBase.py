from panda3d.core import *
from toontown.toonbase.ToontownBattleGlobals import *
from direct.task.Timer import *
import math
from direct.directnotify import DirectNotifyGlobal
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.battle.BattleGlobals import *
import functools

def levelAffectsGroup(track, level):
    return attackAffectsGroup(track, level)

def attackAffectsGroup(track, level, type = None):
    if track == NPCSOS or type == NPCSOS or track == PETSOS or type == PETSOS:
        return 1
    elif track >= 0 and track <= DROP_TRACK:
        return AvPropTargetCat[AvPropTarget[track]][level]
    else:
        return 0

def getToonAttack(id, track = NO_ATTACK, level = -1, target = -1):
    return [id,
     track,
     level,
     target,
     [],
     0,
     0,
     [],
     0,
     0]

def getDefaultSuitAttacks():
    suitAttacks = [[NO_ID,
      NO_ATTACK,
      -1,
      [],
      0,
      0,
      0,
      0],
     [NO_ID,
      NO_ATTACK,
      -1,
      [],
      0,
      0,
      0,
      0],
     [NO_ID,
      NO_ATTACK,
      -1,
      [],
      0,
      0,
      0,
      0],
     [NO_ID,
      NO_ATTACK,
      -1,
      [],
      0,
      0,
      0,
      0]]
    return suitAttacks

def getDefaultSuitAttack():
    return [NO_ID,
     NO_ATTACK,
     -1,
     [],
     0,
     0,
     0]

def findToonAttack(toons, attacks, track):
    foundAttacks = []
    for t in toons:
        if t in attacks:
            attack = attacks[t]
            local_track = attack[TOON_TRACK_COL]
            if track != NPCSOS and attack[TOON_TRACK_COL] == NPCSOS:
                local_track = NPCToons.getNPCTrack(attack[TOON_TGT_COL])
            if local_track == track:
                if local_track == FIRE:
                    canFire = 1
                    for attackCheck in foundAttacks:
                        if attackCheck[TOON_TGT_COL] == attack[TOON_TGT_COL]:
                            canFire = 0

                    if canFire:
                        foundAttacks.append(attack)
                else:
                    foundAttacks.append(attack)

    def compFunc(a, b):
        if a[TOON_LVL_COL] > b[TOON_LVL_COL]:
            return 1
        elif a[TOON_LVL_COL] < b[TOON_LVL_COL]:
            return -1
        return 0

    foundAttacks.sort(key=functools.cmp_to_key(compFunc))
    return foundAttacks

class BattleBase:
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleBase')
    suitPoints = (((Point3(0, 5, 0), 179),),
     ((Point3(2, 5.3, 0), 170), (Point3(-2, 5.3, 0), 180)),
     ((Point3(4, 5.2, 0), 170), (Point3(0, 6, 0), 179), (Point3(-4, 5.2, 0), 190)),
     ((Point3(6, 4.4, 0), 160),
      (Point3(2, 6.3, 0), 170),
      (Point3(-2, 6.3, 0), 190),
      (Point3(-6, 4.4, 0), 200)))
    suitPendingPoints = ((Point3(-4, 8.2, 0), 190),
     (Point3(0, 9, 0), 179),
     (Point3(4, 8.2, 0), 170),
     (Point3(8, 3.2, 0), 160))
    toonPoints = (((Point3(0, -6, 0), 0),),
     ((Point3(1.5, -6.5, 0), 5), (Point3(-1.5, -6.5, 0), -5)),
     ((Point3(3, -6.75, 0), 5), (Point3(0, -7, 0), 0), (Point3(-3, -6.75, 0), -5)),
     ((Point3(4.5, -7, 0), 10),
      (Point3(1.5, -7.5, 0), 5),
      (Point3(-1.5, -7.5, 0), -5),
      (Point3(-4.5, -7, 0), -10)))
    toonPendingPoints = ((Point3(-3, -8, 0), -5),
     (Point3(0, -9, 0), 0),
     (Point3(3, -8, 0), 5),
     (Point3(5.5, -5.5, 0), 20))
    suitSpeed = 4.8
    toonSpeed = 8.0

    def __init__(self):
        self.pos = Point3(0, 0, 0)
        self.initialSuitPos = Point3(0, 1, 0)
        self.timer = Timer()
        self.resetLists()

    def resetLists(self):
        self.cogs = []
        self.pendingSuits = []
        self.joiningSuits = []
        self.activeSuits = []
        self.luredSuits = []
        self.suitGone = 0
        self.toons = []
        self.joiningToons = []
        self.pendingToons = []
        self.activeToons = []
        self.runningToons = []
        self.toonGone = 0
        self.helpfulToons = []

    def calcFaceoffTime(self, centerpos, suitpos):
        facing = Vec3(centerpos - suitpos)
        facing.normalize()
        suitdest = Point3(centerpos - Point3(facing * 6.0))
        dist = Vec3(suitdest - suitpos).length()
        return dist / BattleBase.suitSpeed

    def calcSuitMoveTime(self, pos0, pos1):
        dist = Vec3(pos0 - pos1).length()
        return dist / BattleBase.suitSpeed

    def calcToonMoveTime(self, pos0, pos1):
        dist = Vec3(pos0 - pos1).length()
        return dist / BattleBase.toonSpeed

    def buildJoinPointList(self, avPos, destPos, toon = 0):
        minDist = 999999.0
        nearestP = None
        for p in BattleBase.allPoints:
            dist = Vec3(avPos - p).length()
            if dist < minDist:
                nearestP = p
                minDist = dist

        self.notify.debug('buildJoinPointList() - avp: %s nearp: %s' % (avPos, nearestP))
        dist = Vec3(avPos - destPos).length()
        if dist < minDist:
            self.notify.debug('buildJoinPointList() - destPos is nearest')
            return []
        if toon == 1:
            if nearestP == BattleBase.posE:
                self.notify.debug('buildJoinPointList() - posE')
                plist = [BattleBase.posE]
            elif BattleBase.toonCwise.count(nearestP) == 1:
                self.notify.debug('buildJoinPointList() - clockwise')
                index = BattleBase.toonCwise.index(nearestP)
                plist = BattleBase.toonCwise[index + 1:]
            else:
                self.notify.debug('buildJoinPointList() - counter-clockwise')
                index = BattleBase.toonCCwise.index(nearestP)
                plist = BattleBase.toonCCwise[index + 1:]
        elif nearestP == BattleBase.posA:
            self.notify.debug('buildJoinPointList() - posA')
            plist = [BattleBase.posA]
        elif BattleBase.suitCwise.count(nearestP) == 1:
            self.notify.debug('buildJoinPointList() - clockwise')
            index = BattleBase.suitCwise.index(nearestP)
            plist = BattleBase.suitCwise[index + 1:]
        else:
            self.notify.debug('buildJoinPointList() - counter-clockwise')
            index = BattleBase.suitCCwise.index(nearestP)
            plist = BattleBase.suitCCwise[index + 1:]
        self.notify.debug('buildJoinPointList() - plist: %s' % plist)
        return plist

    def addHelpfulToon(self, toonId):
        if toonId not in self.helpfulToons:
            self.helpfulToons.append(toonId)
