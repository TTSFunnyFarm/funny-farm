from toontown.building import Building
from toontown.toonbase import ToontownGlobals, TTLocalizer
from libotp import *
from direct.gui.DirectGui import *
from panda3d.core import *
from . import HouseGlobals
import random

class House(Building.Building):
    def __init__(self, zoneId, idx, ownerData):
        Building.Building.__init__(self, zoneId)
        self.houseModel = 'phase_5.5/models/estate/houseB'
        self.model = None
        self.index = idx
        self.door = None
        self.namePlate = None
        self.nameText = None
        self.nametag = None
        self.floorMat = None
        self.matText = None
        self.randomGenerator = None
        self.ownerData = ownerData
        self.name = ''
        if self.ownerData != None:
            self.name = ownerData.setName

    def load(self):
        self.model = loader.loadModel(self.houseModel)
        self.model.setName('tb0{0}:toon_landmark_house'.format(self.index))
        self.model.flattenMedium()
        self.setupDoor()
        Building.Building.load(self)

    def unload(self):
        Building.Building.unload(self)
        self.door.removeNode()
        self.door = None
        self.model.removeNode()
        self.model = None
        self.clearNametag()
        if self.namePlate:
            self.namePlate.removeNode()
            del self.namePlate
            self.namePlate = None
        if self.floorMat:
            self.floorMat.removeNode()
            del self.floorMat
            self.floorMat = None
        del self.randomGenerator
        return

    def getBuildingNodePath(self):
        return self.model

    def setupDoor(self):
        self.notify.debug('setupDoor')
        doorModelName = 'door_double_round_ur'
        door = loader.loadModel('phase_3.5/models/modules/doors_practical').find('**/' + doorModelName)
        door_origin = self.model.find('**/door_origin')
        door_origin.setHpr(90, 0, 0)
        door_origin.setScale(0.6, 0.6, 0.8)
        door_origin.setPos(door_origin, 0.5, 0, 0.0)
        door.reparentTo(door_origin)
        self.door_origin = door_origin
        doorTrigger = door.find('**/' + doorModelName + '_trigger')
        doorTrigger.setName('door_trigger_{0}'.format(self.index))
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        houseColor = (0.651, 0.376, 0.31)
        door.setColor(houseColor[0], houseColor[1], houseColor[2], 1)
        door.find('**/door_*_hole_left').setColor(0, 0, 0, 1)
        door.find('**/door_*_hole_right').setColor(0, 0, 0, 1)
        door.find('**/door_*_hole_left').setDepthOffset(1)
        door.find('**/door_*_hole_right').setDepthOffset(1)
        self.door = door
        self.__setupNamePlate()
        self.__setupFloorMat()
        self.__setupNametag()

    def __setupNamePlate(self):
        self.notify.debug('__setupNamePlate')
        if self.namePlate:
            self.namePlate.removeNode()
            del self.namePlate
            self.namePlate = None
        nameText = TextNode('nameText')
        r = self.randomGenerator.random()
        g = self.randomGenerator.random()
        b = self.randomGenerator.random()
        nameText.setTextColor(r, g, b, 1)
        nameText.setAlign(nameText.ACenter)
        nameText.setFont(ToontownGlobals.getBuildingNametagFont())
        nameText.setShadowColor(0, 0, 0, 1)
        nameText.setBin('fixed')
        if TTLocalizer.BuildingNametagShadow:
            nameText.setShadow(*TTLocalizer.BuildingNametagShadow)
        nameText.setWordwrap(16.0)
        xScale = 1.0
        numLines = 0
        if self.name == '':
            return
        else:
            houseName = TTLocalizer.AvatarsHouse % TTLocalizer.GetPossesive(self.name)
        nameText.setText(houseName)
        self.nameText = nameText
        textHeight = nameText.getHeight() - 2
        textWidth = nameText.getWidth()
        xScale = 1.0
        if textWidth > 16:
            xScale = 16.0 / textWidth
        sign_origin = self.model.find('**/sign_origin')
        pos = sign_origin.getPos()
        sign_origin.setPosHpr(pos[0], pos[1], pos[2] + 0.15 * textHeight, 90, 0, 0)
        self.namePlate = sign_origin.attachNewNode(self.nameText)
        self.namePlate.setDepthWrite(0)
        self.namePlate.setPos(0, -0.05, 0)
        self.namePlate.setScale(xScale)
        return nameText

    def __setupFloorMat(self, changeColor = True):
        if self.floorMat:
            self.floorMat.removeNode()
            del self.floorMat
            self.floorMat = None
        mat = self.model.find('**/mat')
        if changeColor:
            mat.setColor(0.4, 0.357, 0.259, 1.0)
        color = HouseGlobals.houseColors[self.index]
        matText = TextNode('matText')
        matText.setTextColor(color[0], color[1], color[2], 1)
        matText.setAlign(matText.ACenter)
        matText.setFont(ToontownGlobals.getBuildingNametagFont())
        matText.setShadowColor(0, 0, 0, 1)
        matText.setBin('fixed')
        if TTLocalizer.BuildingNametagShadow:
            matText.setShadow(*TTLocalizer.BuildingNametagShadow)
        matText.setWordwrap(10.0)
        xScale = 1.0
        numLines = 0
        if self.name == '':
            return
        else:
            houseName = TTLocalizer.AvatarsHouse % TTLocalizer.GetPossesive(self.name)
        matText.setText(houseName)
        self.matText = matText
        textHeight = matText.getHeight() - 2
        textWidth = matText.getWidth()
        xScale = 1.0
        if textWidth > 8:
            xScale = 8.0 / textWidth
        mat_origin = self.model.find('**/mat_origin')
        pos = mat_origin.getPos()
        mat_origin.setPosHpr(pos[0] - 0.15 * textHeight, pos[1], pos[2], 90, -90, 0)
        self.floorMat = mat_origin.attachNewNode(self.matText)
        self.floorMat.setDepthWrite(0)
        self.floorMat.setPos(0, -.025, 0)
        self.floorMat.setScale(0.45 * xScale)
        return

    def __setupNametag(self):
        if self.nametag:
            self.clearNametag()
        if self.name == '':
            houseName = ''
        else:
            houseName = TTLocalizer.AvatarsHouse % TTLocalizer.GetPossesive(self.name)
        self.nametag = NametagGroup()
        self.nametag.setFont(ToontownGlobals.getBuildingNametagFont())
        if TTLocalizer.BuildingNametagShadow:
            self.nametag.setShadow(*TTLocalizer.BuildingNametagShadow)
        self.nametag.setContents(Nametag.CName)
        self.nametag.setColorCode(NametagGroup.CCHouseBuilding)
        self.nametag.setActive(0)
        self.nametag.setAvatar(self.model)
        self.nametag.setObjectCode(self.zoneId)
        self.nametag.setName(houseName)
        self.nametag.manage(base.marginManager)
