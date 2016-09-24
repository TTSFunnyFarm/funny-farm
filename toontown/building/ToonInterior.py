from panda3d.core import *
from toontown.hood import ZoneUtil
from Interior import Interior
import ToonInteriorColors
import random

SIGN_LEFT = -4
SIGN_RIGHT = 4
SIGN_BOTTOM = -3.5
SIGN_TOP = 1.5
FrameScale = 1.4

class ToonInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)

    def randomDNAItem(self, category, findFunc):
        codeCount = self.dnaStore.getNumCatalogCodes(category)
        index = self.randomGenerator.randint(0, codeCount - 1)
        code = self.dnaStore.getCatalogCode(category, index)
        return findFunc(code)

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
                model = self.randomDNAItem(category, self.dnaStore.findNode)
                newNP = model.copyTo(np)
                c = render.findAllMatches('**/collision')
                c.stash()
                if key2 == 'r':
                    self.replaceRandomInModel(newNP)
            elif key1 == 't':
                texture = self.randomDNAItem(category, self.dnaStore.findTexture)
                np.setTexture(texture, 100)
                newNP = np
            if key2 == 'c':
                if category == 'TI_wallpaper' or category == 'TI_wallpaper_border':
                    self.randomGenerator.seed(self.zoneId)
                    newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))
                else:
                    newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))

    def load(self):
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        interior = self.randomDNAItem('TI_room', self.dnaStore.findNode)
        self.interior = interior.copyTo(render)
        musicMgr.playCurrentZoneMusic()
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        doorOrigin = self.interior.find('**/door_origin')
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.1, 0)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        doorColor = self.randomGenerator.choice(self.colors['TI_door'])
        self.door.setColor(doorColor)
        block = str(self.zoneId)[2:]
        sign = hidden.find('**/tb%s:*_landmark_*_DNARoot/**/sign;+s' % block)
        if not sign.isEmpty():
            signOrigin = self.interior.find('**/sign_origin')
            newSignNP = sign.copyTo(signOrigin)
            newSignNP.setDepthWrite(1, 1)
            #TODO: getSignTransform
            #mat = self.dnaStore.getSignTransformFromBlockNumber(int(self.block))
            inv = Mat4(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            #inv.invertFrom(mat)
            newSignNP.setMat(inv)
            newSignNP.flattenLight()
            ll = Point3()
            ur = Point3()
            newSignNP.calcTightBounds(ll, ur)
            width = ur[0] - ll[0]
            height = ur[2] - ll[2]
            if width != 0 and height != 0:
                xScale = (SIGN_RIGHT - SIGN_LEFT) / width
                zScale = (SIGN_TOP - SIGN_BOTTOM) / height
                scale = min(xScale, zScale)
                xCenter = (ur[0] + ll[0]) / 2.0
                zCenter = (ur[2] + ll[2]) / 2.0
                newSignNP.setPosHprScale((SIGN_RIGHT + SIGN_LEFT) / 2.0 - xCenter * scale, -0.1, (SIGN_TOP + SIGN_BOTTOM) / 2.0 - zCenter * scale, 0.0, 0.0, 0.0, scale, scale, scale)
        del self.colors
        del self.randomGenerator
        self.generateNpcs()
        self.interior.flattenMedium()
        self.acceptOnce('avatarExitDone', self.startActive)
