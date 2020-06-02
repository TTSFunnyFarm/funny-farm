from direct.fsm.FSM import FSM
from .CMenuContainer import *
class BattleFSM(FSM):
    def __init__(self, battle):
        self.battle = battle
        FSM.__init__(self, 'BattleFSM')

    def enterToonChoice(self):
        battle = self.battle
        timer = battle.timer
        timer.show()
        timer.setTime(45)
        timer.countdown(45, battle._timerExpired)
        battle.CMenu.show()
        battle.CMenu.showNode(CMENU)

    def exitToonChoice(self):
        battle = self.battle
        timer = battle.timer
        timer.stop()
        timer.hide()
        battle.CMenu.hide()
