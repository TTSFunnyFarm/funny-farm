from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase import Audio3DManager
from toontown.hood import SkyUtil
from toontown.shader import WaterShader
from toontown.toon import NPCToons
from toontown.toonbase import FunnyFarmGlobals
from toontown.town.Street import Street
from toontown.battle import BattleParticles
from toontown.battle import BattleSounds
from toontown.battle import MovieUtil

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
        elif self.zoneId == FunnyFarmGlobals.BarnyardBoulevard:
            self.ignore('entertunnel_trigger_mm_4100') # temporary

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
        cs1 = CollisionSphere(0, 3, 3, 4)
        cs2 = CollisionSphere(0, 10, 3, 4)
        cs3 = CollisionSphere(0, 17, 3, 4)
        cs4 = CollisionSphere(0, 24, 3, 4)
        self.trainColl = self.train.attachNewNode(CollisionNode('train_collision'))
        self.trainColl.node().addSolid(cs1)
        self.trainColl.node().addSolid(cs2)
        self.trainColl.node().addSolid(cs3)
        self.trainColl.node().addSolid(cs4)
        self.train.setH(90)
        
        self.trainLoop = Sequence(self.train.posInterval(35, pos=Point3(445, 45, -0.5), startPos=(-260, 45, -0.5)), Wait(90))
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

    def __handleTrainCollision(self, collEntry):
        np = collEntry.getFromNodePath()
        if np.getName() == 'cRay':
            self.__trainHitCog(collEntry)
        else:
            self.__trainHitToon(collEntry)

    def __trainHitToon(self, collEntry):
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

    def __trainHitCog(self, collEntry):
        suitNP = collEntry.getFromNodePath().getParent()
        suitNP = suitNP.find('**/suit-*')
        if suitNP.isEmpty():
            # AI most likely gave us a bad suit if this is the case.
            return 
        doId = int(suitNP.getName().split('-')[1])
        if doId not in self.sp.activeSuits.keys():
            # Most likely got hit during the face-off of a battle.
            return
        suit = self.sp.activeSuits[doId]
        suit.enableRaycast(0)
        suit.exitWalk()
        suit.setZ(-0.4)
        base.air.suitPlanners[self.zoneId].removeSuitAI(doId)
        
        suitTrack = Sequence()
        suitSfx = BattleSounds.globalBattleSoundCache.getSound('TL_train_cog.ogg')
        suitReact = ActorInterval(suit, 'flatten')
        suitDeath = self.getSuitDeathTrack(suit)
        suitTrack.append(Func(base.playSfx, suitSfx, 0, 1, None, 0.0, suitNP))
        suitTrack.append(suitReact)
        suitTrack.append(suitDeath)
        suitTrack.append(Func(self.sp.deleteSuit, suit))
        suitTrack.append(Func(messenger.send, 'upkeepPopulation-%d' % self.zoneId, [None]))
        suitTrack.start()

    def getSuitDeathTrack(self, suit):
        suitTrack = Sequence()
        suitPos = suit.getPos()
        suitHpr = suit.getHpr()
        deathSuit = suit.getLoseActor()
        suitTrack.append(Func(MovieUtil.insertDeathSuit, suit, deathSuit, self.geom, suitPos, suitHpr))
        suitTrack.append(ActorInterval(deathSuit, 'lose', duration=6.0))
        suitTrack.append(Func(MovieUtil.removeDeathSuit, suit, deathSuit, name='remove-death-suit'))
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        deathSoundTrack = Sequence(Wait(0.8), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2), SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8), SoundInterval(deathSound, volume=0.32))
        BattleParticles.loadParticles()
        smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
        singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
        smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
        bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
        gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
        smallGears.setPos(gearPoint)
        singleGear.setPos(gearPoint)
        smallGears.setDepthWrite(False)
        singleGear.setDepthWrite(False)
        smallGearExplosion.setPos(gearPoint)
        bigGearExplosion.setPos(gearPoint)
        smallGearExplosion.setDepthWrite(False)
        bigGearExplosion.setDepthWrite(False)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(5.4))
        explosionTrack.append(MovieUtil.createKapowExplosionTrack(self.geom, explosionPoint=gearPoint))
        gears1Track = Sequence(Wait(2.1), ParticleInterval(smallGears, self.geom, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
        gears2MTrack = Track((0.0, explosionTrack), (0.7, ParticleInterval(singleGear, self.geom, worldRelative=0, duration=5.7, cleanup=True)), (5.2, ParticleInterval(smallGearExplosion, self.geom, worldRelative=0, duration=1.2, cleanup=True)), (5.4, ParticleInterval(bigGearExplosion, self.geom, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')
        return Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack)

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)
