from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase import Audio3DManager
from toontown.toonbase import FunnyFarmGlobals
from toontown.hood import SkyUtil
from Street import Street

class FFStreet(Street):

    def __init__(self, zoneId):
        Street.__init__(self)
        self.zoneId = zoneId
        self.hoodFile = 'phase_14/models/streets/funny_farm_%d' % zoneId
        self.spookyHoodFile = '%s_halloween' % self.hoodFile
        self.winterHoodFile = '%s_winter' % self.hoodFile
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (1.0, 0.5, 0.4, 1.0)

    def enter(self, shop=None, tunnel=None):
        Street.enter(self, shop=shop, tunnel=tunnel)
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.train.unstash()
            self.trainSfx.play()
            self.audio3d.attachSoundToObject(self.trainSfx, self.train)

    def exit(self):
        Street.exit(self)
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.train.stash()
            self.audio3d.detachSound(self.trainSfx)
            self.trainSfx.stop()

    def load(self):
        Street.load(self)
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.loadTrain()

    def unload(self):
        Street.unload(self)
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.unloadTrain()

    def loadTrain(self):
        self.train = loader.loadModel('phase_5/models/props/train')
        self.train.reparentTo(render)
        cb = CollisionBox(Point3(0, 14.25, 5), 3.5, 14.25, 6)
        self.trainColl = self.train.attachNewNode(CollisionNode('train_collision'))
        self.trainColl.node().addSolid(cb)
        self.train.setH(90)
        self.trainLoop = Sequence(self.train.posInterval(32, pos=Point3(445, 45, -0.5), startPos=(-260, 45, -0.5)), Wait(10))
        self.trainLoop.loop()
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
        self.trainSfx = self.audio3d.loadSfx('phase_14/audio/sfx/train_loop.ogg')
        self.trainSfx.setLoop(True)
        self.audio3d.setDropOffFactor(0.04)
        self.train.stash()

    def unloadTrain(self):
        self.trainLoop.finish()
        self.train.removeNode()
        self.audio3d.disable()
        del self.train
        del self.trainColl
        del self.trainLoop
        del self.trainSfx
        del self.audio3d

    def startActive(self):
        Street.startActive(self)
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.accept('entertrain_collision', self.__handleTrainCollision)

    def __handleTrainCollision(self, entry):
        base.localAvatar.disable()
        base.localAvatar.setAnimState('neutral')
        animalType = base.localAvatar.getStyle().getType()
        dialogue = base.loader.loadSfx('phase_3.5/audio/dial/AV_%s_exclaim.ogg' % animalType)
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
