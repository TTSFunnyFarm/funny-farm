from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.showbase import Audio3DManager
from otp.otpbase import OTPGlobals
from toontown.toonbase import FunnyFarmGlobals
from ToonStreet import ToonStreet
from toontown.hood import SkyUtil

class RRStreet(ToonStreet):

    def __init__(self):
        ToonStreet.__init__(self)
        self.zoneId = FunnyFarmGlobals.RicketyRoad
        self.hoodFile = 'phase_14/models/streets/rickety_road'
        self.spookyHoodFile = 'phase_14/models/streets/rickety_road_halloween'
        self.winterHoodFile = 'phase_14/models/streets/rickety_road_winter'
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleText = FunnyFarmGlobals.RRStreetText
        self.titleColor = (1.0, 0.5, 0.4, 1.0)

    def enter(self, tunnel=None):
        ToonStreet.enter(self, tunnel=tunnel)
        self.trainSfx.play()
        self.audio3d.attachSoundToObject(self.trainSfx, self.train)
        if tunnel:
            if tunnel == 'ff':
                tunnelOrigin = self.geom.find('**/FFTunnel').find('**/tunnel_origin')
            elif tunnel == 'fc':
                tunnelOrigin = self.geom.find('**/FCTunnel').find('**/tunnel_origin')
            base.localAvatar.tunnelIn(tunnelOrigin)
        self.startActive()

    def exit(self):
        ToonStreet.exit(self)

    def load(self):
        ToonStreet.load(self)
        self.geom.find('**/tBlocker1').node().setCollideMask(OTPGlobals.WallBitmask)
        self.geom.find('**/tBlocker2').node().setCollideMask(OTPGlobals.WallBitmask)
        self.train = loader.loadModel('phase_5/models/props/train')
        self.train.reparentTo(render)
        cb = CollisionBox(Point3(0, 14.25, 5), 3.5, 14.25, 6)
        self.trainColl = self.train.attachNewNode(CollisionNode('train_collision'))
        self.trainColl.node().addSolid(cb)
        self.train.setH(90)
        self.trainLoop = Sequence(self.train.posInterval(32, pos=Point3(360, -11.6, 0), startPos=(-345, -11.6, 0)), Wait(5))
        self.trainLoop.loop()
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
        self.trainSfx = self.audio3d.loadSfx('phase_14/audio/sfx/train_loop.ogg')
        self.trainSfx.setLoop(True)
        self.trainSfx.setVolume(5)
        self.audio3d.setDropOffFactor(0.05)

    def unload(self):
        ToonStreet.unload(self)
        self.audio3d.detachSound(self.trainSfx)
        self.trainSfx.stop()
        self.trainLoop.finish()
        self.train.removeNode()
        self.audio3d.disable()
        del self.trainSfx
        del self.trainLoop
        del self.train
        del self.audio3d

    def startActive(self):
        self.acceptOnce('enterFFTunnel_trigger', self.__handleFFTunnel)
        self.acceptOnce('enterFCTunnel_trigger', self.__handleFCTunnel)
        self.accept('entertrain_collision', self.__handleTrainCollision)

    def __handleFFTunnel(self, entry):
        tunnelOrigin = self.geom.find('**/FFTunnel').find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.__handleEnterFF)

    def __handleEnterFF(self):
        base.cr.playGame.exitStreet()
        base.cr.playGame.enterFFHood(tunnel='rr')

    def __handleFCTunnel(self, entry):
        tunnelOrigin = self.geom.find('**/FCTunnel').find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.__handleEnterFC)

    def __handleEnterFC(self):
        base.cr.playGame.exitStreet()
        base.cr.playGame.enterFCHood(tunnel='rr')

    def __handleTrainCollision(self, entry):
        base.localAvatar.disable()
        base.localAvatar.setAnimState('neutral')
        animalType = base.localAvatar.getStyle().getType()
        dialogue = base.loadSfx('phase_3.5/audio/dial/AV_%s_exclaim.ogg' % animalType)
        base.localAvatar.playCurrentDialogue(dialogue, None)
        base.localAvatar.enterSquish(callback=self.__squishDone)

    def __squishDone(self):
        base.localAvatar.exitSquish()
        base.localAvatar.enable()

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)
