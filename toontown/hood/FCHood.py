from pandac.PandaModules import *
from toontown.toonbase import FunnyFarmGlobals
from ToonHood import ToonHood
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

    def enter(self, shop=None, tunnel=None, init=False):
        musicMgr.startFCSZ()
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)
        if tunnel:
            if tunnel == 'rr':
                tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
            #elif tunnel == 'rr':
                #tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
            elif tunnel == 'ww':
                tunnelOrigin = self.geom.find('**/WWTunnel').find('**/tunnel_origin')
            base.localAvatar.tunnelIn(tunnelOrigin)
        if base.air.holidayMgr.isWinter():
            self.snow.start(camera, self.snowRender)
        self.startActive()

    def exit(self):
        musicMgr.stopFCSZ()
        ToonHood.exit(self)
        if base.air.holidayMgr.isWinter():
            self.snow.cleanup()

    def load(self):
        ToonHood.load(self)
        self.sky.setScale(1.5)
        if not base.air.holidayMgr.isWinter() and not base.air.holidayMgr.isHalloween():
            self.startSkyTrack()
        if base.air.holidayMgr.isWinter():
            self.snow = BattleParticles.loadParticleFile('snowdisk.ptf')
            self.snow.setPos(0, 0, 5)
            self.snowRender = render.attachNewNode('snowRender')
            self.snowRender.setDepthWrite(0)
            self.snowRender.setBin('fixed', 1)

    def unload(self):
        if not base.air.holidayMgr.isWinter() and not base.air.holidayMgr.isHalloween():
            self.stopSkyTrack()
        ToonHood.unload(self)

    def startActive(self):
        self.acceptOnce('enterRRTunnel_trigger', self.__handleRRTunnel)
        self.acceptOnce('enterWWTunnel_trigger', self.__handleWWTunnel)

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
