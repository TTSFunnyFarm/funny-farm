from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from otp.nametag.NametagGroup import NametagGroup
from otp.nametag.Nametag import Nametag
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer

class Building(DirectObject):
    notify = directNotify.newCategory('Building')

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.block = self.getBlock()
        self.nametag = None

    def load(self):
        self.setupNametag()

    def unload(self):
        self.clearNametag()

    def getBlock(self):
        block = str(self.zoneId)
        block = int(block[2:])
        return block

    def getBuildingNodePath(self):
        geom = base.cr.playGame.getActiveZone().geom
        np = geom.find('**/tb%d:toon_landmark*' % self.block)
        if np.isEmpty():
            np = geom.find('**/sz%d:toon_landmark*' % self.block)
        return np

    def setupNametag(self):
        if self.nametag == None:
            self.nametag = NametagGroup()
            self.nametag.setFont(ToontownGlobals.getBuildingNametagFont())
            if TTLocalizer.BuildingNametagShadow:
                self.nametag.setShadow(*TTLocalizer.BuildingNametagShadow)
            self.nametag.setContents(Nametag.CName)
            self.nametag.setColorCode(NametagGroup.CCToonBuilding)
            self.nametag.setActive(0)
            self.nametag.setAvatar(self.getBuildingNodePath().find('**/*door_origin*'))
            self.nametag.setObjectCode(self.block)
            name = TTLocalizer.FFZone2TitleDict.get(self.zoneId, '')
            self.nametag.setName(name)
            self.nametag.manage(base.marginManager)
        return

    def clearNametag(self):
        if self.nametag != None:
            self.nametag.unmanage(base.marginManager)
            self.nametag.setAvatar(NodePath())
            self.nametag.destroy()
            self.nametag = None
        return
