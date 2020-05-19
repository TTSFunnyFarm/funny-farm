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
from toontown.suit import Suit, SuitDNA
from toontown.battle.BattleCalculator import BattleCalculator
from toontown.battle.BattleBase import *
from toontown.battle.SuitBattleGlobals import *
from toontown.battle import BattleExperienceAI
from toontown.battle import BattleProps
from toontown.battle import BattleParticles
from toontown.battle import Movie
from toontown.battle import MovieUtil
from toontown.battle import BattleFSM
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

    def __init__(self, toons, cogs, maxSuits = 2, bldg = 0, tutorialFlag = 0):
        self.doId = id(self)
        NodePath.__init__(self, 'Battle-%d' % self.doId)
        BattleBase.__init__(self)
        self.notify.setInfo(1)
        self.toons = toons
        self.cogs = cogs
        self.bldg = bldg
        self.tutorialFlag = tutorialFlag
        self.maxSuits = maxSuits
        self.fsm = BattleFSM.BattleFSM(self)
        self.topCog = None

    def enter(self):
        self.notify.info("Entering battle.")
        self.fsm.demand('FaceOff')

    def update(self):
        self.topCog = self.__determineTopCog()

    def cogRequestJoin(self, cog):
        return self.__cogCanJoin(cog)

    def __cogCanJoin(self, cog):
        return False

    def getCogs(self):
        return self.cogs

    def __determineTopCog(self):
        print(self.cogs)
        cogs = self.getCogs()
        cogWeights = []
        for cog in cogs:
            weight = cog.getWeight()
            cogWeights.append(weight)
        return cogs[cogWeights.index(max(cogWeights))]

    def assignRewards(self):
        return
