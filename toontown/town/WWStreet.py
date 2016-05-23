from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.showbase import Audio3DManager
from otp.otpbase import OTPGlobals
from toontown.toonbase import FunnyFarmGlobals
from ToonStreet import ToonStreet

class WWStreet(ToonStreet):

    def __init__(self):
        ToonStreet.__init__(self)
        self.zoneId = FunnyFarmGlobals.WintryWay
        self.hoodFile = 'phase_14/models/streets/wintry_way'
        self.spookyHoodFile = 'phase_14/models/streets/wintry_way'
        self.winterHoodFile = 'phase_14/models/streets/wintry_way'
        self.skyFile = 'phase_3.5/models/props/BR_sky'
        self.titleText = FunnyFarmGlobals.WWStreetText
        self.titleColor = (0.3, 0.6, 1.0, 1.0)

    def enter(self, tunnel=None):
        musicMgr.startCVSZ()
        ToonStreet.enter(self, tunnel=tunnel)
        if tunnel:
            if tunnel == 'fc':
                tunnelOrigin = self.geom.find('**/FCTunnel').find('**/tunnel_origin')
                base.localAvatar.tunnelIn(tunnelOrigin)
        self.startActive()

    def exit(self):
        musicMgr.stopCVSZ()
        ToonStreet.exit(self)

    def load(self):
        ToonStreet.load(self)

    def unload(self):
        ToonStreet.unload(self)

    def startActive(self):
        self.acceptOnce('enterFCTunnel_trigger', self.__handleFCTunnel)

    def __handleFCTunnel(self, entry):
        tunnelOrigin = self.geom.find('**/FCTunnel').find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.__handleEnterFC)

    def __handleEnterFC(self):
        base.cr.playGame.exitStreet()
        base.cr.playGame.enterFCHood(tunnel='ww')
