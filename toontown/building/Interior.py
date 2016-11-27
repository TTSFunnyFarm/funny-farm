from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from toontown.toon import NPCToons
from toontown.hood import ZoneUtil
import Door

class Interior(DirectObject):
    notify = directNotify.newCategory('Interior')

    def __init__(self, shopId, zoneId):
        self.zoneId = zoneId
        self.shopId = shopId
        self.interiorFile = None
        self.musicOk = 1

    def load(self):
        self.interior = loader.loadModel(self.interiorFile)
        self.interior.reparentTo(render)
        if self.musicOk:
            musicMgr.playCurrentZoneMusic()
        self.generateNPCs()

    def unload(self):
        musicMgr.stopMusic()
        self.ignoreAll()
        self.interior.removeNode()
        del self.interior
        for npc in self.npcs:
            npc.removeActive()
            npc.delete()
            del npc

    def generateNPCs(self):
        self.npcs = NPCToons.createNpcsInZone(self.zoneId)
        for i in xrange(len(self.npcs)):
            origin = self.interior.find('**/npc_origin_%d' % i)
            self.npcs[i].reparentTo(render)
            self.npcs[i].setPosHpr(origin.getPos(), origin.getHpr())
            self.npcs[i].addActive()

    def startActive(self):
        for door in self.interior.findAllMatches('**/door_double_*_ur'):
            self.accept('enter%s' % door.find('**/*_trigger').getName(), self.handleDoorTrigger)

    def handleDoorTrigger(self, collEntry):
        # goddamn toon HQs
        if collEntry.getIntoNodePath().getName() == 'door_0_trigger':
            self.shopId = 'door_0'
        elif collEntry.getIntoNodePath().getName() == 'door_1_trigger':
            self.shopId = 'door_1'
        building = collEntry.getIntoNodePath().getParent()
        door = Door.Door(building, self.shopId + '_int')
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.enterZone)

    def enterZone(self):
        zone = base.cr.playGame.getActiveZone()
        zone.exitPlace()
        if 'door' in self.shopId:
            zoneId = self.shopId
        else:
            zoneId = self.zoneId
        zone.enter(shop=str(zoneId))

    def setupDoor(self, name, parent):
        door = loader.loadModel('phase_3.5/models/modules/doors_practical').find('**/' + name)
        door.reparentTo(self.interior.find('**/' + parent))
        self.fixDoor(door)
        return door

    def fixDoor(self, door):
        door.find('**/door_*_hole_left').setColor(0, 0, 0, 1)
        door.find('**/door_*_hole_right').setColor(0, 0, 0, 1)
        door.find('**/door_*_hole_left').setDepthOffset(1)
        door.find('**/door_*_hole_right').setDepthOffset(1)
