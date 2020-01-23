from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase import Audio3DManager
from toontown.hood import SkyUtil
from toontown.shader import WaterShader
from toontown.toon import NPCToons
from toontown.toonbase import FunnyFarmGlobals
from toontown.town.Street import Street

class FFStreet(Street):

    def __init__(self, zoneId):
        Street.__init__(self)
        self.zoneId = zoneId
        self.hoodFile = 'phase_14/models/streets/funny_farm_%d' % zoneId
        self.spookyHoodFile = '%s_halloween' % self.hoodFile
        self.winterHoodFile = '%s_winter' % self.hoodFile
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.waterShader = None

    def enter(self, shop=None, tunnel=None):
        self.loadQuestChanges()
        Street.enter(self, shop=shop, tunnel=tunnel)
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.trainSfx.play()
            self.audio3d.attachSoundToObject(self.trainSfx, self.train)
            self.waterShader.waterPos = -1.5
            self.waterShader.start('water', self.geom, self.sky)

    def exit(self):
        Street.exit(self)
        self.unloadQuestChanges()
        self.waterShader.stop()
        self.waterShader.waterPos = 0
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.audio3d.detachSound(self.trainSfx)
            self.trainSfx.stop()

    def load(self):
        Street.load(self)
        self.waterShader = WaterShader.WaterShader()
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.loadTrain()

    def unload(self):
        Street.unload(self)
        self.waterShader = None
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.unloadTrain()

    def startActive(self):
        Street.startActive(self)
        if self.zoneId == FunnyFarmGlobals.RicketyRoad:
            self.accept('entertrain_collision', self.__handleTrainCollision)
            self.ignore('entertunnel_trigger_ss_2100') # temporary

    def loadQuestChanges(self):
        for questDesc in base.localAvatar.quests:
            if questDesc[0] in range(1019, 1023):
                self.npcs.append(NPCToons.createLocalNPC(1114, True))
                origin = self.geom.find('**/npc_origin_1')
                origin.setPosHpr(-97.042, 133.081, 0.025, 171, 0 , 0)
                self.npcs[1].reparentTo(self.geom)
                self.npcs[1].setPosHpr(origin, 0, 0, 0, 0, 0, 0)
                self.npcs[1].origin = origin
                self.npcs[1].initializeBodyCollisions('toon')
                self.npcs[1].addActive()
                continue
            if questDesc[0] in [1028, 1029] and questDesc[1] != 1:
                bldg = base.air.suitPlanners[self.zoneId].buildingMap[18]
                if bldg.mode == 'toon':
                    messenger.send('spawnBuilding-%d' % self.zoneId, [18])

    def unloadQuestChanges(self):
        if len(self.npcs) > 1:
            self.npcs[1].delete()
            del self.npcs[1]

    def loadTrain(self):
        self.train = loader.loadModel('phase_5/models/props/train')
        self.train.reparentTo(self.geom)
        cb = CollisionBox(Point3(0, 14.25, 5), 3.5, 14.25, 6)
        self.trainColl = self.train.attachNewNode(CollisionNode('train_collision'))
        self.trainColl.node().addSolid(cb)
        self.train.setH(90)
        self.trainLoop = Sequence(self.train.posInterval(32, pos=Point3(445, 45, -0.5), startPos=(-260, 45, -0.5)), Wait(90))
        self.trainLoop.loop()
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
        self.trainSfx = self.audio3d.loadSfx('phase_14/audio/sfx/train_loop.ogg')
        self.trainSfx.setLoop(True)
        self.audio3d.setDropOffFactor(0.04)

    def unloadTrain(self):
        self.trainLoop.finish()
        self.train.removeNode()
        self.audio3d.disable()
        del self.train
        del self.trainColl
        del self.trainLoop
        del self.trainSfx
        del self.audio3d

    def __handleTrainCollision(self, entry):
        if base.localAvatar.getInBattle():
            return
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
