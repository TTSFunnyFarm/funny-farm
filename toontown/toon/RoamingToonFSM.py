from direct.fsm.FSM import FSM
from panda3d.core import *
from direct.interval.IntervalGlobal import *

class RoamingToonFSM(FSM):
    def __init__(self, id, toon):
        self.toon = toon
        self.track = None
        FSM.__init__(self, str(id) + '-fsm')

    def enterStandingAround(self):
        self.toon.enterNeutral()

    def exitStandingAround(self):
        self.toon.exitNeutral()

    def enterReadingBook(self):
        if self.track:
            self.track.finish()
        self.track = Sequence(Func(self.toon.enterOpenBook), Wait(0.4), Func(self.toon.enterReadBook))
        self.track.start()

    def exitReadingBook(self):
        if self.track:
            self.track.finish()
        self.track = Sequence(Func(self.toon.enterCloseBook), Wait(1.595), Func(self.toon.enterNeutral))
        self.track.start()

    def enterRunning(self):
        self.toon.loop('run')

    def exitRunning(self):
        return

    def enterWalking(self):
        self.toon.loop('walk')

    def exitWalking(self):
        return
