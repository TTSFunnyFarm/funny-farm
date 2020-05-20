from panda3d.core import *
from toontown.battle.BattleGlobals import *

def toonFaceCog(toon, cog):
    cog.headsUp(toon)
    toon.stopLookAround()
    toon.headsUp(cog)

def calcSuitMoveTime(pos0, pos1):
    dist = Vec3(pos0 - pos1).length()
    return dist / cogSpeed

def calcToonMoveTime(pos0, pos1):
    dist = Vec3(pos0 - pos1).length()
    return dist / toonSpeed
