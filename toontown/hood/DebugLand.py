from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.hood.ToonHood import ToonHood
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitDNA
from toontown.suit import BattleSuit

class DebugLand(ToonHood):
    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.DebugLand
        self.hoodFile = 'phase_14/models/debug/thebug_land'
        self.winterHoodFile = 'phase_14/models/debug/thebug_land'
        self.spookyHoodFile = 'phase_14/models/debug/thebug_land'
        self.titleColor = (0.5, 0.5, 0.5, 1.0)

    def startSuitWalkInterval(self):
        self.suitWalk = Sequence(
            Func(self.suit.setHpr, 90, 0, 0),
            self.suit.posInterval(20, self.suitPoints[0]),
            Func(self.suit.setHpr, 0, 0, 0),
            self.suit.posInterval(15, self.suitPoints[1]),
            Func(self.suit.setHpr, 270, 0, 0),
            self.suit.posInterval(20, self.suitPoints[2]),
            Func(self.suit.setHpr, 180, 0, 0),
            self.suit.posInterval(15, self.suitPoints[3])
        )
        self.suitWalk.loop()

    def enter(self, shop=None, tunnel=None, init=0):
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('f')
        self.suit = BattleSuit.BattleSuit()
        self.suit.setDNA(suitDNA)
        self.suit.setLevel(0)
        self.suit.reparentTo(render)
        self.suit.setPos(650, -100, 0.1)
        self.suit.setPosHpr(650, -100, 0.1, 90, 0, 0)
        self.suit.addActive()        
        self.suitPoints = [
            Point3(450, -100, 0.1),                     
            Point3(450, 50, 0.3),
            Point3(650, 50, 0.3),
            Point3(650, -100, 0.1)   
        ]
        self.suit.loop('walk')
        self.startSuitWalkInterval()
    
    def exit(self):
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)

    def unload(self):
        ToonHood.unload(self)
    
    