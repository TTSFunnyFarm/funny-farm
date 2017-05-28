from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.login import AvatarChooser
from toontown.makeatoon import MakeAToon
from toontown.toontowngui import TTDialog
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from otp.otpbase import OTPLocalizer
from otp.nametag import NametagGlobals
import random
import PlayGame

class FFClientRepository(DirectObject):
    notify = directNotify.newCategory('ClientRepository')
    notify.setInfo(True)
    AI_TIMEOUT = 30

    def __init__(self):
        self.avChoice = None
        self.avCreate = None
        self.playGame = PlayGame.PlayGame()
        self.playingGame = 0
        self.waitDialog = None

    def begin(self):
        if not base.air.isLoaded:
            base.transitions.fadeIn(1.0)
            # We usually won't get here, but just in case the AI is taking extra long, we'll have them wait.
            # In the future, as we build up our AI more and more, there's a better chance we'll get here.
            self.waitDialog = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.NoButtons, text=OTPLocalizer.AIPleaseWait)
            self.waitDialog.show()
            self.accept('ai-done', self.enterChooseAvatar, [True])
            taskMgr.doMethodLater(self.AI_TIMEOUT, self.aiTimeout, 'aiTimeout')
        else:
            self.enterChooseAvatar()

    def aiTimeout(self, task):
        # Even more unlikely that we'll get here, but better safe than sorry!
        self.ignore('ai-done')
        base.handleGameError('AI services either took too long or could not be started.')
        return task.done

    def enterChooseAvatar(self, fade = False):
        if self.waitDialog:
            self.waitDialog.destroy()
            self.waitDialog = None
            self.ignore('ai-done')
            taskMgr.remove('aiTimeout')
        if fade:
            base.transitions.fadeOut(1.0)
        else:
            base.transitions.fadeScreen(1.0)
        self.avChoice = AvatarChooser.AvatarChooser()
        self.avChoice.load()
        self.avChoice.enter()

    def exitChooseAvatar(self):
        base.transitions.noTransitions()
        self.avChoice.exit()
        self.avChoice = None

    def enterCreateAvatar(self, index):
        if self.avChoice:
            self.exitChooseAvatar()
        self.avCreate = MakeAToon.MakeAToon('MakeAToon-done', index, 1)
        self.avCreate.load()
        self.avCreate.enter()

    def exitCreateAvatar(self, tutorialFlag=0):
        base.transitions.noTransitions()
        self.avCreate = None
        if tutorialFlag:
            self.playGame.enterTutorial()
            self.setupLocalAvatar(tutorialFlag=tutorialFlag)
            NametagGlobals.setMasterArrowsOn(1)
            self.playingGame = 1
        else:
            self.enterTheTooniverse(FunnyFarmGlobals.FunnyFarm)

    def setupLocalAvatar(self, tutorialFlag=0):
        base.localAvatar.reparentTo(render)
        base.localAvatar.setupControls()
        base.localAvatar.setupSmartCamera()
        base.localAvatar.initInterface()
        base.localAvatar.useLOD(1000)
        base.localAvatar.startBlink()
        if not tutorialFlag:
            base.localAvatar.book.showButton()
            base.localAvatar.laffMeter.start()
            base.localAvatar.startChat()
        base.localAvatar.disable()

    def teleportTo(self, zoneId):
        base.localAvatar.enterTeleportOut(callback=self.__handleTeleport, extraArgs=[zoneId])

    def __handleTeleport(self, zoneId):
        base.localAvatar.exitTeleportOut()
        if self.playGame.hood and zoneId == self.playGame.hood.zoneId:
            if self.playGame.hood.place:
                # Teleporting to the playground from a local shop
                self.playGame.hood.exitPlace()
                base.transitions.irisIn()
                self.playGame.hood.enter()
            else:
                # Teleporting to the same playground you're currently in (via the map)
                base.transitions.irisIn()
                base.localAvatar.setRandomSpawn(zoneId)
                base.localAvatar.enterTeleportIn(callback=self.playGame.hood.handleEntered)
        else:
            self.playGame.exitActiveZone()
            if base.secretAreaFlag:
                secretAreaFlag = random.randint(0, 9)
                if not secretAreaFlag:
                    base.secretAreaFlag = 0
                    self.playGame.enterSecretArea()
                else:
                    self.playGame.enterHood(zoneId)
            else:
                self.playGame.enterHood(zoneId)

    def enterTheTooniverse(self, zoneId):
        base.transitions.noTransitions()
        self.playGame.enterHood(zoneId, init=1)
        self.setupLocalAvatar()
        NametagGlobals.setMasterArrowsOn(1)
        self.playingGame = 1

    def exitTheTooniverse(self):
        base.localAvatar.enterTeleportOut(callback=self.__handleExit)

    def __handleExit(self):
        self.cleanupGame()
        musicMgr.playPickAToon()
        self.enterChooseAvatar()

    def cleanupGame(self):
        self.playGame.exitActiveZone()
        camera.reparentTo(render)
        # If we're in the tutorial, don't even bother cleaning up localAvatar; too many errors
        if base.localAvatar.tutorialAck:
            base.localAvatar.delete()
            base.localAvatar = None
        NametagGlobals.setMasterArrowsOn(0)
        self.playingGame = 0

    def shutdown(self, errorCode = None):
        if self.playingGame:
            self.cleanupGame()
        self.notify.info('Exiting cleanly')
        base.exitShow(errorCode)

    def isPaid(self):
        return True
