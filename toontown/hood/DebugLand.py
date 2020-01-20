from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.hood.ToonHood import ToonHood
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals

class DebugLand(ToonHood):
    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.DebugLand
        self.hoodFile = 'phase_14/models/debug/thebug_land'
        self.winterHoodFile = 'phase_14/models/debug/thebug_land'
        self.spookyHoodFile = 'phase_14/models/debug/thebug_land'
        self.titleColor = (0.5, 0.5, 0.5, 1.0)

    def enter(self, shop=None, tunnel=None, init=0):
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)

    def exit(self):
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)

    def unload(self):
        ToonHood.unload(self)
