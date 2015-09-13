from direct.showbase import RandomNumGen
from toontown.toonbase import ToontownGlobals

IconMap = {
    ToontownGlobals.ToontownCentral: ['phase_3.5/models/props/mickeySZ', 'mickeySZ'],
    ToontownGlobals.DaisyGardens: ['phase_4/models/props/daisySZ', 'daisySZ'],
    ToontownGlobals.TheBrrrgh: ['phase_4/models/props/plutoSZ', 'plutoSZ'],
    ToontownGlobals.DonaldsDreamland: ['phase_4/models/props/donald_DL_SZ', 'donald_DL_SZ']
}

def getMazeName(gameDoId, numPlayers, mazeNames):
    try:
        return forcedMaze
    except:
        names = mazeNames[numPlayers - 1]
        return names[RandomNumGen.randHash(gameDoId) % len(names)]


ENDLESS_GAME = config.GetBool('endless-maze-game', 0)
GAME_DURATION = 60.0
SHOWSCORES_DURATION = 2.0
SUIT_TIC_FREQ = int(256)
WALK_SAME_DIRECTION_PROB = 4
WALK_TURN_AROUND_PROB = 30
SUIT_START_POSITIONS = ((0.25, 0.25),
 (0.75, 0.75),
 (0.25, 0.75),
 (0.75, 0.25),
 (0.2, 0.5),
 (0.8, 0.5),
 (0.5, 0.2),
 (0.5, 0.8),
 (0.33, 0.0),
 (0.66, 0.0),
 (0.33, 1.0),
 (0.66, 1.0),
 (0.0, 0.33),
 (0.0, 0.66),
 (1.0, 0.33),
 (1.0, 0.66))
