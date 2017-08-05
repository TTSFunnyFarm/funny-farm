from panda3d.core import *
from toontown.hood import ZoneUtil
from Interior import Interior
import ToonInteriorColors
import InteriorStorage
import random
import Door

class ToonHallInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)
        self.interiorFile = 'phase_14/models/modules/toonhall_interior'

    def load(self):
        Interior.load(self)
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        doorOrigin = self.interior.find('**/door_origin')
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        labDoorOrigin = self.interior.find('**/lab_door_origin')
        labDoorOrigin.setScale(0.8, 0.8, 0.8)
        labDoorOrigin.setPos(labDoorOrigin, 0, -0.025, 0)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        self.labDoor = self.setupDoor('door_double_round_ur', 'lab_door_origin')
        self.labDoor.find('**/door_double_round_ur_trigger').setName('door_trigger_15')
        doorColor = 0
        self.labDoor.setColor(self.colors['TI_door'][doorColor])
        if self.zoneId in InteriorStorage.ZoneStyles:
            doorColor = InteriorStorage.ZoneStyles[self.zoneId].get('TI_door', 0)
        self.door.setColor(self.colors['TI_door'][doorColor])
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()
        self.acceptOnce('avatarExitDone', self.startActive)

    def unload(self):
        Interior.unload(self)

    def generateNPCs(self):
        Interior.generateNPCs(self)
        self.npcs[0].useLOD(1000)
        #self.npcs[1].initPos()
        #self.npcs[2].initPos()
        #self.npcs[3].initPos()
        #self.npcs[1].setAnimState('ScientistJealous')
        #self.npcs[2].setAnimState('ScientistJealous')
        #self.npcs[3].setAnimState('ScientistEmcee')

    def startActive(self):
        Interior.startActive(self)
        self.accept('enterdoor_trigger_15', self.handleLabDoorTrigger)

    def handleLabDoorTrigger(self, collEntry):
        building = collEntry.getIntoNodePath().getParent()
        door = Door.Door(building, self.shopId + '_int')
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.enterLoonyLabs)

    def enterLoonyLabs(self):
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
        zone = base.cr.playGame.getActiveZone()
        zone.place.unload()
        zone.place = zone.Shop2ClassDict['loonylabs']('loonylabs', 1515)
        zone.place.load()
        door = Door.Door(zone.place.door, 'loonylabs_int')
        door.avatarExit(base.localAvatar)
