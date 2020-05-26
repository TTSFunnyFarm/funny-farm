from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownTimer
from panda3d.core import *
from . import BattleFSM
class BattleManager(DirectObject):
    def __init__(self, toons=[], cogs=[]):
        self.toons = toons
        self.cogs = cogs
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.posInTopRightCorner()
        self.timer.setTime(30)
        self.timer.countdown(30, print)
        self.fsm = BattleFSM.BattleFSM(self)
