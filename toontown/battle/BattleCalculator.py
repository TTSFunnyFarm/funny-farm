from toontown.battle.BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
import random
from toontown.battle import SuitBattleGlobals
from toontown.toon import NPCToons
from toontown.pets import PetTricks
from direct.showbase.PythonUtil import lerp

class BattleCalculator:
    AccuracyBonuses = [0, 20, 40, 60]
    DamageBonuses = [0, 20, 20, 20]
    AttackExpPerTrack = [0, 10, 20, 30, 40, 50, 60]
    NumRoundsLured = [2, 2, 3, 3, 4, 4, 15]
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleCalculator')
    toonsAlwaysHit = config.GetBool('toons-always-hit', 0)
    toonsAlwaysMiss = config.GetBool('toons-always-miss', 0)
    suitsAlwaysHit = config.GetBool('suits-always-hit', 0)
    suitsAlwaysMiss = config.GetBool('suits-always-miss', 0)
    immortalSuits = config.GetBool('immortal-suits', 0)
    propAndOrganicBonusStack = config.GetBool('prop-and-organic-bonus-stack', 0)

    def __init__(self, battle, tutorialFlag = 0):
        self.battle = battle
