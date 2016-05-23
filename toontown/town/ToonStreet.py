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
        if shop:
            return
        base.localAvatar.setZoneId(self.zoneId)
        self.title = OnscreenText(self.titleText, fg=self.titleColor, font=ToontownGlobals.getSignFont(), pos=(0, -0.5), scale=TTLocalizer.HtitleText, drawOrder=0, mayChange=1)
        self.spawnTitleText()

    def exit(self):
        ToonHood.ToonHood.exit(self)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.geom.flattenStrong()

    def unload(self):
        ToonHood.ToonHood.unload(self)
