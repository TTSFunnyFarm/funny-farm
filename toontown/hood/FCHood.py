from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from ToonHood import ToonHood
from toontown.battle import BattleParticles
import SkyUtil

class FCHood(ToonHood):

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.FunnyFarmCentral
        self.hoodFile = 'phase_14/models/neighborhoods/funny_farm_central'
        self.spookyHoodFile = 'phase_14/models/neighborhoods/funny_farm_central_halloween'
        self.winterHoodFile = 'phase_14/models/neighborhoods/funny_farm_central_winter'
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleText = FunnyFarmGlobals.FCHoodText
        self.titleColor = (1.0, 0.5, 0.4, 1.0)

    def enter(self, shop=None, tunnel=None, init=False):
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)
        if tunnel:
            if tunnel == 'rr':
                tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
            #elif tunnel == 'rr':
                #tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
            elif tunnel == 'ww':
                tunnelOrigin = self.geom.find('**/WWTunnel').find('**/tunnel_origin')
            base.localAvatar.tunnelIn(tunnelOrigin)
        self.startActive()

    def exit(self):
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)

    def unload(self):
        ToonHood.unload(self)

    def startActive(self):
        self.acceptOnce('enterRRTunnel_trigger', self.__handleRRTunnel)
        #self.acceptOnce('enterWWTunnel_trigger', self.__handleWWTunnel)

    def __handleRRTunnel(self, entry):
        tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.__handleEnterRR)

    def __handleEnterRR(self):
        base.cr.playGame.exitHood()
        base.cr.playGame.enterRRStreet(tunnel='fc')

    def __handleWWTunnel(self, entry):
        tunnelOrigin = self.geom.find('**/WWTunnel').find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.__handleEnterWW)

    def __handleEnterWW(self):
        base.cr.playGame.exitHood()
        base.cr.playGame.enterWWStreet(tunnel='fc')

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)
