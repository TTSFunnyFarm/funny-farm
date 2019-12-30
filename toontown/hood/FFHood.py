import random

from panda3d.core import *

from toontown.battle import BattleParticles
from toontown.hood import SkyUtil
from toontown.hood.ToonHood import ToonHood
from toontown.shader import WaterShader
from toontown.suit.BattleSuit import BattleSuit
from toontown.suit.SuitDNA import SuitDNA
from toontown.toon import NPCToons
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals
from toontown.safezone.FFTreasurePlanner import FFTreasurePlanner


class FFHood(ToonHood):

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.FunnyFarm
        self.TTZoneId = ToontownGlobals.ToontownCentral
        self.hoodFile = 'phase_14/models/neighborhoods/funny_farm'
        self.spookyHoodFile = 'phase_14/models/neighborhoods/funny_farm_halloween'
        self.winterHoodFile = 'phase_14/models/neighborhoods/funny_farm_winter'
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.birdSound = list(map(base.loader.loadSfx, ['phase_4/audio/sfx/SZ_TC_bird1.ogg', 'phase_4/audio/sfx/SZ_TC_bird2.ogg', 'phase_4/audio/sfx/SZ_TC_bird3.ogg']))
        self.waterShader = None
        self.treasurePlanner = FFTreasurePlanner()

    def enter(self, shop=None, tunnel=None, init=0):
        self.loadQuestChanges()
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)
        taskMgr.doMethodLater(1, self.doBirds, 'FF-birds')
        self.waterShader.start('water', self.geom, self.sky)
        if hasattr(self, 'snow'):
            self.snow.start(camera, self.snowRender)

    def exit(self):
        ToonHood.exit(self)
        taskMgr.remove('FF-birds')
        self.unloadQuestChanges()
        self.waterShader.stop()
        if hasattr(self, 'snow'):
            self.snow.disable()

    def load(self):
        ToonHood.load(self)
        self.sky.setScale(2.0)
        self.waterShader = WaterShader.WaterShader()
        self.waterShader.waterPos = 1.05
        if base.air.holidayMgr.isWinter():
            self.snow = BattleParticles.loadParticleFile('snowdisk.ptf')
            self.snow.setPos(0, 0, 5)
            self.snowRender = render.attachNewNode('snowRender')
            self.snowRender.setDepthWrite(0)
            self.snowRender.setBin('fixed', 1)

    def unload(self):
        ToonHood.unload(self)
        self.waterShader.stop()
        self.waterShader = None
        if hasattr(self, 'snow'):
            self.snow.cleanup()
            self.snowRender.removeNode()
            del self.snow
            del self.snowRender

    def startActive(self):
        ToonHood.startActive(self)
        self.ignore('entertunnel_trigger_ff_1200')

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)

    def loadQuestChanges(self):
        for questDesc in base.localAvatar.quests:
            if questDesc[0] == 1002 and questDesc[1] == 0:
                if not self.actors.get('suit'):
                    dna = SuitDNA()
                    dna.newSuit('tbc')
                    actor = self.actors['suit'] = BattleSuit()
                    actor.setDNA(dna)
                    actor.setLevel(4)
                    actor.setElite(1)
                    actor.initializeBodyCollisions('suit')
                    actor.reparentTo(self.geom)
                    actor.setPosHpr(-70, -20, 0, 270, 0, 0)
                    actor.addActive()
                    actor.loop('neutral')
                if not self.actors.get('flippy'):
                    actor = self.actors['flippy'] = NPCToons.createLocalNPC(1001, functional=True)
                    actor.initializeBodyCollisions('toon')
                    actor.reparentTo(self.geom)
                    actor.setPosHpr(-50, -20, 0, 90, 0, 0)
                    actor.setScale(1, 1, 1)
                    actor.useLOD(1000)
                    actor.addActive()
                    actor.stopLookAround()
                return

    def doBirds(self, task):
        base.playSfx(random.choice(self.birdSound))
        t = random.random() * 20.0 + 1
        taskMgr.doMethodLater(t, self.doBirds, 'FF-birds')
        return task.done
