from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.login.PickAToon import PickAToon
from toontown.toontowngui import TTDialog
from toontown.toonbase import FunnyFarmGlobals
from otp.otpbase import OTPLocalizer
from toontown.login import Launcher
import random
import PlayGame
import os
import sys

class FFClientRepository(DirectObject):
    notify = directNotify.newCategory('ClientRepository')
    notify.setInfo(True)

    def __init__(self):
        self.launcher = None
        self.avChooser = None
        self.playGame = PlayGame.PlayGame()

    def enterLogin(self):
        self.launcher = Launcher.Launcher()
        self.launcher.load()
        self.launcher.enter()

    def loadPAT(self):
        self.avChooser = PickAToon()
        self.avChooser.load()

    def enterPAT(self):
        base.transitions.noTransitions()
        if not self.avChooser:
            self.loadPAT()
        self.avChooser.enter()

    def exitPAT(self):
        base.transitions.noTransitions()
        self.avChooser.exit()
        self.avChooser = None

    def finishMAT(self, tutorial):
        if tutorial:
            self.exitPAT()
            self.playGame.enterTutorial()
            base.localAvatar.reparentTo(render)
            base.localAvatar.setupControls()
            base.localAvatar.initInterface()
            base.localAvatar.addActive()
        else:
            self.enterTheTooniverse(FunnyFarmGlobals.FunnyFarm)

    def enterHood(self, zoneId, init=False):
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
            secretAreaFlag = random.randint(0, 100)
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
        self.exitPAT()
        self.enterHood(zoneId, init=True)
        base.localAvatar.reparentTo(render)
        base.localAvatar.setupControls()
        base.localAvatar.setupSmartCamera()
        base.localAvatar.initInterface()
        base.localAvatar.book.showButton()
        base.localAvatar.laffMeter.start()
        base.localAvatar.startChat()
        base.localAvatar.addActive()

    def exitTheTooniverse(self):
        base.localAvatar.enterTeleportOut(callback=self.__handleExit)

    def __handleExit(self):
        if self.playGame.hood:
            self.playGame.exitHood()
        elif self.playGame.street:
            self.playGame.exitStreet()
        elif self.playGame.place:
            self.playGame.exitPlace()
        base.localAvatar.destroy()
        base.localAvatar = None
        camera.reparentTo(render)
        musicMgr.startPAT()
        self.enterPAT()

    def isPaid(self):
        return True
