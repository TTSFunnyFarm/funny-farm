from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownTimer
from panda3d.core import *
from . import BattleFSM, CMenuContainer
class BattleManager(DirectObject):
    def __init__(self, toons=[], cogs=[]):
        self.fsm = BattleFSM.BattleFSM(self)
        self.toons = toons
        self.cogs = cogs
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.posInTopRightCorner()
        self.timer.hide()
        self.CMenu = CMenuContainer.CMenuContainer(self)
        for cog in self.cogs:
            cog.enterBattle()
        self.fsm.request('ToonChoice')

    def resetTimer(self):
        self.timer.setTime(45)
        self.timer.countdown(45, self.__timerExpired)

    def __timerExpired(self):
        self.timer.stop()
        self.timer.hide()
        if self.fsm.state == 'ToonChoice':
            self.fsm.request('ToonAttack')
