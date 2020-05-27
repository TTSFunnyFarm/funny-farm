from direct.fsm.FSM import FSM
class BattleFSM(FSM):
    def __init__(self, battle):
        self.battle = battle
        FSM.__init__(self, 'BattleFSM')

    def enterToonChoice(self):
        timer = self.battle.timer
        timer.show()
        timer.setTime(45)
        timer.countdown(45, self.battle._timerExpired)
        self.battle.combatMenu.show()

    def exitToonChoice(self):
        timer = self.battle.timer
        timer.stop()
        timer.hide()
        self.battle.cttackMenu.hide()
