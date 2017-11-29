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
        # Overrides Interior.load because we don't want to start music here
        self.interior = loader.loadModel(self.interiorFile)
        self.interior.reparentTo(render)
        self.generateNPCs()
        
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
        self.loadQuestChanges()
        self.acceptOnce('avatarExitDone', self.startActive)

    def unload(self):
        # Overrides Interior.unload because we don't want to stop music here
        self.ignoreAll()
        self.interior.removeNode()
        del self.interior
        if hasattr(self, 'npcs'):
            for npc in self.npcs:
                npc.removeActive()
                npc.delete()
                del npc

    def generateNPCs(self):
        Interior.generateNPCs(self)

    def startActive(self):
        base.localAvatar.checkQuestCutscene()
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

    def loadQuestChanges(self):
        # Checks for any instance-based changes we need to make
        for questDesc in base.localAvatar.quests:
            if questDesc[0] == 1001 or questDesc[0] == 1002:
                self.npcs[0].stash()
                self.npcs[0].removeActive()
