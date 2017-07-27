from panda3d.core import *
from otp.nametag.NametagGroup import *
from toontown.toonbase import ToontownGlobals
import random
from toontown.hood import ZoneUtil
import ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
import sys, os
import string
QUEST_MOVIE_CLEAR = 0
QUEST_MOVIE_REJECT = 1
QUEST_MOVIE_COMPLETE = 2
QUEST_MOVIE_INCOMPLETE = 3
QUEST_MOVIE_ASSIGN = 4
QUEST_MOVIE_BUSY = 5
QUEST_MOVIE_QUEST_CHOICE = 6
QUEST_MOVIE_QUEST_CHOICE_CANCEL = 7
QUEST_MOVIE_TRACK_CHOICE = 8
QUEST_MOVIE_TRACK_CHOICE_CANCEL = 9
QUEST_MOVIE_TIMEOUT = 10
QUEST_MOVIE_TIER_NOT_DONE = 11
PURCHASE_MOVIE_CLEAR = 0
PURCHASE_MOVIE_START = 1
PURCHASE_MOVIE_START_BROWSE = 9
PURCHASE_MOVIE_START_BROWSE_JBS = 11
PURCHASE_MOVIE_COMPLETE = 2
PURCHASE_MOVIE_NO_MONEY = 3
PURCHASE_MOVIE_TIMEOUT = 8
PURCHASE_MOVIE_START_NOROOM = 10
SELL_MOVIE_CLEAR = 0
SELL_MOVIE_START = 1
SELL_MOVIE_COMPLETE = 2
SELL_MOVIE_NOFISH = 3
SELL_MOVIE_TROPHY = 4
SELL_MOVIE_TIMEOUT = 8
SELL_MOVIE_PETRETURNED = 9
SELL_MOVIE_PETADOPTED = 10
SELL_MOVIE_PETCANCELED = 11
PARTY_MOVIE_CLEAR = 0
PARTY_MOVIE_START = 1
PARTY_MOVIE_COMPLETE = 2
PARTY_MOVIE_ALREADYHOSTING = 3
PARTY_MOVIE_MAYBENEXTTIME = 4
PARTY_MOVIE_ONLYPAID = 5
PARTY_MOVIE_COMINGSOON = 6
PARTY_MOVIE_MINCOST = 7
PARTY_MOVIE_TIMEOUT = 8
BLOCKER_MOVIE_CLEAR = 0
BLOCKER_MOVIE_START = 1
BLOCKER_MOVIE_TIMEOUT = 8
NPC_REGULAR = 0
NPC_CLERK = 1
NPC_TAILOR = 2
NPC_HQ = 3
NPC_BLOCKER = 4
NPC_FISHERMAN = 5
NPC_PETCLERK = 6
NPC_KARTCLERK = 7
NPC_PARTYPERSON = 8
NPC_SPECIALQUESTGIVER = 9
NPC_FLIPPY = 10
NPC_SCIENTIST = 11
NPC_SNOWBALLGIVER = 12
CLERK_COUNTDOWN_TIME = 120
TAILOR_COUNTDOWN_TIME = 300
RTDNAFile = '/RTDNAFile.txt'
saveDNA = False

def getRandomDNA(seed, gender):
    randomDNA = ToonDNA.ToonDNA()
    randomDNA.newToonRandom(seed, gender, 1)
    return randomDNA.asTuple()

def createNpcsInZone(zoneId):
    npcs = []
    canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)
    npcIdList = zone2NpcDict.get(canonicalZoneId, [])
    for i in xrange(len(npcIdList)):
        npcId = npcIdList[i]
        npcs.append(createLocalNPC(npcId, True))

    return npcs

def createLocalNPC(npcId, functional = False):
    import Toon
    import NPCToon
    import NPCClerk
    import NPCScientist
    import NPCFlippy
    if npcId not in NPCToonDict:
        return None
    desc = NPCToonDict[npcId]
    canonicalZoneId, name, dnaType, gender, accessories, protected, type = desc
    if not functional:
        npc = Toon.Toon()
        # if type == NPC_FLIPPY:
            # npc.setScale(1.25) # TODO: Reposition tutorial camera and elements to account for this
    elif type == NPC_CLERK:
        npc = NPCClerk.NPCClerk()
    elif type == NPC_SCIENTIST:
        npc = NPCScientist.NPCScientist()
    elif type == NPC_FLIPPY:
        npc = NPCFlippy.NPCFlippy()
    elif type == NPC_HQ:
        npc = NPCToon.NPCToon(hq=1)
    else:
        npc = NPCToon.NPCToon()
    npc.setName(name)
    npc.setPickable(0)
    npc.setPlayerType(NametagGroup.CCNonPlayer)
    npc.npcId = npcId
    dna = ToonDNA.ToonDNA()
    if dnaType == 'r':
        dnaList = getRandomDNA(npcId, gender)
    else:
        dnaList = dnaType
    dna.newToonFromProperties(*dnaList)
    npc.setDNAString(dna.makeNetString())
    if len(accessories) > 0:
        npc.setHat(*accessories[0])
        npc.setGlasses(*accessories[1])
        npc.setBackpack(*accessories[2])
        npc.setShoes(*accessories[3])
    npc.nametag.setFont(ToontownGlobals.getSignFont())
    npc.animFSM.request('neutral')
    return npc


def isZoneProtected(zoneId):
    npcs = []
    npcIdList = zone2NpcDict.get(zoneId, [])
    for npcId in npcIdList:
        npcDesc = NPCToonDict.get(npcId)
        if npcDesc[4]:
            return 1

    return 0


lnames = TTLocalizer.NPCToonNames
NPCToonDict = {
 1001: (1514,
        lnames[2001],
        ('dss',
        'ms',
        'm',
        'm',
        17,
        0,
        17,
        17,
        3,
        3,
        3,
        3,
        7,
        2),
        'm',
        [],
        1,
        NPC_FLIPPY),
 1002: (1510,
        lnames[2006],
        ('dsl',
         'ls',
         'l',
         'm',
         18,
         0,
         18,
         18,
         1,
         4,
         1,
         4,
         1,
         2),
        'm',
        [],
        1,
        NPC_CLERK),
 1003: (1510,
        lnames[2011],
        ('rll',
         'ms',
         'l',
         'f',
         2,
         0,
         2,
         2,
         1,
         9,
         1,
         9,
         23,
         27),
        'f',
        [],
        1,
        NPC_CLERK),
 1004: (1511,
        lnames[2013],
        ('rls',
         'ms',
         'l',
         'm',
         9,
         0,
         9,
         9,
         0,
         7,
         0,
         7,
         1,
         19),
        'm',
        [],
        1,
        NPC_PETCLERK),
 1005: (1511,
        lnames[2014],
        ('mls',
         'ms',
         'm',
         'f',
         2,
         0,
         2,
         2,
         0,
         12,
         0,
         12,
         1,
         0),
        'f',
        [],
        1,
        NPC_PETCLERK),
 1006: (1511,
        lnames[2015],
        ('hsl',
         'ls',
         'm',
         'm',
         17,
         0,
         17,
         17,
         0,
         8,
         0,
         8,
         1,
         13),
        'm',
        [],
        1,
        NPC_PETCLERK),
 1007: (1512,
        lnames[2007],
        ('dss',
         'ms',
         'l',
         'm',
         10,
         0,
         10,
         10,
         1,
         5,
         1,
         5,
         1,
         20),
        'm',
        [],
        1,
        NPC_HQ),
 1008: (1512,
        lnames[2008],
        ('fll',
         'ss',
         'l',
         'm',
         3,
         0,
         3,
         3,
         1,
         5,
         1,
         5,
         1,
         17),
        'm',
        [],
        1,
        NPC_HQ),
 1009: (1512,
        lnames[2009],
        ('fsl',
         'md',
         'l',
         'f',
         18,
         0,
         18,
         18,
         1,
         8,
         1,
         8,
         11,
         27),
        'f',
        [],
        1,
        NPC_HQ),
 1010: (1512,
        lnames[2010],
        ('fls',
         'ls',
         'l',
         'f',
         11,
         0,
         11,
         11,
         1,
         8,
         1,
         8,
         8,
         4),
        'f',
        [],
        1,
        NPC_HQ),
 1012: (1000,
        lnames[2012],
        ('rss',
         'ls',
         'l',
         'm',
         17,
         0,
         17,
         17,
         1,
         6,
         1,
         6,
         1,
         1),
        'm',
        [],
        1,
        NPC_FISHERMAN),
 1013: (1515,
        lnames[2019],
        ('fll',
         'ss',
         's',
         'm',
         15,
         0,
         15,
         15,
         99,
         27,
         86,
         27,
         39,
         27),
        'm',
        [],
        1,
        NPC_SCIENTIST),
 1014: (1515,
        lnames[2018],
        ('pls',
         'ls',
         'l',
         'm',
         9,
         0,
         9,
         9,
         98,
         27,
         86,
         27,
         38,
         27),
        'm',
        [],
        1,
        NPC_SCIENTIST),
 1015: (1515,
        lnames[2020],
        ('hss',
         'ms',
         'm',
         'm',
         20,
         0,
         20,
         20,
         97,
         27,
         86,
         27,
         37,
         27),
        'm',
        [],
        1,
        NPC_SCIENTIST),
 1101: (1610,
        lnames[2104],
        ('mls',
         'ms',
         'm',
         'm',
         15,
         0,
         15,
         15,
         1,
         10,
         1,
         10,
         0,
         16),
        'm',
        [],
        1,
        NPC_HQ),
 1102: (1610,
        lnames[2105],
        ('hsl',
         'ss',
         'm',
         'm',
         7,
         0,
         7,
         7,
         1,
         10,
         1,
         10,
         0,
         13),
        'm',
        [],
        1,
        NPC_HQ),
 1103: (1610,
        lnames[2106],
        ('hss',
         'ld',
         'm',
         'f',
         23,
         0,
         23,
         23,
         1,
         23,
         1,
         23,
         24,
         27),
        'f',
        [],
        1,
        NPC_HQ),
 1104: (1610,
        lnames[2107],
        ('cll',
         'sd',
         'm',
         'f',
         14,
         0,
         14,
         14,
         1,
         24,
         1,
         24,
         7,
         4),
        'f',
        [],
        1,
        NPC_HQ),
 1105: (1611,
        lnames[1105],
        ('rss',
         'md',
         's',
         'f',
         17,
         0,
         17,
         17,
         5,
         24,
         5,
         24,
         7,
         2),
        'f',
        [],
        1,
        NPC_REGULAR),
 6001: (-1,
        lnames[6001],
        ('bss',
         'ss',
         's',
         'm',
         20,
         0,
         20,
         20,
         4,
         2,
         4,
         2,
         7,
         14),
        'm',
        [],
        1,
        NPC_REGULAR),
}

del lnames
BlockerPositions = {TTLocalizer.Flippy: (Point3(207.4, 18.81, -0.475), 90.0)}
zone2NpcDict = {}

def generateZone2NpcDict():
    for id, npcDesc in NPCToonDict.items():
        zoneId = npcDesc[0]
        if zoneId in zone2NpcDict:
            zone2NpcDict[zoneId].append(id)
        else:
            zone2NpcDict[zoneId] = [id]


def getNPCName(npcId):
    npc = NPCToonDict.get(npcId)
    if npc:
        return npc[1]
    else:
        return None
    return None


def getNPCZone(npcId):
    npc = NPCToonDict.get(npcId)
    if npc:
        return npc[0]
    else:
        return None
    return None


def getBuildingArticle(zoneId):
    return TTLocalizer.zone2TitleDict.get(zoneId, 'Toon Building')


def getBuildingTitle(zoneId):
    return TTLocalizer.zone2TitleDict.get(zoneId, 'Toon Building')

# Regular NPC SOS Toons (The good ones)
HQnpcFriends = {
2001: (ToontownBattleGlobals.HEAL_TRACK, 5, ToontownGlobals.MaxHpLimit, 5),
2132: (ToontownBattleGlobals.HEAL_TRACK, 5, 70, 4),
2121: (ToontownBattleGlobals.HEAL_TRACK, 5, 45, 3),
2011: (ToontownBattleGlobals.TRAP_TRACK, 4, 180, 5),
3007: (ToontownBattleGlobals.TRAP_TRACK, 4, 70, 4),
1001: (ToontownBattleGlobals.TRAP_TRACK, 4, 50, 3),
3112: (ToontownBattleGlobals.LURE_TRACK, 5, 0, 5),
1323: (ToontownBattleGlobals.LURE_TRACK, 5, 0, 3),
2308: (ToontownBattleGlobals.LURE_TRACK, 5, 0, 3),
4119: (ToontownBattleGlobals.SOUND_TRACK, 5, 80, 5),
4219: (ToontownBattleGlobals.SOUND_TRACK, 5, 50, 4),
4115: (ToontownBattleGlobals.SOUND_TRACK, 5, 40, 3),
1116: (ToontownBattleGlobals.DROP_TRACK, 5, 170, 5),
2311: (ToontownBattleGlobals.DROP_TRACK, 5, 100, 4),
4140: (ToontownBattleGlobals.DROP_TRACK, 5, 60, 3),
3137: (ToontownBattleGlobals.NPC_COGS_MISS, 0, 0, 4),
4327: (ToontownBattleGlobals.NPC_COGS_MISS, 0, 0, 4),
4230: (ToontownBattleGlobals.NPC_COGS_MISS, 0, 0, 4),
3135: (ToontownBattleGlobals.NPC_TOONS_HIT, 0, 0, 4),
2208: (ToontownBattleGlobals.NPC_TOONS_HIT, 0, 0, 4),
5124: (ToontownBattleGlobals.NPC_TOONS_HIT, 0, 0, 4),
2003: (ToontownBattleGlobals.NPC_RESTOCK_GAGS, -1, 0, 5),
2126: (ToontownBattleGlobals.NPC_RESTOCK_GAGS, ToontownBattleGlobals.HEAL_TRACK, 0, 3),
4007: (ToontownBattleGlobals.NPC_RESTOCK_GAGS, ToontownBattleGlobals.TRAP_TRACK, 0, 3),
1315: (ToontownBattleGlobals.NPC_RESTOCK_GAGS, ToontownBattleGlobals.LURE_TRACK, 0, 3),
5207: (ToontownBattleGlobals.NPC_RESTOCK_GAGS, ToontownBattleGlobals.SQUIRT_TRACK, 0, 3),
3129: (ToontownBattleGlobals.NPC_RESTOCK_GAGS, ToontownBattleGlobals.THROW_TRACK, 0, 3),
4125: (ToontownBattleGlobals.NPC_RESTOCK_GAGS, ToontownBattleGlobals.SOUND_TRACK, 0, 3),
1329: (ToontownBattleGlobals.NPC_RESTOCK_GAGS, ToontownBattleGlobals.DROP_TRACK, 0, 3)
}

# Field Office NPC Toons (The rubbish ones)
FOnpcFriends = {
9310: (ToontownBattleGlobals.LURE_TRACK, 1, 0, 0),
9311: (ToontownBattleGlobals.LURE_TRACK, 1, 0, 1),
9312: (ToontownBattleGlobals.LURE_TRACK, 3, 0, 2),
9307: (ToontownBattleGlobals.SOUND_TRACK, 1, 10, 0),
9308: (ToontownBattleGlobals.SOUND_TRACK, 3, 20, 1),
9309: (ToontownBattleGlobals.SOUND_TRACK, 4, 30, 2),
9304: (ToontownBattleGlobals.DROP_TRACK, 1, 20, 0),
9305: (ToontownBattleGlobals.DROP_TRACK, 2, 35, 1),
9306: (ToontownBattleGlobals.DROP_TRACK, 3, 50, 2),
9301: (ToontownBattleGlobals.HEAL_TRACK, 3, 10, 0),
9302: (ToontownBattleGlobals.HEAL_TRACK, 3, 20, 1),
9303: (ToontownBattleGlobals.HEAL_TRACK, 3, 30, 2)
}

npcFriends = dict(HQnpcFriends)
npcFriends.update(FOnpcFriends)

def getNPCName(npcId):
    if npcId in NPCToonDict:
        return NPCToonDict[npcId][1]
    return None


def npcFriendsMinMaxStars(minStars, maxStars):
    return [ id for id in npcFriends.keys() if getNPCTrackLevelHpRarity(id)[3] >= minStars and getNPCTrackLevelHpRarity(id)[3] <= maxStars ]


def getNPCTrack(npcId):
    if npcId in npcFriends:
        return npcFriends[npcId][0]
    return None


def getNPCTrackHp(npcId):
    if npcId in npcFriends:
        track, level, hp, rarity = npcFriends[npcId]
        return (track, hp)
    return (None, None)


def getNPCTrackLevelHp(npcId):
    if npcId in npcFriends:
        track, level, hp, rarity = npcFriends[npcId]
        return (track, level, hp)
    return (None, None, None)


def getNPCTrackLevelHpRarity(npcId):
    if npcId in npcFriends:
        return npcFriends[npcId]
    return (None, None, None, None)
