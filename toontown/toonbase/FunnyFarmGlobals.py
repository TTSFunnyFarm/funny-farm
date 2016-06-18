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
FFHoodText = 'Funny Farm\nPlayground'
RRStreetText = 'Funny Farm\nRickety Road'
FCHoodText = 'Funny Farm Central'
SSHoodText = 'Silly Springs\nPlayground'
CVHoodText = 'Chilly Village\nPlayground'
WWStreetText = 'Chilly Village\nWintry Way'
MMHoodText = 'Moonlit Meadow\nPlayground'
BBStreetText = 'Moonlit Meadow\nBreezy Bend'
SecretAreaText = '???'
HoodHierarchy = {
    FunnyFarm: (RicketyRoad),
    FunnyFarmCentral: (SecretArea),
    SillySprings: (UnknownStreet),
    ChillyVillage: (WintryWay),
    MoonlitMeadow: (BreezyBend)
}

def getHoodNameFromId(zoneId):
    if zoneId == FunnyFarm:
        return ('Funny Farm', 'Playground')
    elif zoneId == FunnyFarmCentral:
        return ('Funny Farm Central', '')
    elif zoneId == SillySprings:
        return ('Silly Springs', 'Playground')
    elif zoneId == ChillyVillage:
        return ('Chilly Village', 'Playground')
    elif zoneId == MoonlitMeadow:
        return ('Moonlit Meadow', 'Playground')
    elif zoneId == RicketyRoad:
        return ('Funny Farm', 'Rickety Road')
    elif zoneId == WintryWay:
        return ('Chilly Village', 'Wintry Way')
    elif zoneId == BreezyBend:
        return ('Moonlit Meadow', 'Breezy Bend')
    elif zoneId == SecretArea:
        return ('???', '')

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
ToonUpIncrements = {
    xrange(20, 40): 1,
    xrange(40, 60): 2,
    xrange(60, 80): 3,
    xrange(80, 100): 4,
    xrange(100, 120): 5
}

def addCullBins():
    cbm = CullBinManager.getGlobalPtr()
    cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
    cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)

def setNametagGlobals():
    base.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
    base.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
    base.mouseWatcherNode.setButtonDownPattern('button-down-%r')
    base.mouseWatcherNode.setButtonUpPattern('button-up-%r')

    base.wantNametags = True
    arrow = loader.loadModel('phase_3/models/props/arrow')
    card = loader.loadModel('phase_3/models/props/panel')
    speech3d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox'))
    thought3d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox_thought_cutout'))
    speech2d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox_noarrow'))
    chatButtonGui = loader.loadModel('phase_3/models/gui/chat_button_gui')
    NametagGlobals.setCamera(base.cam)
    NametagGlobals.setArrowModel(arrow)
    NametagGlobals.setNametagCard(card, VBase4(-0.5, 0.5, -0.5, 0.5))
    NametagGlobals.setMouseWatcher(base.mouseWatcherNode)
    NametagGlobals.setSpeechBalloon3d(speech3d)
    NametagGlobals.setThoughtBalloon3d(thought3d)
    NametagGlobals.setSpeechBalloon2d(speech2d)
    NametagGlobals.setThoughtBalloon2d(thought3d)
    NametagGlobals.setPageButton(PGButton.SReady, chatButtonGui.find('**/Horiz_Arrow_UP'))
    NametagGlobals.setPageButton(PGButton.SDepressed, chatButtonGui.find('**/Horiz_Arrow_DN'))
    NametagGlobals.setPageButton(PGButton.SRollover, chatButtonGui.find('**/Horiz_Arrow_Rllvr'))
    NametagGlobals.setQuitButton(PGButton.SReady, chatButtonGui.find('**/CloseBtn_UP'))
    NametagGlobals.setQuitButton(PGButton.SDepressed, chatButtonGui.find('**/CloseBtn_DN'))
    NametagGlobals.setQuitButton(PGButton.SRollover, chatButtonGui.find('**/CloseBtn_Rllvr'))
    rolloverSound = DirectGuiGlobals.getDefaultRolloverSound()
    if rolloverSound:
        NametagGlobals.setRolloverSound(rolloverSound)
    clickSound = DirectGuiGlobals.getDefaultClickSound()
    if clickSound:
        NametagGlobals.setClickSound(clickSound)
    NametagGlobals.setToon(base.cam)

    # For whitelist filtering:
    tpSlant = TextProperties()
    tpSlant.setSlant(0.3)
    tpMgr = TextPropertiesManager.getGlobalPtr()
    tpMgr.setProperties('slant', tpSlant)

    base.marginManager = MarginManager()
    base.margins = aspect2d.attachNewNode(base.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
    mm = base.marginManager

    # TODO: Dynamicaly add more and reposition cells
    padding = 0.0225

    # Order: Top to bottom
    base.leftCells = [
        mm.addGridCell(0.2 + padding, -0.45, base.a2dTopLeft), # Above boarding groups
        mm.addGridCell(0.2 + padding, -0.9, base.a2dTopLeft),  # 1
        mm.addGridCell(0.2 + padding, -1.35, base.a2dTopLeft)  # Below Boarding Groups
    ]

    # Order: Left to right
    base.bottomCells = [
        mm.addGridCell(-0.87, 0.2 + padding, base.a2dBottomCenter), # To the right of the laff meter
        mm.addGridCell(-0.43, 0.2 + padding, base.a2dBottomCenter), # 1
        mm.addGridCell(0.01, 0.2 + padding, base.a2dBottomCenter),  # 2
        mm.addGridCell(0.45, 0.2 + padding, base.a2dBottomCenter),  # 3
        mm.addGridCell(0.89, 0.2 + padding, base.a2dBottomCenter)   # To the left of the shtiker book
    ]

    # Order: Bottom to top
    base.rightCells = [
        mm.addGridCell(-0.2 - padding, -1.35, base.a2dTopRight), # Above the street map
        mm.addGridCell(-0.2 - padding, -0.9, base.a2dTopRight),  # Below the friends list
        mm.addGridCell(-0.2 - padding, -0.45, base.a2dTopRight)  # Behind the friends list
    ]
