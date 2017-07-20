from panda3d.core import *
from toontown.toon import Toon
from direct.gui import DirectGuiGlobals
from otp.margins.MarginManager import MarginManager
from otp.nametag import NametagGlobals
from otp.nametag.ChatBalloon import ChatBalloon
import TTLocalizer
from ToontownGlobals import *

def getVar(var):
    return globals()[var]

Tutorial = 500
FunnyFarm = 1000
SillySprings = 2000
ChillyVillage = 3000
MoonlitMeadow = 4000
RicketyRoad = 1100
BarnyardBoulevard = 1200
TulipTerrace = 2100
PetalPathway = 2200
WintryWay = 3100
BreezyBend = 4100
Estate = 5000 # Should be fine as one zone considering this is singleplayer
HoodHierarchy = {
    FunnyFarm: (RicketyRoad,),
    SillySprings: (TulipTerrace,),
    ChillyVillage: (WintryWay,),
    MoonlitMeadow: (BreezyBend,),
    Estate: (),
}
hoodNameMap = {
    Tutorial: TTLocalizer.Tutorial,
    FunnyFarm: TTLocalizer.lFunnyFarm,
    SillySprings: TTLocalizer.lSillySprings,
    ChillyVillage: TTLocalizer.lChillyVillage,
    MoonlitMeadow: TTLocalizer.lMoonlitMeadow,
    Estate: TTLocalizer.lEstate,
}
StreetNames = { # TODO: split out into localizer...
    FunnyFarm: 'Playground',
    RicketyRoad: 'Rickety Road',
    BarnyardBoulevard: 'Barnyard Boulevard',
    SillySprings: 'Playground',
    TulipTerrace: 'Tulip Terrace',
    PetalPathway: 'Petal Pathway',
    ChillyVillage: 'Playground',
    WintryWay: 'Wintry Way',
    MoonlitMeadow: 'Playground',
    BreezyBend: 'Breezy Bend',
    Estate: '' # Hood title will take care of it...
}
HoodName2Id = {
    'ff': FunnyFarm,
    'ss': SillySprings,
    'cv': ChillyVillage,
    'mm': MoonlitMeadow,
    'e': Estate
}
HoodId2Name = {
    FunnyFarm: 'ff',
    SillySprings: 'ss',
    ChillyVillage: 'cv',
    MoonlitMeadow: 'mm',
    Estate: 'e'
}

def getIdFromName(hoodName):
    id = HoodName2Id.get(hoodName)
    if id:
        return id
    return None

def getNameFromId(hoodId):
    name = HoodId2Name.get(hoodId)
    if name:
        return name
    return None

def getHoodId(zoneId):
    for zones in HoodHierarchy.values():
        if zoneId in zones:
            return HoodHierarchy.keys()[HoodHierarchy.values().index(zones)]
    return zoneId

phaseMap = {
    FunnyFarm: 'phase_14/models/neighborhoods/funny_farm',
    SillySprings: 'phase_14/models/neighborhoods/silly_springs',
    RicketyRoad: 'phase_14/models/streets/funny_farm_1100',
    Estate: 'phase_14/models/neighborhoods/estate_1'
}
safeZoneCountMap = {
    FunnyFarm: 6,
    SillySprings: 6,
    Estate: 6,
}
townCountMap = {
    Tutorial: 40,
    FunnyFarm: 40,
    SillySprings: 40
}
SpawnPoints = {
    FunnyFarm: [
        (Point3(0, -140, 0), Vec3(0, 0, 0)),
        (Point3(-40, -90, 0), Vec3(315, 0, 0)),
        (Point3(40, -90, 0), Vec3(45, 0, 0)),
        (Point3(60, -20, 0), Vec3(90, 0, 0)),
        (Point3(-60, -20, 0), Vec3(270, 0, 0)),
        (Point3(-50, 45, 0), Vec3(225, 0, 0)),
        (Point3(5, 60, 0), Vec3(180, 0, 0)),
        (Point3(60, 35, 0), Vec3(135, 0, 0))
    ]
}
nametagFonts = []
for font in TTLocalizer.NametagFonts:
    nametagFonts.append(loader.loadFont(font))
Default = getInterfaceFont()
Mickey = getSignFont()
Simple = nametagFonts[0]
Shivering = nametagFonts[1]
Wonky = nametagFonts[2]
Fancy = nametagFonts[3]
Silly = nametagFonts[4]
Zany = nametagFonts[5]
Practical = nametagFonts[6]
Nautical = nametagFonts[7]
Whimsical = nametagFonts[8]
Spooky = nametagFonts[9]
Action = nametagFonts[10]
Poetic = nametagFonts[11]
Boardwalk = nametagFonts[12]
Western = nametagFonts[13]
nametagDict = {
    Default: 'Default',
    Mickey: 'Mickey',
    Simple: 'Simple',
    Shivering: 'Shivering',
    Wonky: 'Wonky',
    Fancy: 'Fancy',
    Silly: 'Silly',
    Zany: 'Zany',
    Practical: 'Practical',
    Nautical: 'Nautical',
    Whimsical: 'Whimsical',
    Spooky: 'Spooky',
    Action: 'Action',
    Poetic: 'Poetic',
    Boardwalk: 'Boardwalk',
    Western: 'Western'
}
PetShopFish = [
    'BearAcuda',
    'devilRay',
    'holeyMackerel',
    'nurseShark',
    'pianoTuna',
    'poolShark',
    'seaHorse'
]
PetShopFishPositions = [
    Point3(0, 35, 3),
    Point3(8, 24, 5),
    Point3(-8, 27.5, 9),
    Point3(0, 22, 3.5),
    Point3(-7, 25, 4),
    Point3(-16, 16, 3),
    Point3(17, 17, 3)
]
PetShopFishRotations = [
    Vec3(90, 0, 0),
    Vec3(315, 0, 0),
    Vec3(0, 0, 0),
    Vec3(270, 0, 0),
    Vec3(20, 0, 0),
    Vec3(45, 0, 0),
    Vec3(315, 0, 0)
]
PetShopFishScales = [ # pun intended
    Vec3(1.0, 1.0, 1.0),
    Vec3(1.0, 1.0, 1.0),
    Vec3(3.0, 3.0, 3.0),
    Vec3(1.0, 1.0, 1.0),
    Vec3(1.0, 1.0, 1.0),
    Vec3(1.0, 1.0, 1.0),
    Vec3(1.0, 1.0, 1.0)
]
PetShopBearSwimPoints = [
    Point3(5, 30, 3),
    Point3(0, 25, 3),
    Point3(-5, 30, 3),
    Point3(0, 35, 3)
]
ToonLevelCap = 10
LevelExperience = [
    # FF
    50,
    100,
    200,
    300,
    450,
    600,
    800,
    1000,
    1250,
    1500,
    # SS
    1800,
    2100,
    2450,
    2800,
    3200,
    3600,
    4050,
    4500,
    5000,
    5500,
    # CV
    6050,
    6600,
    7200,
    7800,
    8450,
    9100,
    9800,
    10500,
    11250,
    12000,
    # MM
    12800,
    13600,
    14450,
    15300,
    16200,
    17100,
    18050,
    19000,
    20000,
    21000
]
MaxAvatars = 6
