from panda3d.core import *
from libotp import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from toontown.toon import NPCToons
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.hood.ToonHood import ToonHood
from toontown.tutorial.CogPinata import CogPinata
from toontown.hood import SkyUtil
from toontown.suit import SuitDNA
from toontown.suit import BattleSuit
from toontown.battle.Battle import Battle
from toontown.town.TownBattle import TownBattle
from toontown.shader import WaterShader

class Tutorial(ToonHood):
    notify = directNotify.newCategory('Tutorial')
    notify.setInfo(1)

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.Tutorial
        self.hoodFile = 'phase_14/models/streets/tutorial_street'
        self.spookyHoodFile = self.hoodFile
        self.winterHoodFile = self.hoodFile
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.toon = base.localAvatar
        self.suitPoints = [
            Point3(-5, 95, -0.5),
            Point3(-5, 85, -0.5),
            Point3(45, 85, -0.5),
            Point3(45, 95, -0.5)
        ]

    def enter(self, tunnel=None, init=0):
        self.toon.setZoneId(self.zoneId)
        self.toon.setPos(0, 0, -0.5)
        musicMgr.playCurrentZoneMusic()
        self.waterShader.start('water', self.geom, self.sky)
        Sequence(Wait(0.3), Func(self.toon.enterTeleportIn, 1, 0, self.__handleEntered)).start()

    def exit(self):
        self.spookyMusic.stop()
        self.ignoreAll()
        self.waterShader.stop()
        # This will always be true unless we're exiting from a crash or deliberate close out of the game
        if base.localAvatar.tutorialAck:
            self.toon.laffMeter.start()
            self.toon.book.hideButton()
            self.book['command'] = self.toon.book.open
            self.chat['command'] = self.toon.chatMgr.openChatInput
            self.chat['extraArgs'] = ['']
            self.toon.chatMgr.enableKeyboardShortcuts()
            self.toon.experienceBar.show()

    def __handleEntered(self):
        self.toon.exitTeleportIn()
        self.enableToon()
        self.flippy.setChatAbsolute(TTLocalizer.TutorialGreeting, CFSpeech|CFTimeout)
        self.acceptOnce('enter' + self.flippy.collNodePath.node().getName(), self.enterIntro)

    def load(self):
        ToonHood.load(self)
        self.waterShader = WaterShader.WaterShader()
        self.waterShader.waterPos = 0

        self.spookyMusic = base.loader.loadMusic('phase_12/audio/bgm/Bossbot_Factory_v3.ogg')
        self.battleMusic = base.loader.loadMusic('phase_3.5/audio/bgm/encntr_general_bg.ogg')

        self.townBattle = TownBattle('townbattle-done')
        self.townBattle.load()

        self.flippy = NPCToons.createLocalNPC(1001)
        self.flippy.reparentTo(render)
        self.flippy.setPosHpr(0, 20, -0.5, 180, 0, 0)
        self.flippy.initializeBodyCollisions('toon')
        self.flippy.startBlink()
        self.flippy.addActive()

        gui = loader.loadModel('phase_3.5/models/gui/tutorial_gui')
        self.guiCogs = gui.find('**/suits')
        self.guiSquirt = gui.find('**/squirt2')
        self.guiBldgs = gui.find('**/suit_buildings')
        self.guiFarm = gui.find('**/toon_buildings')
        self.tart = loader.loadModel('phase_3.5/models/props/tart')
        self.flower = loader.loadModel('phase_3.5/models/props/squirting-flower')
        self.restockSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_pies_restock.ogg')
        self.guiCogs.setPosHprScale(-1.25, 8, 0, 0, 0, 0, 0.01, 0.01, 0.01)
        self.guiSquirt.setPosHprScale(-1.25, 8, 0, 0, 0, 0, 1.875, 1.875, 1.875)
        self.guiBldgs.setPosHprScale(-1.25, 8, 0, 0, 0, 0, 1.875, 1.875, 1.875)
        self.guiFarm.setPosHprScale(-1.25, 8, 0, 0, 0, 0, 1.875, 1.875, 1.875)
        gui.removeNode()

        origin1 = self.geom.attachNewNode('cog_origin_1')
        origin2 = self.geom.attachNewNode('cog_origin_2')
        origin3 = self.geom.attachNewNode('cog_origin_3')
        origin1.setPos(-6, 75, -0.5)
        origin2.setPos(0, 65, -0.5)
        origin3.setPos(6, 75, -0.5)

        self.cog1 = CogPinata(origin1, 100)
        self.cog2 = CogPinata(origin2, 200)
        self.cog3 = CogPinata(origin3, 300)
        self.cogs = [self.cog1, self.cog2, self.cog3]
        for cog in self.cogs:
            cog.pose('up', 0)

        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('cc')
        self.suit = BattleSuit.BattleSuit()
        self.suit.setDNA(suitDNA)
        self.suit.setLevel(0)
        self.suit.setPosHpr(45, 95, -0.5, 90, 0, 0)

        self.battleCell = NodePath('battle_cell_1')
        self.battleCell.reparentTo(self.geom)
        self.battleCell.setPosHpr(0, 90, -0.5, 270, 0, 0)

    def unload(self):
        ToonHood.unload(self)
        self.waterShader.stop()
        self.waterShader = None
        self.townBattle.unload()
        self.townBattle.cleanup()
        self.guiCogs.removeNode()
        self.guiSquirt.removeNode()
        self.guiBldgs.removeNode()
        self.guiFarm.removeNode()
        self.tart.removeNode()
        self.flower.removeNode()
        del self.spookyMusic
        del self.battleMusic
        del self.townBattle
        del self.flippy
        del self.guiCogs
        del self.guiSquirt
        del self.guiBldgs
        del self.guiFarm
        del self.tart
        del self.flower
        for cog in self.cogs:
            del cog
        del self.suit
        del self.battleCell

    def enterIntro(self, *args):
        self.flippy.clearChat()
        self.disableToon()
        self.toon.setAnimState('neutral')
        self.toon.setZ(-0.5)
        self.flippy.lookAt(self.toon)
        camera.wrtReparentTo(self.flippy)
        self.toon.lookAt(self.flippy)
        self.toon.setY(self.flippy, 7.5)
        camera.setPosHpr(-2, 7, 3.3, 205, 5, 0)
        Sequence(Wait(0.5), Func(self.introSequence)).start()

    def introSequence(self):
        self.flippy.clearChat()
        self.flippy.setLocalPageChat(TTLocalizer.TutorialIntro, None)
        self.accept(self.flippy.uniqueName('nextChatPage'), self.introChat)
        self.acceptOnce(self.flippy.uniqueName('doneChatPage'), self.enterGag)

    def introChat(self, pageNumber, elapsedTime):
        if pageNumber == 1:
            Sequence(
                Func(self.guiCogs.reparentTo, camera),
                Func(self.guiCogs.scaleInterval(0.5, (2, 2, 2)).start),
                Wait(0.5),
                Func(self.guiCogs.scaleInterval(0.1, (1.875, 1.875, 1.875)).start)
            ).start()
        elif pageNumber == 3:
            self.guiCogs.reparentTo(hidden)
            self.guiSquirt.reparentTo(camera)
        elif pageNumber == 4:
            self.guiSquirt.reparentTo(hidden)
            self.guiBldgs.reparentTo(camera)
        elif pageNumber == 5:
            self.guiBldgs.reparentTo(hidden)
            self.guiFarm.reparentTo(camera)
        elif pageNumber == 6:
            Sequence(
                Func(self.guiFarm.scaleInterval(0.1, (2, 2, 2)).start),
                Wait(0.1),
                Func(self.guiFarm.scaleInterval(0.5, (0.01, 0.01, 0.01)).start),
                Wait(0.5),
                Func(self.guiFarm.reparentTo, hidden),
            ).start()

    def enterGag(self, elapsedTime):
        self.flippy.clearChat()
        self.ignore(self.flippy.uniqueName('nextChatPage'))
        self.inventory = self.toon.inventory
        self.inventory.zeroInv()
        self.inventory.updateGUI()
        self.flippy.setLocalPageChat(TTLocalizer.TutorialGags_0, None)
        self.acceptOnce(self.flippy.uniqueName('doneChatPage'), self.gagSequence)

    def gagSequence(self, elapsedTime):
        self.flippy.clearChat()
        gagSeq = Sequence(
            Func(self.inventory.reparentTo, camera),
            Func(self.inventory.show),
            Func(self.inventory.noDetail),
            Func(self.inventory.setPosHprScale, -0.77, 7.92, 1.11, 0, 0, 0, .01, .01, .01),
            Func(self.setInventoryYPos, 4, 0, -.1),
            Func(self.setInventoryYPos, 5, 0, -.1),
            Func(self.inventory.scaleInterval(1, (3, .01, 3)).start),
            Wait(1),
            Func(self.tart.reparentTo, self.flippy.find('**/1000/**/def_joint_right_hold')),
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
            Func(self.inventory.setPosHprScale, -0.77, 7.92, 1.11, 0, 0, 0, 3, .01, 3),
            Func(self.tart.reparentTo, hidden),
            Func(self.flower.reparentTo, self.flippy.find('**/1000/**/def_joint_right_hold')),
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
            Func(self.inventory.setPosHprScale, -0.77, 7.92, 1.11, 0, 0, 0, 3, .01, 3),
            Func(self.flower.reparentTo, hidden),
            Func(self.flippy.loop, 'neutral'),
            Wait(1),
            Func(self.flippy.setLocalPageChat, TTLocalizer.TutorialGags_1, None),
            Func(self.acceptOnce, self.flippy.uniqueName('doneChatPage'), self.enterLaffMeter)
        )
        gagSeq.start()

    def enterLaffMeter(self, elapsedTime):
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
            Func(self.flippy.setLocalPageChat, TTLocalizer.TutorialLaffMeter_0, None),
            Func(self.acceptOnce, self.flippy.uniqueName('doneChatPage'), self.greenLocalAvatar)
        )
        laffSeq.start()

    def greenLocalAvatar(self, elapsedTime):
        self.flippy.clearChat()
        laffSeq = Sequence(
            Func(self.flippy.sadEyes),
            Func(self.flippy.blinkEyes),
            Func(self.laffMeter.adjustFace, 20, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 19, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 18, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 17, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 16, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 15, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 14, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 13, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 12, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 11, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 10, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 9, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 8, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 7, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 6, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 5, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 4, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 3, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 2, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 1, 20),
            Wait(0.1),
            Func(self.laffMeter.adjustFace, 0, 20),
            Func(self.flippy.setLocalPageChat, TTLocalizer.TutorialLaffMeter_1, None),
            Func(self.acceptOnce, self.flippy.uniqueName('doneChatPage'), self.laffMeterSequence)
        )
        laffSeq.start()

    def laffMeterSequence(self, elapsedTime):
        self.flippy.clearChat()
        laffSeq = Sequence(
            Func(self.flippy.normalEyes),
            Func(self.flippy.blinkEyes),
            Func(self.laffMeter.adjustFace, 20, 20),
            Func(self.laffMeter.wrtReparentTo, base.a2dBottomLeft),
            Wait(0.5),
            Func(self.laffMeter.posInterval(0.6, pos=(0.153, 0.0, 0.13)).start),
            Func(self.laffMeter.scaleInterval(0.6, scale=(0.075, 0.075, 0.075)).start),
            Func(self.flippy.setPlayRate, -2.0, 'right-hand-start'),
            Func(self.flippy.loop, 'right-hand-start'),
            Wait(1.0625),
            Func(self.flippy.loop, 'neutral'),
            Func(self.enterBook)
        )
        laffSeq.start()

    def enterBook(self):
        self.flippy.setLocalPageChat(TTLocalizer.TutorialBook_0, None)
        self.acceptOnce(self.flippy.uniqueName('doneChatPage'), self.bookSequence)

    def bookSequence(self, elapsedTime):
        self.flippy.clearChat()
        self.book = self.toon.book.bookOpenButton
        self.book['command'] = None
        bookSeq = Sequence(
            Func(self.book.reparentTo, aspect2d),
            Func(self.book.show),
            Func(self.book.setPos, 0, 0, 0),
            Func(self.book.setScale, 0.5, 0.5, 0.5),
            Func(self.book.setColorScale, 1, 1, 1, 0),
            Func(self.book.colorScaleInterval(0.5, (1, 1, 1, 1)).start),
            Func(self.book.wrtReparentTo, base.a2dBottomRight),
            Wait(1.5),
            Func(self.book.posInterval(1, (-0.158, 0, 0.17)).start),
            Func(self.book.scaleInterval(1, (0.305, 0.305, 0.305)).start),
            Wait(1),
            Func(self.exitBook)
        )
        bookSeq.start()

    def exitBook(self):
        self.flippy.setLocalPageChat(TTLocalizer.TutorialBook_1, None)
        self.acceptOnce(self.flippy.uniqueName('doneChatPage'), self.enterChat)

    def enterChat(self, elapsedTime):
        self.flippy.setLocalPageChat(TTLocalizer.TutorialChat_0, None)
        self.acceptOnce(self.flippy.uniqueName('doneChatPage'), self.chatSequence)

    def chatSequence(self, elapsedTime):
        self.flippy.clearChat()
        self.toon.startChat()
        self.toon.chatMgr.disableKeyboardShortcuts()
        self.chat = self.toon.chatMgr.chatButton
        self.chat['command'] = None
        chatSeq = Sequence(
            Func(self.chat.reparentTo, aspect2d),
            Func(self.chat.show),
            Func(self.chat.setPos, 0, 0, 0),
            Func(self.chat.setScale, 1.5, 1.5, 1.5),
            Func(self.chat.setColorScale, 1, 1, 1, 0),
            Func(self.chat.colorScaleInterval(0.5, (1, 1, 1, 1)).start),
            Func(self.chat.wrtReparentTo, base.a2dTopLeft),
            Wait(1.5),
            Func(self.chat.posInterval(1, (0.0683, 0, -0.072)).start),
            Func(self.chat.scaleInterval(1, (1.179, 1.179, 1.179)).start),
            Wait(1),
            Func(self.flippy.setLocalPageChat, TTLocalizer.TutorialChat_1, None),
            Func(self.acceptOnce, self.flippy.uniqueName('doneChatPage'), self.exitChat)
        )
        chatSeq.start()

    def exitChat(self, elapsedTime):
        self.flippy.setLocalPageChat(TTLocalizer.TutorialTraining_0, None)
        self.acceptOnce(self.flippy.uniqueName('doneChatPage'), self.trainingSequence)

    def trainingSequence(self, elapsedTime):
        trainingSeq = Sequence(
            Func(self.flippy.setChatAbsolute, TTLocalizer.TutorialTraining_1, CFSpeech|CFTimeout),
            Func(self.flippy.hprInterval(2, (0, 0, 0)).start),
            Func(self.flippy.loop, 'walk'),
            Func(self.enableToon),
            Wait(2),
            Func(self.flippy.loop, 'neutral'),
            Func(self.enterTraining)
        )
        trainingSeq.start()

    def enterTraining(self):
        for cog in self.cogs:
            cog.intoIdle()
            cog.startActive()
        self.toon.givePies(0, FunnyFarmGlobals.FullPies)
        base.playSfx(self.restockSfx)
        self.acceptOnce('training-done', self.exitTraining)
        taskMgr.add(self.checkActiveCogs, 'checkActiveCogs')

    def checkActiveCogs(self, task):
        cog1Active = self.cog1.getActive()
        cog2Active = self.cog2.getActive()
        cog3Active = self.cog3.getActive()
        if not cog1Active and not cog2Active and not cog3Active:
            Sequence(Wait(2.5), Func(messenger.send, 'training-done')).start()
            return task.done
        return task.cont

    def exitTraining(self):
        taskMgr.remove('checkActiveCogs')
        self.toon.endAllowPies()
        self.toon.setNumPies(0)
        self.enterCog()

    def enterCog(self):
        self.disableToon()
        self.toon.setAnimState('neutral')
        self.toon.setZ(-0.5)
        camera.wrtReparentTo(self.flippy)
        camera.setPosHpr(0, 9, 4, 180, 0, 0)
        self.flippy.setLocalPageChat(TTLocalizer.TutorialTraining_2, None)
        self.acceptOnce(self.flippy.uniqueName('doneChatPage'), self.cogSequence)

    def cogSequence(self, elapsedTime):
        self.flippy.clearChat()
        cogSeq = Sequence(
            Func(musicMgr.stopMusic),
            Func(camera.wrtReparentTo, render),
            Func(self.flippy.loop, 'walk'),
            self.flippy.hprInterval(1, (-30, 0, 0)),
            Func(self.flippy.loop, 'neutral'),
            Func(self.flippy.setLocalPageChat, TTLocalizer.TutorialCog_0, None),
            Func(self.acceptOnce, self.flippy.uniqueName('doneChatPage'), self.cogFlyIn)
        )
        cogSeq.start()

    def cogFlyIn(self, elapsedTime):
        self.flippy.clearChat()
        # Looks like we have an unexpected visitor...
        flyInSeq = Sequence(
            Func(base.transitions.fadeOut, 1.0),
            Wait(1),
            Func(aspect2d.hide),
            Func(camera.setPosHpr, -5, 95, 4, 270, 12, 0),
            Func(base.transitions.fadeIn, 1.0),
            Func(musicMgr.playMusic, self.spookyMusic, looping=1),
            Wait(1),
            Func(self.suit.reparentTo, render),
            Func(self.suit.addActive),
            self.suit.beginSupaFlyMove(Point3(45, 95, -0.5), True, 'TutorialSuitFlyIn', walkAfterLanding=True),
            Func(self.startSuitWalkInterval),
            Wait(2),
            Func(base.transitions.fadeOut, 1.0),
            Wait(1),
            Func(aspect2d.show),
            Func(camera.wrtReparentTo, self.flippy),
            Func(camera.setPosHpr, 0, 9, 4, 180, 0, 0),
            Func(base.transitions.fadeIn, 1.0),
            Wait(1),
            Func(self.flippy.sadEyes),
            Func(self.flippy.blinkEyes),
            Func(self.flippy.setLocalPageChat, TTLocalizer.TutorialCog_1, 1),
            Func(self.acceptOnce, self.flippy.uniqueName('doneChatPage'), self.exitCog)
        )
        flyInSeq.start()

    def exitCog(self, elapsedTime):
        self.flippy.clearChat()
        self.enableToon()
        self.suit.initializeBodyCollisions('suit')
        self.suit.enableBattleDetect(self.enterBattle)

    def enterBattle(self, collEntry):
        self.disableToon()
        self.toon.book.hideButton()
        self.stopSuitWalkInterval()
        self.battle = Battle(self.townBattle, toons=[self.toon], suits=[self.suit], tutorialFlag=1)
        # Never parent a battle directly to render, always use a battle cell 
        # otherwise __faceOff will fuck you in the ass
        self.battle.reparentTo(self.battleCell)
        self.battle.enter()
        self.spookyMusic.stop()
        musicMgr.playMusic(self.battleMusic, looping=1)
        self.accept(self.townBattle.doneEvent, self.exitBattle)

    def exitBattle(self, doneStatus):
        self.enableToon()
        self.toon.book.showButton()
        self.battleMusic.stop()
        musicMgr.playMusic(self.spookyMusic, looping=1)
        self.ignore(self.townBattle.doneEvent)
        self.battle.cleanupBattle()
        self.battle.delete()
        self.battle = None
        self.enterOutro()

    def startSuitWalkInterval(self):
        self.suitWalk = Sequence(
            Func(self.suit.setHpr, 90, 0, 0),
            self.suit.posInterval(12, self.suitPoints[0]),
            Func(self.suit.setHpr, 180, 0, 0),
            self.suit.posInterval(2, self.suitPoints[1]),
            Func(self.suit.setHpr, 270, 0, 0),
            self.suit.posInterval(12, self.suitPoints[2]),
            Func(self.suit.setHpr, 0, 0, 0),
            self.suit.posInterval(2, self.suitPoints[3])
        )
        self.suitWalk.loop()

    def stopSuitWalkInterval(self):
        self.suit.disableBattleDetect()
        self.suitWalk.pause()
        self.suitWalk = None

    def enterOutro(self):
        self.enableToon()
        self.flippy.setHpr(0, 0, 0)
        flippyExit = Sequence(
            Func(self.flippy.clearChat),
            Func(camera.wrtReparentTo, self.toon),
            Func(self.flippy.enterTeleportOut, callback=self.flippy.delete),
            Wait(3.2),
            Func(self.flippy.hide),
            Func(self.flippy.removeActive),
            Wait(0.2),
            Func(self.exitOutro)
        )
        Sequence(
            Wait(0.5),
            Func(self.disableToon),
            Func(camera.wrtReparentTo, self.flippy),
            Func(camera.setPosHpr, 0, 9, 4, 180, 0, 0),
            Func(self.flippy.setLocalPageChat, TTLocalizer.TutorialOutro, 1),
            Func(self.acceptOnce, self.flippy.uniqueName('doneChatPage'), flippyExit.start)
        ).start()

    def exitOutro(self):
        self.enableToon()
        self.disableToon()
        self.toon.addQuest(1001)
        self.toon.questPage.questFrames[0].setPosHpr(0, 0, 0, 0, 0, 0)
        self.toon.questPage.showQuestsOnscreen()
        self.toon.setTutorialAck(1)
        self.acceptOnce('bubble-done', self.questDialogDone)
        Sequence(Wait(0.5), Func(base.localAvatar.showInfoBubble, 0, 'bubble-done')).start()

    def questDialogDone(self):
        self.toon.questPage.hideQuestsOnscreen()
        self.toon.questPage.questFrames[0].setPosHpr(-0.45, 0, 0.28, 0, 0, 0)
        self.startActive()
        self.enableToon()

    def enterHood(self, zoneId):
        # For now we're just entering through the rickety road tunnel
        base.cr.playGame.enterHood(zoneId, tunnel='1100')

    # Misc. functions

    def setInventoryYPos(self, track, level, yPos):
        button = self.inventory.buttons[track][level].stateNodePath[0]
        text = button.find('**/+TextNode')
        text.setY(yPos)

    def addInventory(self, track, level, number):
        countSound = base.loader.loadSfx('phase_3.5/audio/sfx/tick_counter.ogg')
        base.playSfx(countSound)
        self.inventory.buttonBoing(track, level)
        self.inventory.addItems(track, level, number)
        self.inventory.updateGUI(track, level)

    # Alternate versions of LocalToon's enable() and disable() functions,
    # so that we don't show their shtickerbook, laff meter, or chat button.
    def enableToon(self):
        self.toon.enabled = 1
        self.toon.startBlink()
        self.toon.attachCamera()
        shouldPush = 1
        if len(self.toon.cameraPositions) > 0:
            shouldPush = not self.toon.cameraPositions[self.toon.cameraIndex][4]
        self.toon.startUpdateSmartCamera(shouldPush)
        self.toon.showName()
        self.toon.collisionsOn()
        self.toon.enableAvatarControls()
        self.toon.beginAllowPies()
        self.toon.walkStateData.fsm.request('walking')

    def disableToon(self):
        self.toon.enabled = 0
        self.toon.walkStateData.fsm.request('off')
        self.toon.disableAvatarControls()
        self.toon.stopUpdateSmartCamera()
        self.toon.stopBlink()
        self.toon.detachCamera()
        self.toon.collisionsOff()
        self.toon.controlManager.placeOnFloor()
        self.toon.endAllowPies()

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)
