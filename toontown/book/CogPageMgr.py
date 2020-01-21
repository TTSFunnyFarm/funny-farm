from toontown.suit.SuitDNA import suitHeadTypes
from toontown.book.CogPageGlobals import *

class CogPageMgr:
    def toonEncounteredCogs(self, encounteredCogs):
        cogs = base.localAvatar.getCogStatus()
        for cog in encounteredCogs:
            cogIndex = suitHeadTypes.index(cog['type'])
            if toon.getDoId() in cog['activeToons']:
                if cogs[cogIndex] == COG_UNSEEN: # We haven't seen this cog yet!
                    cogs[cogIndex] = COG_BATTLED # Set it to battled!

        toon.setCogStatus(cogs)

    def toonKilledCogs(self, killedCogs):
        toon = base.localAvatar
        cogCounts = toon.getCogCounts()
        eliteCounts = toon.getEliteCounts()
        skeleCounts = toon.getSkeleCounts()
        cogs = toon.getCogStatus()
        for cog in killedCogs:
            cogIndex = suitHeadTypes.index(cog['type'])
            if cog['isSkelecog']:
                skeleCounts[cogIndex] += 1
            elif cog['isElite']:
                eliteCounts[cogIndex] += 1
            else:
                cogCounts[cogIndex] += 1
            if cogs[cogIndex] == COG_BATTLED: # We haven't defeated this cog yet!
                cogs[cogIndex] = COG_DEFEATED
        toon.setCogStatus(cogs)
        toon.setCogCounts(cogCounts)
        toon.setEliteCounts(eliteCounts)
        toon.setSkeleCounts(skeleCounts)
