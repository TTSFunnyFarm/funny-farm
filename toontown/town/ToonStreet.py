from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.hood import ToonHood

class ToonStreet(ToonHood.ToonHood):
    notify = directNotify.newCategory('ToonStreet')

    def __init__(self):
        ToonHood.ToonHood.__init__(self)

    def enter(self, shop=None, tunnel=None):
        base.localAvatar.setZoneId(self.zoneId)
        musicMgr.playCurrentZoneMusic()
        if shop:
            return
        self.spawnTitleText()

    def exit(self):
        ToonHood.ToonHood.exit(self)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.geom.flattenStrong()

    def unload(self):
        ToonHood.ToonHood.unload(self)
