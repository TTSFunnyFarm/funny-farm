from pandac.PandaModules import *
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
FunnyFarmCentral = 2000
SillySprings = 3000
ChillyVillage = 4000
MoonlitMeadow = 5000
RicketyRoad = 1100
SecretArea = 2100
UnknownStreet = 3100
WintryWay = 4100
BreezyBend = 5100
lTutorial = 'The Toon-torial'
lFunnyFarm = 'Funny Farm'
lFunnyFarmCentral = 'Funny Farm Central'
lSillySprings = 'Silly Springs'
lChillyVillage = 'Chilly Village'
lMoonlitMeadow = 'Moonlit Meadow'
lRicketyRoad = 'Rickety Road'
lSecretArea = '???'
lWintryWay = 'Wintry Way'
lBreezyBend = 'Breezy Bend'
lPlayground = 'Playground'
FFHoodText = lFunnyFarm + '\n' + lPlayground
FCHoodText = lFunnyFarmCentral
SSHoodText = lSillySprings + '\n' + lPlayground
CVHoodText = lChillyVillage + '\n' + lPlayground
MMHoodText = lMoonlitMeadow + '\n' + lPlayground
RRStreetText = lFunnyFarm + '\n' + lRicketyRoad
SecretAreaText = lSecretArea
WWStreetText = lChillyVillage + '\n' + lWintryWay
BBStreetText = lMoonlitMeadow + '\n' + lBreezyBend
HoodHierarchy = {
    FunnyFarm: [RicketyRoad],
    FunnyFarmCentral: [SecretArea],
    SillySprings: [UnknownStreet],
    ChillyVillage: [WintryWay],
    MoonlitMeadow: [BreezyBend]
}
HoodNameDict = {
    Tutorial: lTutorial,
    FunnyFarm: lFunnyFarm,
    FunnyFarmCentral: lFunnyFarmCentral,
    SillySprings: lSillySprings,
    ChillyVillage: lChillyVillage,
    MoonlitMeadow: lMoonlitMeadow,
    RicketyRoad: lRicketyRoad,
    SecretArea: lSecretArea,
    WintryWay: lWintryWay,
    BreezyBend: lBreezyBend
}
HoodTextDict = {
    FunnyFarm: FFHoodText,
    FunnyFarmCentral: FCHoodText,
    SillySprings: SSHoodText,
    ChillyVillage: CVHoodText,
    MoonlitMeadow: MMHoodText,
    RicketyRoad: RRStreetText,
    SecretArea: SecretAreaText,
    WintryWay: WWStreetText,
    BreezyBend: BBStreetText
}

def getHoodId(zoneId):
    for zones in HoodHierarchy.values():
        if zoneId in zones:
            return HoodHierarchy.keys()[HoodHierarchy.values().index(zones)]
    return zoneId

phaseMap = {
    FunnyFarm: 'phase_14/models/neighborhoods/funny_farm',
    FunnyFarmCentral: 'phase_14/models/neighborhoods/funny_farm_central',
    SillySprings: 'phase_14/models/neighborhoods/silly_springs',
    RicketyRoad: 'phase_14/models/streets/rickety_road',
    WintryWay: 'phase_14/models/streets/wintry_way'
}
SpawnPoints = {
    FunnyFarm: [
        (Point3(-70, 0, 0), Vec3(270, 0, 0)),
        (Point3(70, 0, 0), Vec3(90, 0, 0)),
        (Point3(0, -60, 0), Vec3(0, 0, 0)),
        (Point3(0, 60, 0), Vec3(180, 0, 0)),
        (Point3(-65, 60, 0), Vec3(225, 0, 0))
    ],
    FunnyFarmCentral: [
        (Point3(0, 0, 0), Vec3(0, 0, 0)),
        (Point3(60, -50, 0), Vec3(45, 0, 0)),
        (Point3(-60, -50, 0), Vec3(315, 0, 0)),
        (Point3(-55, 55, 0), Vec3(225, 0, 0)),
        (Point3(55, 55, 0), Vec3(135, 0, 0))
    ],
    SillySprings: [
        (Point3(0, -35, 0), Vec3(0, 0, 0)),
        (Point3(-50, -5, 0), Vec3(300, 0, 0)),
        (Point3(23, 30, 0), Vec3(180, 0, 0)),
        (Point3(-23, 30, 0), Vec3(180, 0, 0)),
        (Point3(50, -10, 0), Vec3(90, 0, 0))
    ],
    SecretArea: [
        (Point3(0, -20, 0), Vec3(0, 0, 0))
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
# Maximum experience for each Toon level; we're only defining the first 10
# because level 10 will be the cap in 1.4.0.
LevelExperience = [
    50,
    100,
    200,
    350,
    500,
    700,
    900,
    1150,
    1400,
    1700
]
