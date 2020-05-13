from direct.fsm.FSM import FSM
from panda3d.core import *

class BattleFSM(FSM):
    def __init__(self, battle):
        self.battle = battle
        FSM.__init__(self, 'BattleFSM')

    def enterFaceOff(self):
        print(self.battle._determineTopCog())
