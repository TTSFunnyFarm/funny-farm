from panda3d.core import *
from toontown.hood import ZoneUtil
from Interior import Interior
import ToonInteriorColors
import InteriorStorage
import random

SIGN_LEFT = -4
SIGN_RIGHT = 4
SIGN_BOTTOM = -3.5
SIGN_TOP = 1.5
FrameScale = 1.4

class ToonInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)

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
                if self.zoneId in InteriorStorage.ZoneStyles.keys() and category in InteriorStorage.ZoneStyles[self.zoneId]:
                    texture = InteriorStorage.findTexture(category, self.zoneId)
                else:
                    texture = InteriorStorage.findRandomTexture(category, self.randomGenerator)
                np.setTexture(texture, 100)
                newNP = np
            if key2 == 'c':
                if self.zoneId in InteriorStorage.ZoneStyles.keys() and category in InteriorStorage.ZoneStyles[self.zoneId]:
                    colorIndex = InteriorStorage.ZoneStyles[self.zoneId][category][1]
                    newNP.setColorScale(self.colors[category][colorIndex])
                else:
                    if category == 'TI_wallpaper' or category == 'TI_wallpaper_border':
                        self.randomGenerator.seed(self.zoneId)
                        newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))
                    else:
                        newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))

    def load(self):
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        interior = self.randomGenerator.choice(InteriorStorage.ToonInteriors)
        self.interiorFile = InteriorStorage.ModelPath + interior
        Interior.load(self)
        
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        doorOrigin = self.interior.find('**/door_origin')
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.1, 0)
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
        Interior.unload(self)
