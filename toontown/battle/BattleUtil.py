def toonFaceCog(toon, cog):
    cog.headsUp(toon)
    toon.stopLookAround()
    toon.headsUp(cog)


def calcSuitMoveTime(self, pos0, pos1):
    dist = Vec3(pos0 - pos1).length()
    return dist / BattleBase.suitSpeed

def calcToonMoveTime(self, pos0, pos1):
    dist = Vec3(pos0 - pos1).length()
    return dist / BattleBase.toonSpeed
