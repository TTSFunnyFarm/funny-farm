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

    def __init__(self):
        self.avChoice = None
        self.avCreate = None
        self.playGame = PlayGame.PlayGame()

    def enterChooseAvatar(self):
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
                base.secretAreaFlag = False
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

    def exitTheTooniverse(self):
        base.localAvatar.enterTeleportOut(callback=self.__handleExit)

    def __handleExit(self):
        if self.playGame.hood:
            self.playGame.exitHood()
        elif self.playGame.street:
            self.playGame.exitStreet()
        elif self.playGame.place:
            self.playGame.exitPlace()
        base.localAvatar.delete()
        base.localAvatar = None
        camera.reparentTo(render)
        musicMgr.startPAT()
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

    def isPaid(self):
        return True
