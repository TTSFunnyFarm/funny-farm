from pandac.PandaModules import *
from toontown.hood import ZoneUtil
from Interior import Interior
import ToonInteriorColors
import InteriorStorage
import random

class GagShopInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)
        self.interiorFile = 'phase_4/models/modules/gagShop_interior'

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
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        doorOrigin = self.interior.find('**/door_origin')
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        if self.zoneId in InteriorStorage.ZoneStyles:
            doorColor = InteriorStorage.ZoneStyles[self.zoneId].get('TI_door', 0)
        else:
            doorColor = 0
        self.door.setColor(self.colors['TI_door'][doorColor])
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()
        self.acceptOnce('avatarExitDone', self.startActive)

    def unload(self):
        Interior.unload(self)
