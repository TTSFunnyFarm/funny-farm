from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.login.PickAToon import PickAToon
from toontown.toontowngui import TTDialog
from toontown.toonbase import FunnyFarmGlobals
from otp.otpbase import OTPLocalizer
from toontown.login import Login
import random
import PlayGame
import os
import sys

class FFClientRepository(DirectObject):
    notify = directNotify.newCategory('ClientRepository')
    notify.setInfo(True)

    def __init__(self):
        self.login = None
        self.avChooser = None
        self.playGame = PlayGame.PlayGame()

    def enterLogin(self):
        self.login = Login.Login()
        self.login.load()
        self.login.enter()

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

    def enterHood(self, zoneId):
        if zoneId == FunnyFarmGlobals.FunnyFarm:
            self.playGame.enterFFHood()
        elif zoneId == FunnyFarmGlobals.FunnyFarmCentral:
            self.playGame.enterFCHood()
        elif zoneId == FunnyFarmGlobals.SillySprings:
            self.playGame.enterSSHood()
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
        Sequence(Wait(3.2), Func(base.localAvatar.hide)).start()

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
        self.enterHood(zoneId)
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
        Sequence(Wait(3.2), Func(base.localAvatar.hide)).start()

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
        soundMgr.startPAT()
        self.enterPAT()

    def isPaid(self):
        return True
