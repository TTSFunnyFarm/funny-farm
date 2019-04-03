from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.hood.ToonHood import ToonHood
from toontown.hood import SkyUtil

class SSHood(ToonHood):

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.SillySprings
        self.TTZoneId = ToontownGlobals.DaisyGardens
        self.hoodFile = 'phase_14/models/neighborhoods/silly_springs'
        self.spookyHoodFile = 'phase_14/models/neighborhoods/silly_springs_halloween'
        self.winterHoodFile = 'phase_14/models/neighborhoods/silly_springs_winter'
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (0.8, 0.6, 1.0, 1.0)

    def enter(self, shop=None, tunnel=None, init=0):
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)

    def exit(self):
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)

    def unload(self):
        ToonHood.unload(self)

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)
