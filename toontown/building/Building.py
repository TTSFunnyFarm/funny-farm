from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from otp.nametag.NametagGroup import NametagGroup
from otp.nametag.Nametag import Nametag
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.quest.QuestIcon import *

class Building(DirectObject):
    notify = directNotify.newCategory('Building')

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.block = self.getBlock()
        self.nametag = None
        self.questOffer = None
        self.mainQuest = None
        self.sideQuest = None
        self.questIcon = None

    def load(self):
        self.setupNametag()

    def unload(self):
        self.clearNametag()
        self.clearQuestIcon()

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
            name = TTLocalizer.zone2TitleDict.get(self.zoneId, '')
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

    def setQuestOffer(self, questId):
        self.questOffer = questId
        if self.questIcon:
            self.questIcon.unload()
        self.questIcon = QuestIcon(typeId=Offer)
        self.questIcon.reparentTo(self.getBuildingNodePath().find('**/*door_origin*'))
        self.questIcon.setPos(0, -1, 10)
        self.questIcon.setScale(3.0)
        self.questIcon.start()

    def clearQuestOffer(self):
        self.questOffer = None
        if self.questIcon:
            self.questIcon.unload()
            self.questIcon = None

    def getQuestOffer(self):
        return self.questOffer

    def setMainQuest(self, questId):
        self.mainQuest = questId
        if self.questIcon:
            self.questIcon.unload()
        self.questIcon = QuestIcon(typeId=Main)
        self.questIcon.reparentTo(self.getBuildingNodePath().find('**/*door_origin*'))
        self.questIcon.setPos(0, -1, 10)
        self.questIcon.setScale(3.0)
        self.questIcon.start()

    def clearMainQuest(self):
        self.mainQuest = None
        if self.questIcon:
            self.questIcon.unload()
            self.questIcon = None

    def getMainQuest(self):
        return self.mainQuest

    def setSideQuest(self, questId):
        self.sideQuest = questId
        if self.questIcon:
            self.questIcon.unload()
        self.questIcon = QuestIcon(typeId=Bonus)
        self.questIcon.reparentTo(self.getBuildingNodePath().find('**/*door_origin*'))
        self.questIcon.setPos(0, -1, 10)
        self.questIcon.setScale(3.0)
        self.questIcon.start()

    def clearSideQuest(self):
        self.sideQuest = None
        if self.questIcon:
            self.questIcon.unload()
            self.questIcon = None

    def getSideQuest(self):
        return self.sideQuest

    def clearQuestIcon(self):
        if self.questOffer:
            self.clearQuestOffer()
        elif self.mainQuest:
            self.clearMainQuest()
        elif self.sideQuest:
            self.clearSideQuest()
