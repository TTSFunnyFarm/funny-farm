from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from toontown.toon import NPCToons
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.hood import ToonHood
from otp.nametag.NametagConstants import *
from toontown.tutorial.CogPinata import CogPinata
from toontown.hood import SkyUtil

TutorialGreeting = 'Hello! Use the arrow keys to come over here.'
TutorialIntro = [
    'Welcome to Funny Farm.',
    'Many many years ago, Toontown was invaded by evil business robots called Cogs.',
    'The Cogs despise all silliness, and they can\'t take a joke!',
    'For 10 long years the toons fought Cogs with silly jokes and gags...',
    '...until one day, they became too strong for us.',
    'The Cogs introduced a new level of power: Elite Cogs.',
    'We were no match for the Elites, and they took over Toontown completely!',
    'Since then, we\'ve rebuilt our town on the grounds of Funny Farm, a faraway land that we abandoned long ago.',
    'And it\'s only a matter of time before the Cogs find us again.',
    'But that\'s enough talk. Let\'s get you some gags.'
]
TutorialGags = [
    'Throw and Squirt are the two most basic gag tracks, so I\'ll give you these to start.',
    'As you progress, you will gain lots of new gags, including special sugary drinks to boost your stats!'
]
TutorialLaffMeter = [
    'Oh! You also need a Laff meter!',
    'If your Laff meter gets too low, you\'ll be sad!',
    'A happy Toon is a healthy Toon!'
]

class Tutorial(ToonHood.ToonHood):
    notify = directNotify.newCategory('Tutorial')
    notify.setInfo(True)

    def __init__(self):
        ToonHood.ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.Tutorial
        self.hoodFile = 'phase_14/models/streets/tutorial_street'
        self.spookyHoodFile = self.hoodFile
        self.winterHoodFile = self.hoodFile
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.toon = base.localAvatar

    def enter(self, tunnel=None, init=0):
        musicMgr.startTutorial()
        Sequence(Wait(0.3), Func(self.toon.enterTeleportIn, 1, 0, self.__handleEntered)).start()

    def exit(self):
        musicMgr.stopTutorial()
        self.ignoreAll()

    def __handleEntered(self):
        self.toon.exitTeleportIn()
        self.enableToon()
        self.flippy.setChatAbsolute(TutorialGreeting, CFSpeech|CFTimeout)
        self.acceptOnce('enter' + self.flippy.collNodePath.node().getName(), self.enterIntro)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.flippy = NPCToons.createLocalNPC(2001)
        self.flippy.reparentTo(render)
        self.flippy.setPosHpr(0, 20, -0.5, 180, 0, 0)
        self.flippy.initializeBodyCollisions('toon')
        self.flippy.useLOD(1000)
        self.flippy.startBlink()
        self.flippy.addActive()

        self.restockSfx = base.loadSfx('phase_9/audio/sfx/CHQ_SOS_pies_restock.ogg')

        origin1 = self.geom.attachNewNode('cog_origin_1')
        origin2 = self.geom.attachNewNode('cog_origin_2')
        origin3 = self.geom.attachNewNode('cog_origin_3')
        origin1.setPos(-6, 80, -0.5)
        origin2.setPos(0, 70, -0.5)
        origin3.setPos(6, 80, -0.5)

        self.cog1 = CogPinata(origin1, 100)
        self.cog2 = CogPinata(origin2, 200)
        self.cog3 = CogPinata(origin3, 300)
        self.cogs = [self.cog1, self.cog2, self.cog3]
        for cog in self.cogs:
            cog.pose('up', 0)

        self.tart = loader.loadModel('phase_3.5/models/props/tart')
        self.flower = loader.loadModel('phase_3.5/models/props/squirting-flower')

    def unload(self):
        ToonHood.unload(self)
        self.tart.removeNode()
        self.flower.removeNode()
        del self.tart
        del self.flower
        del self.flippy

    def enterIntro(self, *args):
        self.disableToon()
        self.toon.setAnimState('neutral')
        self.toon.setZ(-0.5)
        self.flippy.lookAt(self.toon)
        camera.wrtReparentTo(self.flippy)
        self.toon.setY(self.flippy, 5)
        h = PythonUtil.fitDestAngle2Src(self.toon.getH(self.flippy), 215)
        camera.posHprInterval(2, (-6, 9, 4), (h, 0, 0), blendType='easeOut').start()
        self.introChat(0)

    def introChat(self, pageNumber):
        if pageNumber >= len(TutorialIntro) - 1:
            self.flippy.setLocalPageChat(TutorialIntro[-1], True)
            self.acceptOnce('Nametag-nextChat', self.enterGag)
        else:
            self.flippy.setLocalPageChat(TutorialIntro[pageNumber], None)
            self.acceptOnce('Nametag-nextChat', self.introChat, [pageNumber + 1])
        if pageNumber == 6:
            self.flippy.sadEyes()
            self.flippy.blinkEyes()
        elif pageNumber == 7:
            self.flippy.normalEyes()
            self.flippy.blinkEyes()

    def enterGag(self):
        self.flippy.clearChat()
        self.inventory = self.toon.inventory
        self.inventory.zeroInv()
        self.inventory.updateGUI()
        h = PythonUtil.fitDestAngle2Src(camera.getH(self.flippy), 180)
        camera.posHprInterval(2, (1, 7, 4), (h, 0, 0), blendType='easeOut').start()
        taskMgr.doMethodLater(2, self.gagChat, 'gagChat')

    def gagChat(self, task):
        self.flippy.setLocalPageChat(TutorialGags[0], True)
        self.acceptOnce('Nametag-nextChat', self.gagSequence)
        return task.done

    def gagSequence(self):
        self.flippy.clearChat()
        gagSeq = Sequence(
            Func(self.inventory.reparentTo, camera),
            Func(self.inventory.show),
            Func(self.inventory.noDetail),
            Func(self.inventory.setPosHprScale, -0.77, 7.42, 1.11, 0, 0, 0, .01, .01, .01),
            Func(self.setInventoryYPos, 4, 0, -.1),
            Func(self.setInventoryYPos, 5, 0, -.1),
            Func(self.inventory.scaleInterval(1, (3, .01, 3)).start),
            Wait(1),
            Func(self.tart.reparentTo, self.flippy.getGeomNode().find('**/def_joint_right_hold')),
            Func(self.tart.setPosHprScale, 0.19, 0.02, 0.00, 0.00, 0.00, 349.38, 0.34, 0.34, 0.34),
            Func(self.flippy.setPlayRate, 1.8, 'right-hand-start'),
            Func(self.flippy.play, 'right-hand-start'),
            Wait(1.1574),
            Func(self.flippy.setPlayRate, 1.1, 'right-hand'),
            Func(self.flippy.loop, 'right-hand'),
            Wait(0.8),
            Func(self.tart.wrtReparentTo, camera),
            Func(self.tart.posHprScaleInterval(0.589, pos=(-1.37, 4.56, 0), hpr=(329.53, 39.81, 346.76), scale=(0.6, 0.6, 0.6)).start),
            Wait(1.094),
            Func(self.tart.posHprScaleInterval(1, pos=(-1.66, 7.42, -0.36), hpr=(0, 30, 30), scale=(0.12, 0.12, 0.12)).start),
            Func(self.flippy.setPlayRate, -1.5, 'right-hand-start'),
            Func(self.flippy.play, 'right-hand-start'),
            Wait(1),
            Func(self.addInventory, 4, 0, 1),
            Func(self.inventory.setPosHprScale, -0.77, 7.42, 1.11, 0, 0, 0, 3, .01, 3),
            Func(self.tart.reparentTo, hidden),
            Func(self.flower.reparentTo, self.flippy.find('**/def_joint_right_hold')),
            Func(self.flower.setPosHprScale, 0.10, -0.14, 0.20, 180.00, 287.10, 168.69, 0.70, 0.70, 0.70),
            Func(self.flippy.setPlayRate, 1.8, 'right-hand-start'),
            Func(self.flippy.play, 'right-hand-start'),
            Wait(1.1574),
            Func(self.flippy.setPlayRate, 1.1, 'right-hand'),
            Func(self.flippy.loop, 'right-hand'),
            Wait(0.8),
            Func(self.flower.wrtReparentTo, camera),
            Func(self.flower.posHprScaleInterval(0.589, pos=(-1.75, 4.77, 0.00), hpr=(30.00, 180.00, 16.39), scale=(0.75, 0.75, 0.75)).start),
            Wait(1.094),
            Func(self.flower.posHprScaleInterval(1, pos=(-1.76, 7.42, -0.63), hpr=(179.96, -89.9, -153.43), scale=(0.12, 0.12, 0.12)).start),
            Func(self.flippy.setPlayRate, -1.5, 'right-hand-start'),
            Func(self.flippy.play, 'right-hand-start'),
            Wait(1),
            Func(self.addInventory, 5, 0, 1),
            Func(self.inventory.setPosHprScale, -0.77, 7.42, 1.11, 0, 0, 0, 3, .01, 3),
            Func(self.flower.reparentTo, hidden),
            Func(self.flippy.loop, 'neutral'),
            Wait(1),
            Func(self.flippy.setLocalPageChat, TutorialGags[1], True),
            Func(self.acceptOnce, 'Nametag-nextChat', self.enterLaffMeter)
        )
        gagSeq.start()

    def enterLaffMeter(self):
        self.flippy.clearChat()
        self.laffMeter = self.toon.laffMeter
        laffSeq = Sequence(
            Func(self.flippy.setPlayRate, 1.0, 'right-hand-start'),
            Func(self.flippy.play, 'right-hand-start'),
            Func(self.inventory.hide),
            Func(self.inventory.reparentTo, hidden),
            Func(self.setInventoryYPos, 4, 0, 0),
            Func(self.setInventoryYPos, 5, 0, 0),
            Func(self.inventory.hideDetail),
            Func(self.inventory.setPosHprScale, 0, 0, 0, 0, 0, 0, 1, 1, 1),
            Wait(1),
            Func(self.laffMeter.start),
            Func(self.laffMeter.setPos, 0.153, 0.0, 0.13),
            Func(self.laffMeter.setScale, 0, 0, 0),
            Func(self.laffMeter.wrtReparentTo, aspect2d),
            Func(self.laffMeter.posInterval(1, pos=(-0.25, 0, -0.15)).start),
            Func(self.laffMeter.scaleInterval(1, scale=(0.2, 0.2, 0.2)).start),
            Wait(1.0833),
            Func(self.flippy.setPlayRate, 1.0, 'right-hand'),
            Func(self.flippy.loop, 'right-hand'),
            Func(self.laffMeterChat, 0)
        )
        laffSeq.start()

    def laffMeterChat(self, pageNumber):
        if pageNumber == 1:
            self.flippy.setLocalPageChat(TutorialLaffMeter[1], True)
            self.acceptOnce('Nametag-nextChat', self.laffMeterSequence)
        else:
            self.flippy.setLocalPageChat(TutorialLaffMeter[pageNumber], None)
            self.acceptOnce('Nametag-nextChat', self.laffMeterChat, [pageNumber + 1])

    def laffMeterSequence(self):
        self.flippy.clearChat()
        laffSeq = Sequence(
            Func(self.flippy.sadEyes),
            Func(self.flippy.blinkEyes),
            Func(self.laffMeter.adjustFace, 15, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 14, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 13, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 12, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 11, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 10, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 9, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 8, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 7, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 6, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 5, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 4, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 3, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 2, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 1, 15),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 0, 15),
            Func(self.flippy.setLocalPageChat, TutorialLaffMeter[2], True),
            Func(self.acceptOnce, 'Nametag-nextChat', self.laffMeterSequence2)
        )
        laffSeq.start()

    def laffMeterSequence2(self):
        self.flippy.clearChat()
        laffSeq = Sequence(
            Func(self.flippy.normalEyes),
            Func(self.flippy.blinkEyes),
            Func(self.laffMeter.adjustFace, 15, 15),
            Func(self.laffMeter.wrtReparentTo, base.a2dBottomLeft),
            Wait(0.5),
            Func(self.laffMeter.posInterval(0.6, pos=(0.153, 0.0, 0.13)).start),
            Func(self.laffMeter.scaleInterval(0.6, scale=(0.075, 0.075, 0.075)).start),
            Func(self.flippy.setPlayRate, -2.0, 'right-hand-start'),
            Func(self.flippy.loop, 'right-hand-start'),
            Wait(1.0625),
            Func(self.flippy.loop, 'neutral')
            #Func(self.enterBook)
        )
        laffSeq.start()

    def setInventoryYPos(self, track, level, yPos):
        button = self.inventory.buttons[track][level].stateNodePath[0]
        text = button.find('**/+TextNode')
        text.setY(yPos)

    def addInventory(self, track, level, number):
        countSound = base.loadSfx('phase_3.5/audio/sfx/tick_counter.ogg')
        base.playSfx(countSound)
        self.inventory.buttonBoing(track, level)
        self.inventory.addItems(track, level, number)
        self.inventory.updateGUI(track, level)

    # Temporary enabling and disabling of the toon before the player recieves their laff meter, shtickerbook, etc.
    def enableToon(self):
        self.toon.collisionsOn()
        self.toon.enableAvatarControls()
        self.toon.setupSmartCamera()
        self.toon.beginAllowPies()

    def disableToon(self):
        self.toon.stopUpdateSmartCamera()
        self.toon.shutdownSmartCamera()
        self.toon.disableAvatarControls()
        self.toon.collisionsOff()
        self.toon.endAllowPies()

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)
