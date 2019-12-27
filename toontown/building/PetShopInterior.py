from panda3d.core import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.hood import ZoneUtil
from toontown.building.Interior import Interior
from toontown.building import ToonInteriorColors
from toontown.building import InteriorStorage
import random

class PetShopInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)
        self.interiorFile = 'phase_4/models/modules/PetShopInterior'

    def replaceRandomInModel(self, model):
        baseTag = 'random_'
        npc = model.findAllMatches('**/' + baseTag + '???_*')
        for i in range(npc.getNumPaths()):
            np = npc.getPath(i)
            name = np.getName()
            b = len(baseTag)
            category = name[b + 4:]
            key1 = name[b]
            key2 = name[b + 1]
            if key1 == 'm':
                model = InteriorStorage.findNode(category)
                model.reparentTo(np)
                if key2 == 'r':
                    self.replaceRandomInModel(model)
            elif key1 == 't':
                texture = InteriorStorage.findTexture(category, self.zoneId)
                np.setTexture(texture, 100)
                newNP = np
                if key2 == 'c':
                    colorIndex = InteriorStorage.ZoneStyles[self.zoneId][category][1]
                    newNP.setColorScale(self.colors[category][colorIndex])

    def load(self):
        Interior.load(self)
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.generateFish()
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        doorOrigin = self.interior.find('**/door_origin')
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.25, 0)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        doorColor = 0
        if self.zoneId in InteriorStorage.ZoneStyles:
            doorColor = InteriorStorage.ZoneStyles[self.zoneId].get('TI_door', 0)
        self.door.setColor(self.colors['TI_door'][doorColor])
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()
        self.acceptOnce('avatarExitDone', self.startActive)

    def unload(self):
        self.bearSwim.finish()
        del self.bearSwim
        for fish in self.fish:
            fish.stop()
            fish.cleanup()
            fish.removeNode()
            del fish
        del self.fish
        Interior.unload(self)

    def generateFish(self):
        self.fish = []
        for fishName in FunnyFarmGlobals.PetShopFish:
            fish = Actor('phase_4/models/char/' + fishName + '-zero.bam',
                                    {'swim':'phase_4/models/char/' + fishName + '-swim.bam'})
            fish.reparentTo(render)
            fish.setPos(FunnyFarmGlobals.PetShopFishPositions[FunnyFarmGlobals.PetShopFish.index(fishName)])
            fish.setHpr(FunnyFarmGlobals.PetShopFishRotations[FunnyFarmGlobals.PetShopFish.index(fishName)])
            fish.setScale(FunnyFarmGlobals.PetShopFishScales[FunnyFarmGlobals.PetShopFish.index(fishName)])
            if config.GetBool('smooth-animations', True):
                fish.setBlend(frameBlend=True)
            fish.actorInterval('swim').loop()
            if fishName == 'BearAcuda':
                self.bearSwim = Parallel(
                        Sequence(
                                fish.posInterval(5, FunnyFarmGlobals.PetShopBearSwimPoints[0], blendType='easeInOut'),
                                fish.posInterval(5, FunnyFarmGlobals.PetShopBearSwimPoints[1], blendType='easeInOut'),
                                fish.posInterval(5, FunnyFarmGlobals.PetShopBearSwimPoints[2], blendType='easeInOut'),
                                fish.posInterval(5, FunnyFarmGlobals.PetShopBearSwimPoints[3], blendType='easeInOut')
                        ),
                        fish.hprInterval(20, Vec3(-270, 0, 0))
                )
                self.bearSwim.loop()
            self.fish.append(fish)
        return
