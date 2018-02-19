from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.shader import WaterShader
from toontown.battle import BattleParticles
from toontown.suit.BattleSuit import BattleSuit
from toontown.suit.SuitDNA import SuitDNA
from toontown.toon import NPCToons
from ToonHood import ToonHood
import SkyUtil

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
        self.waterShader = None

    def enter(self, shop=None, tunnel=None, init=0):
        self.loadQuestChanges()
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)
        self.waterShader.start('water', self.geom, self.sky)
        if hasattr(self, 'snow'):
            self.snow.start(camera, self.snowRender)

    def exit(self):
        ToonHood.exit(self)
        self.unloadQuestChanges()
        self.waterShader.stop()
        if hasattr(self, 'snow'):
            self.snow.disable()

    def load(self):
        ToonHood.load(self)
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
                if not hasattr(self, 'suit'):
                    dna = SuitDNA()
                    dna.newSuit('tbc')
                    self.suit = BattleSuit()
                    self.suit.setDNA(dna)
                    self.suit.setLevel(4)
                    self.suit.setElite(1)
                    self.suit.initializeBodyCollisions('suit')
                    self.suit.reparentTo(self.geom)
                    self.suit.setPosHpr(-90, -20, 0, 270, 0, 0)
                    self.suit.addActive()
                    self.suit.loop('neutral')
                if not hasattr(self, 'flippy'):
                    self.flippy = NPCToons.createLocalNPC(1001, functional=True)
                    self.flippy.initializeBodyCollisions('toon')
                    self.flippy.reparentTo(self.geom)
                    self.flippy.setPosHpr(-70, -20, 0, 90, 0, 0)
                    self.flippy.useLOD(1000)
                    self.flippy.addActive()
                    self.flippy.stopLookAround()
                return

    def unloadQuestChanges(self):
        if hasattr(self, 'suit'):
            self.suit.delete()
            del self.suit
        if hasattr(self, 'flippy'):
            self.flippy.delete()
            del self.flippy
