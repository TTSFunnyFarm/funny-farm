from panda3d.core import *
from toontown.toonbase.ToontownBattleGlobals import *

TOON_ID_COL = 0
TOON_TRACK_COL = 1
TOON_LVL_COL = 2
TOON_TGT_COL = 3
TOON_HP_COL = 4
TOON_ACCBONUS_COL = 5
TOON_HPBONUS_COL = 6
TOON_KBBONUS_COL = 7
SUIT_DIED_COL = 8
SUIT_REVIVE_COL = 9
SUIT_ID_COL = 0
SUIT_ATK_COL = 1
SUIT_TGT_COL = 2
SUIT_HP_COL = 3
TOON_DIED_COL = 4
SUIT_BEFORE_TOONS_COL = 5
SUIT_TAUNT_COL = 6
NO_ID = -1
NO_ATTACK = -1
UN_ATTACK = -2
PASS_ATTACK = -3
NO_TRAP = -1
LURE_SUCCEEDED = -1
PASS = 98
SOS = 99
NPCSOS = 97
PETSOS = 96
FIRE = 100
HEAL = HEAL_TRACK
TRAP = TRAP_TRACK
LURE = LURE_TRACK
SOUND = SOUND_TRACK
THROW = THROW_TRACK
SQUIRT = SQUIRT_TRACK
DROP = DROP_TRACK
TOON_ATTACK_TIME = 12.0
SUIT_ATTACK_TIME = 12.0
TOON_TRAP_DELAY = 0.8
TOON_SOUND_DELAY = 1.0
TOON_THROW_DELAY = 0.5
TOON_THROW_SUIT_DELAY = 1.0
TOON_SQUIRT_DELAY = 0.5
TOON_SQUIRT_SUIT_DELAY = 1.0
TOON_DROP_DELAY = 0.8
TOON_DROP_SUIT_DELAY = 1.0
TOON_RUN_T = 3.3
TIMEOUT_PER_USER = 5
TOON_FIRE_DELAY = 0.5
TOON_FIRE_SUIT_DELAY = 1.0
REWARD_TIMEOUT = 120
FLOOR_REWARD_TIMEOUT = 4
BUILDING_REWARD_TIMEOUT = 300
CLIENT_INPUT_TIMEOUT = config.GetFloat('battle-input-timeout', TTLocalizer.BBbattleInputTimeout)

MAX_JOIN_T = TTLocalizer.BBbattleInputTimeout
FACEOFF_TAUNT_T = 3.5
FACEOFF_LOOK_AT_PROP_T = 6
ELEVATOR_T = 4.0
BATTLE_SMALL_VALUE = 1e-07
MAX_EXPECTED_DISTANCE_FROM_BATTLE = 50.0

cogPoints = (((Point3(0, 5, 0), 179),),
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

posA = Point3(0, 10, 0)
posB = Point3(-7.071, 7.071, 0)
posC = Point3(-10, 0, 0)
posD = Point3(-7.071, -7.071, 0)
posE = Point3(0, -10, 0)
posF = Point3(7.071, -7.071, 0)
posG = Point3(10, 0, 0)
posH = Point3(7.071, 7.071, 0)

allPoints = (posA,
 posB,
 posC,
 posD,
 posE,
 posF,
 posG,
 posH)
toonCwise = [posA,
 posB,
 posC,
 posD,
 posE]
toonCCwise = [posH,
 posG,
 posF,
 posE]
suitCwise = [posE,
 posF,
 posG,
 posH,
 posA]
suitCCwise = [posD,
 posC,
 posB,
 posA]

cogSpeed = 4.8
toonSpeed = 8.0
