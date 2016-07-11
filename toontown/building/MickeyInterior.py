from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
import ToonInteriorColors
import random
import Door

class MickeyInterior(DirectObject):

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.interiorFile = 'phase_14/models/modules/mickey_interior'

    def load(self):
        self.interior = loader.loadModel(self.interiorFile)
        self.interior.reparentTo(render)
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.colors = ToonInteriorColors.colors[self.zoneId]
        self.interior.find('**/door_origin').setScale(0.8, 0.8, 0.8)
        self.interior.find('**/door_origin').setH(180)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        doorColor = self.colors['TI_door'][1]
        self.door.setColor(doorColor)
        self.fixDoor(self.door)
        self.acceptOnce('avatarExitDone', self.startActive)
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()

    def unload(self):
        self.ignoreAll()
        self.interior.removeNode()
        del self.interior

    def startActive(self):
        self.acceptOnce('enterdoor_double_round_ur_trigger', self.__handleDoor)

    def __handleDoor(self, entry):
        door = Door.Door(self.door, 'mc_int', self.zoneId)
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.__handleEnterFF)

    def __handleEnterFF(self):
        base.cr.playGame.exitPlace()
        base.cr.playGame.enterFFHood(shop='mc')

    def setupDoor(self, name, node):
        door = loader.loadModel('phase_3.5/models/modules/doors_practical').find('**/' + name)
        door.reparentTo(self.interior.find('**/' + node))
        return door

    def fixDoor(self, door):
        door.find('**/door_*_hole_left').setColor(0, 0, 0, 1)
        door.find('**/door_*_hole_right').setColor(0, 0, 0, 1)
        door.find('**/door_*_flat').setDepthOffset(1)
        door.find('**/door_*_hole_left').setDepthOffset(2)
        door.find('**/door_*_hole_right').setDepthOffset(2)
        door.find('**/door_*_left').setDepthOffset(3)
        door.find('**/door_*_right').setDepthOffset(3)
        door.find('**/door_*_trigger').setY(-0.24)
        door.setDepthOffset(3)
