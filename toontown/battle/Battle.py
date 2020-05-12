from panda3d.core import *
from libotp import *
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from otp.avatar import Emote
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.suit import Suit
from toontown.battle.BattleCalculator import BattleCalculator
from toontown.battle.BattleBase import *
from toontown.battle.SuitBattleGlobals import *
from toontown.battle import BattleExperienceAI
from toontown.battle import BattleProps
from toontown.battle import BattleParticles
from toontown.battle import Movie
from toontown.battle import MovieUtil
import random

class Battle(DirectObject, NodePath, BattleBase):
    notify = directNotify.newCategory('Battle')
    camPos = ToontownBattleGlobals.BattleCamDefaultPos
    camHpr = ToontownBattleGlobals.BattleCamDefaultHpr
    camFov = ToontownBattleGlobals.BattleCamDefaultFov
    camMenuFov = ToontownBattleGlobals.BattleCamMenuFov
    camJoinPos = ToontownBattleGlobals.BattleCamJoinPos
    camJoinHpr = ToontownBattleGlobals.BattleCamJoinHpr
    camFOFov = ToontownBattleGlobals.BattleCamFaceOffFov
    camFOPos = ToontownBattleGlobals.BattleCamFaceOffPos

    def __init__(self, townBattle, toons = [], suits = [], maxSuits = 2, bldg = 0, tutorialFlag = 0):
        self.doId = id(self)
        NodePath.__init__(self, 'Battle-%d' % self.doId)
        BattleBase.__init__(self)
