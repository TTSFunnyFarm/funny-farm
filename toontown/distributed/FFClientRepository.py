from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.login import AvatarChooser
from toontown.makeatoon import MakeAToon
from toontown.toontowngui import TTDialog
from toontown.toonbase import TTLocalizer
from toontown.toonbase import FunnyFarmGlobals
from otp.otpbase import OTPLocalizer
import random
import PlayGame
import os
import sys

class FFClientRepository(DirectObject):
    notify = directNotify.newCategory('ClientRepository')
    notify.setInfo(True)
    AI_TIMEOUT = 15

    def __init__(self):
        self.avChoice = None
        self.avCreate = None
        self.playGame = PlayGame.PlayGame()
        self.playingGame = 0
        self.waitDialog = None

    def begin(self):
        if not base.air.isLoaded:
            # We'll probably never get here, but just in case the AI is taking extra long, we'll have them wait.
            # In the future, as we build up our AI more and more, there's a chance we'll get here.
            self.waitDialog = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.NoButtons, text=OTPLocalizer.AIPleaseWait)
            self.waitDialog.show()
            self.accept('ai-done', self.enterChooseAvatar)
            taskMgr.doMethodLater(self.AI_TIMEOUT, self.aiTimeout, 'aiTimeout')
        else:
            self.enterChooseAvatar()

    def aiTimeout(self, task):
        # Even more unlikely that we'll get here, but better safe than sorry!
        self.ignore('ai-done')
        base.handleGameError('AI services could not be started.')
        return task.done

    def enterChooseAvatar(self):
        if self.waitDialog:
            self.waitDialog.destroy()
            del self.waitDialog
            self.ignore('ai-done')
        base.transitions.noTransitions()
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
        else:
            self.enterTheTooniverse(FunnyFarmGlobals.FunnyFarm)

    def enterHood(self, zoneId, init=0):
        if zoneId == FunnyFarmGlobals.FunnyFarm:
            self.playGame.enterFFHood(init=init)
        elif zoneId == FunnyFarmGlobals.FunnyFarmCentral:
            self.playGame.enterFCHood(init=init)
        elif zoneId == FunnyFarmGlobals.SillySprings:
            self.playGame.enterSSHood(init=init)
        elif zoneId == FunnyFarmGlobals.SecretArea:
            self.playGame.enterSecretArea()
        else:
            self.playGame.notify.warning('zoneId ' + str(zoneId) + ' does not exist. Going to Funny Farm..')
            self.playGame.enterFFHood()

    def teleportTo(self, zoneId):
        if base.secretAreaFlag:
            secretAreaFlag = random.randint(0, 9)
            if not secretAreaFlag:
                zoneId = FunnyFarmGlobals.SecretArea
                base.secretAreaFlag = 0
        base.localAvatar.enterTeleportOut(callback=self.__handleTeleport, extraArgs=[zoneId])

    def __handleTeleport(self, zoneId):
        base.localAvatar.exitTeleportOut()
        if self.playGame.hood:
            self.playGame.exitHood()
        elif self.playGame.street:
            self.playGame.exitStreet()
        elif self.playGame.place:
            self.playGame.exitPlace()
        self.enterHood(zoneId)

    def enterTheTooniverse(self, zoneId):
        base.transitions.noTransitions()
        self.enterHood(zoneId, init=1)
        self.setupLocalAvatar()
        self.playingGame = 1

    def exitTheTooniverse(self):
        base.localAvatar.enterTeleportOut(callback=self.__handleExit)

    def __handleExit(self):
        self.cleanupGame()
        musicMgr.playPickAToon()
        self.enterChooseAvatar()

    def setupLocalAvatar(self, tutorialFlag=0):
        base.localAvatar.reparentTo(render)
        base.localAvatar.setupControls()
        base.localAvatar.setupSmartCamera()
        base.localAvatar.initInterface()
        base.localAvatar.useLOD(1000)
        base.localAvatar.addActive()
        base.localAvatar.startBlink()
        if not tutorialFlag:
            base.localAvatar.book.showButton()
            base.localAvatar.laffMeter.start()
            base.localAvatar.startChat()
        base.localAvatar.disable()

    def cleanupGame(self):
        if self.playGame.hood:
            self.playGame.exitHood()
        elif self.playGame.street:
            self.playGame.exitStreet()
        elif self.playGame.place:
            self.playGame.exitPlace()
        camera.reparentTo(render)
        base.localAvatar.delete()
        base.localAvatar = None
        self.playingGame = 0

    def shutdown(self, errorCode = None):
        if self.playingGame:
            self.cleanupGame()
        self.notify.info('Exiting cleanly')
        base.exitShow(errorCode)

    def isPaid(self):
        return True
