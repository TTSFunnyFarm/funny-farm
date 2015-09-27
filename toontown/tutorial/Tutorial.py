from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.toon import NPCToons
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.hood.ToonHood import ToonHood
from otp.nametag.NametagConstants import *
from toontown.tutorial.CogPinata import CogPinata

class Tutorial(ToonHood):
    notify = directNotify.newCategory('Tutorial')
    notify.setInfo(True)

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.Tutorial
        self.hoodFile = 'phase_14/models/modules/tutorial'
        self.spookyHoodFile = self.hoodFile
        self.winterHoodFile = self.hoodFile
        self.skyFile = 'phase_3.5/models/props/TT_sky'

    def enter(self, shop=None, tunnel=None):
        musicMgr.startTutorial()
        base.localAvatar.disableAvatarControls()
        base.localAvatar.enterTeleportIn(callback=self.__handleEntered)

    def exit(self):
        musicMgr.stopTutorial()
        self.ignoreAll()
        self.unload()
        base.cr.playGame.enterFFHood()
        base.localAvatar.setupSmartCamera()
        base.localAvatar.laffMeter.start()
        base.localAvatar.book.showButton()
        self.book['command'] = base.localAvatar.book.open
        self.chat['command'] = base.localAvatar.chatMgr.openChatInput
        self.chat['extraArgs'] = [None]
        base.localAvatar.chatMgr.enableKeyboardShortcuts()
        base.localAvatar.enableAvatarControls()

    def __handleEntered(self):
        base.localAvatar.exitTeleportIn()
        base.localAvatar.enableAvatarControls()
        self.flippy.setChatAbsolute('Hello! Use the arrow keys to move.', CFSpeech|CFTimeout)
        self.acceptOnce('enter' + self.flippy.collNodePath.node().getName(), self.enterIntro)

    def load(self):
        ToonHood.load(self)
        self.geom.find('**/donaldSZ').removeNode()
        self.sky.setScale(2.8)
        self.startSkyTrack()

        self.flippy = NPCToons.createLocalNPC(2001)
        self.flippy.reparentTo(render)
        self.flippy.setPosHpr(0, 15, -0.5, 180, 0, 0)
        self.flippy.initializeBodyCollisions('toon')
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

        self.flower = loader.loadModel('phase_3.5/models/props/squirting-flower')
        self.tart = loader.loadModel('phase_3.5/models/props/tart')

    def unload(self):
        ToonHood.unload(self)
        for cog in self.cogs:
            del cog
        del self.flippy

    def enterIntro(self, *args):
        base.localAvatar.disableAvatarControls()
        base.localAvatar.setMovementAnimation('neutral')
        base.localAvatar.setPosHpr(0, 6, -0.5, 0, 0, 0)
        camera.posInterval(2, (0, 2, 4), blendType='easeOut').start()
        self.introChat(0)

    def introChat(self, pageNumber):
        if pageNumber >= len(TTLocalizer.TutorialIntro) - 1:
            self.flippy.setLocalPageChat(TTLocalizer.TutorialIntro[-1], True)
            self.acceptOnce('Nametag-nextChat', self.introSequence)
        else:
            self.flippy.setLocalPageChat(TTLocalizer.TutorialIntro[pageNumber], None)
            self.acceptOnce('Nametag-nextChat', self.introChat, [pageNumber + 1])

    def introSequence(self):
        introSeq = Sequence(
                Func(self.flippy.setChatAbsolute, 'I\'ll give you some pies to start. Practice by throwing them at the targets ahead.', CFSpeech|CFTimeout),
                Func(self.flippy.hprInterval(2, (0, 0, 0)).start),
                Func(self.flippy.actorInterval('walk').loop),
                Func(base.localAvatar.enableAvatarControls),
                Wait(2),
                Func(self.flippy.actorInterval('neutral').loop),
                Func(self.enterTraining),
                Wait(5),
                Func(self.flippy.setChatAbsolute, 'Come to me if you need more pies.', CFSpeech|CFTimeout)
        )
        introSeq.start()

    def enterTraining(self):
        for cog in self.cogs:
            cog.intoIdle()
            cog.startActive()
        base.localAvatar.givePies(4, 10)
        base.playSfx(self.restockSfx)
        self.accept('enter' + self.flippy.collNodePath.node().getName(), self.__handleFlippyCollision)
        self.acceptOnce('training-done', self.exitTraining)
        taskMgr.add(self.checkActiveCogs, 'checkActiveCogs')

    def exitTraining(self):
        self.ignore('enter' + self.flippy.collNodePath.node().getName())
        taskMgr.remove('checkActiveCogs')
        base.localAvatar.endAllowPies()
        base.localAvatar.setNumPies(0)
        self.enterGag()

    def enterGag(self):
        base.localAvatar.disableAvatarControls()
        base.localAvatar.setMovementAnimation('neutral')
        base.localAvatar.setPosHpr(0, 24, -0.5, 180, 0, 0)
        camera.posInterval(2, (0, 2, 4), blendType='easeOut').start()
        self.inventory = base.localAvatar.inventory
        self.inventory.zeroInv()
        self.inventory.updateGUI()
        self.gagChat(0)

    def gagChat(self, pageNumber):
        if pageNumber >= len(TTLocalizer.TutorialGags) - 1:
            camera.posInterval(2, (-1, 2, 4), blendType='easeOut').start()
            self.flippy.setLocalPageChat(TTLocalizer.TutorialGags[-1], True)
            self.acceptOnce('Nametag-nextChat', self.gagSequence)
        else:
            self.flippy.setLocalPageChat(TTLocalizer.TutorialGags[pageNumber], None)
            self.acceptOnce('Nametag-nextChat', self.gagChat, [pageNumber + 1])

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
                Func(self.flower.reparentTo, self.flippy.find('**/def_joint_right_hold')),
                Func(self.flower.setPosHprScale, 0.10, -0.14, 0.20, 180.00, 287.10, 168.69, 0.70, 0.70, 0.70),
                Func(self.flippy.actorInterval('right-hand-start', playRate=1.8).start),
                Wait(1.1574),
                Func(self.flippy.actorInterval('right-hand', playRate=1.1).loop),
                Wait(0.8),
                Func(self.flower.wrtReparentTo, camera),
                Func(self.flower.posHprScaleInterval(0.589, pos=(-1.75, 4.77, 0.00), hpr=(30.00, 180.00, 16.39), scale=(0.75, 0.75, 0.75)).start),
                Wait(1.094),
                Func(self.flower.posHprScaleInterval(1, pos=(-1.76, 7.42, -0.63), hpr=(179.96, -89.9, -153.43), scale=(0.12, 0.12, 0.12)).start),
                Func(self.flippy.actorInterval('right-hand-start', playRate=-1.5).start),
                Wait(1),
                Func(self.addInventory, 5, 0, 1),
                Func(self.inventory.setPosHprScale, -0.77, 7.42, 1.11, 0, 0, 0, 3, .01, 3),
                Func(self.flower.reparentTo, hidden),
                Func(self.tart.reparentTo, self.flippy.find('**/def_joint_right_hold')),
                Func(self.tart.setPosHprScale, 0.19, 0.02, 0.00, 0.00, 0.00, 349.38, 0.34, 0.34, 0.34),
                Func(self.flippy.actorInterval('right-hand-start', playRate=1.8).start),
                Wait(1.1574),
                Func(self.flippy.actorInterval('right-hand', playRate=1.1).loop),
                Wait(0.8),
                Func(self.tart.wrtReparentTo, camera),
                Func(self.tart.posHprScaleInterval(0.589, pos=(-1.37, 4.56, 0), hpr=(329.53, 39.81, 346.76), scale=(0.6, 0.6, 0.6)).start),
                Wait(1.094),
                Func(self.tart.posHprScaleInterval(1, pos=(-1.66, 7.42, -0.36), hpr=(0, 30, 30), scale=(0.12, 0.12, 0.12)).start),
                Func(self.flippy.actorInterval('right-hand-start', playRate=-1.5).start),
                Wait(1),
                Func(self.addInventory, 4, 0, 1),
                Func(self.inventory.setPosHprScale, -0.77, 7.42, 1.11, 0, 0, 0, 3, .01, 3),
                Func(self.tart.reparentTo, hidden),
                Func(self.flippy.actorInterval('right-hand-start').start),
                Wait(1),
                Func(self.inventory.hide),
                Func(self.inventory.reparentTo, hidden),
                Func(self.setInventoryYPos, 4, 0, 0),
                Func(self.setInventoryYPos, 5, 0, 0),
                Func(self.inventory.hideDetail),
                Func(self.inventory.setPosHprScale, 0, 0, 0, 0, 0, 0, 1, 1, 1),
                Func(self.enterLaffMeter)
        )
        gagSeq.start()

    def enterLaffMeter(self):
        self.laffMeter = base.localAvatar.laffMeter
        laffSeq = Sequence(
                Func(self.laffMeter.start),
                Func(self.laffMeter.setPos, 0.153, 0.0, 0.13),
                Func(self.laffMeter.setScale, 0, 0, 0),
                Func(self.laffMeter.wrtReparentTo, aspect2d),
                Func(self.laffMeter.posInterval(1, pos=(-0.25, 0, -0.15)).start),
                Func(self.laffMeter.scaleInterval(1, scale=(0.2, 0.2, 0.2)).start),
                Wait(1.0833),
                Func(self.flippy.actorInterval('right-hand').loop),
                Func(self.laffMeterChat, 0)
        )
        laffSeq.start()

    def laffMeterChat(self, pageNumber):
        if pageNumber >= len(TTLocalizer.TutorialLaffMeter) - 1:
            self.flippy.setLocalPageChat(TTLocalizer.TutorialLaffMeter[-1], True)
            self.acceptOnce('Nametag-nextChat', self.laffMeterSequence)
        else:
            self.flippy.setLocalPageChat(TTLocalizer.TutorialLaffMeter[pageNumber], None)
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
                Func(self.flippy.setLocalPageChat, 'A happy Toon is a healthy Toon!', True),
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
                Func(self.flippy.actorInterval('right-hand-start', playRate=-2).start),
                Wait(1.0625),
                Func(self.flippy.actorInterval('neutral').loop),
                Func(self.enterBook)
        )
        laffSeq.start()

    def enterBook(self):
        self.flippy.setLocalPageChat('Here is your Shticker Book...', True)
        self.acceptOnce('Nametag-nextChat', self.bookSequence)

    def bookSequence(self):
        self.flippy.clearChat()
        self.book = base.localAvatar.book.bookOpenButton
        self.book['command'] = None
        bookSeq = Sequence(
                Func(self.book.reparentTo, aspect2d),
                Func(self.book.show),
                Func(self.book.setPos, 0, 0, 0),
                Func(self.book.setScale, 0.5, 0.5, 0.5),
                Func(self.book.colorScaleInterval(0.5, colorScale=(1, 1, 1, 1), startColorScale=(1, 1, 1, 0)).start),
                Func(self.book.wrtReparentTo, base.a2dBottomRight),
                Wait(1.5),
                Func(self.book.posInterval(1, pos=(-0.158, 0, 0.17)).start),
                Func(self.book.scaleInterval(1, scale=(0.305, 0.305, 0.305)).start),
                Wait(1),
                Func(self.exitBook)
        )
        bookSeq.start()

    def exitBook(self):
        self.flippy.setLocalPageChat('You\'ll find all sorts of neat-o stuff in there.', None)
        self.acceptOnce('Nametag-nextChat', self.enterChat)

    def enterChat(self):
        self.flippy.setLocalPageChat('And finally, here is your chat button.', True)
        self.acceptOnce('Nametag-nextChat', self.chatSequence)

    def chatSequence(self):
        self.flippy.clearChat()
        base.localAvatar.startChat()
        base.localAvatar.chatMgr.disableKeyboardShortcuts()
        self.chat = base.localAvatar.chatMgr.chat_btn
        self.chat['command'] = None
        chatSeq = Sequence(
                Func(self.chat.reparentTo, aspect2d),
                Func(self.chat.show),
                Func(self.chat.setPos, 0, 0, 0),
                Func(self.chat.setScale, 1.5, 1.5, 1.5),
                Func(self.chat.colorScaleInterval(0.5, colorScale=(1, 1, 1, 1), startColorScale=(1, 1, 1, 0)).start),
                Func(self.chat.wrtReparentTo, base.a2dTopLeft),
                Wait(1.5),
                Func(self.chat.posInterval(1, pos=(0.0683, 0, -0.072)).start),
                Func(self.chat.scaleInterval(1, scale=(1.179, 1.179, 1.179)).start),
                Wait(1),
                Func(self.exitChat)
        )
        chatSeq.start()

    def exitChat(self):
        self.flippy.setLocalPageChat('You can use that button to say things! It\'ll come in handy every once in a while.', True)
        self.acceptOnce('Nametag-nextChat', self.enterOutro)

    def enterOutro(self):
        camera.posInterval(2, (0, 2, 4), blendType='easeOut').start()
        self.outroChat(0)

    def outroChat(self, pageNumber):
        if pageNumber >= len(TTLocalizer.TutorialOutro) - 1:
            self.flippy.setLocalPageChat(TTLocalizer.TutorialOutro[-1], True)
            self.acceptOnce('Nametag-nextChat', self.outroSequence)
        else:
            self.flippy.setLocalPageChat(TTLocalizer.TutorialOutro[pageNumber], None)
            self.acceptOnce('Nametag-nextChat', self.outroChat, [pageNumber + 1])

    def outroSequence(self):
        outroSeq = Sequence(
                Func(self.flippy.setChatAbsolute, 'See you later!', CFSpeech|CFTimeout),
                Func(self.flippy.enterTeleportOut, callback=self.flippy.delete),
                Func(base.localAvatar.enableAvatarControls),
                Wait(3.2),
                Func(self.flippy.hide),
                Wait(0.2),
                Func(self.exitOutro)
        )
        outroSeq.start()

    def exitOutro(self):
        base.localAvatar.disableAvatarControls()
        base.localAvatar.enterTeleportOut(callback=self.exit)
        Sequence(Wait(3.2), Func(base.localAvatar.hide)).start()

    def checkActiveCogs(self, task):
        cog1Active = self.cog1.getActive()
        cog2Active = self.cog2.getActive()
        cog3Active = self.cog3.getActive()
        if not cog1Active and not cog2Active and not cog3Active:
            Sequence(Wait(2.5), Func(messenger.send, 'training-done')).start()
            return task.done
        return task.cont

    def __handleFlippyCollision(self, entry):
        if base.localAvatar.numPies >= 0 and base.localAvatar.numPies < 10:
            base.localAvatar.givePies(4, 10)
            base.playSfx(self.restockSfx)

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
