from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownTimer
from panda3d.core import *
from . import BattleFSM, GagMenu, AttackMenu
class BattleManager(DirectObject):
    def __init__(self, toons=[], cogs=[]):
        self.toons = toons
        self.cogs = cogs
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.posInTopRightCorner()
        self.timer.hide()
        self.gagMenu = GagMenu.GagMenu()
        self.gagMenu.hide()
        self.attackMenu = AttackMenu.AttackMenu()
        for cog in self.cogs:
            cog.enterBattle()
        self.fsm = BattleFSM.BattleFSM(self)
        self.fsm.request('ToonChoice')

    def _timerExpired(self):
        self.timer.stop()
        self.timer.hide()
        if self.fsm.state == 'ToonChoice':
            self.fsm.request('ToonAttack')
