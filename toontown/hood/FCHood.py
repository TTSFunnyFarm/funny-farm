from pandac.PandaModules import *
from toontown.toonbase import FunnyFarmGlobals
from ToonHood import ToonHood
from toontown.toonbase import FFTime
from toontown.battle import BattleParticles

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

    def enter(self, shop=None, tunnel=None):
        soundMgr.startFFSZ()
        ToonHood.enter(self, shop=shop, tunnel=tunnel)
        if tunnel:
            if tunnel == 'ff':
                tunnelOrigin = self.geom.find('**/FFTunnel').find('**/tunnel_origin')
                base.localAvatar.tunnelIn(tunnelOrigin)
            elif tunnel == 'rr':
                tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
                base.localAvatar.tunnelIn(tunnelOrigin)
        if FFTime.isWinter():
            self.snow.start(camera, self.snowRender)
        self.startActive()

    def exit(self):
        soundMgr.stopFFSZ()
        ToonHood.exit(self)
        if FFTime.isWinter():
            self.snow.cleanup()

    def load(self):
        ToonHood.load(self)
        self.sky.setScale(1.5)
        if not FFTime.isWinter() and not FFTime.isHalloween():
            self.startSkyTrack()
        if FFTime.isWinter():
            self.snow = BattleParticles.loadParticleFile('snowdisk.ptf')
            self.snow.setPos(0, 0, 5)
            self.snowRender = render.attachNewNode('snowRender')
            self.snowRender.setDepthWrite(0)
            self.snowRender.setBin('fixed', 1)

    def unload(self):
        if not FFTime.isWinter() and not FFTime.isHalloween():
            self.stopSkyTrack()
        ToonHood.unload(self)

    def startActive(self):
        self.acceptOnce('enterFFTunnel_trigger', self.__handleFFTunnel)
        self.acceptOnce('enterRRTunnel_trigger', self.__handleRRTunnel)

    def __handleFFTunnel(self, entry):
        tunnelOrigin = self.geom.find('**/FFTunnel').find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.__handleEnterFF)

    def __handleEnterFF(self):
        base.cr.playGame.exitHood()
        base.cr.playGame.enterFFHood(tunnel='fc')

    def __handleRRTunnel(self, entry):
        tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.__handleEnterRR)

    def __handleEnterRR(self):
        base.cr.playGame.exitHood()
        base.cr.playGame.enterSSStreet(tunnel='fc')
