from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from toontown.toon import NPCToons
from toontown.hood import ZoneUtil
from toontown.quest import Quests
import Door

class Interior(DirectObject):
    notify = directNotify.newCategory('Interior')

    def __init__(self, shopId, zoneId):
        self.zoneId = zoneId
        self.shopId = shopId
        self.interiorFile = None

    def load(self):
        self.interior = loader.loadModel(self.interiorFile)
        self.interior.reparentTo(render)
        musicMgr.playCurrentZoneMusic()
        self.generateNPCs()

    def unload(self):
        musicMgr.stopMusic()
        self.ignoreAll()
        self.interior.removeNode()
        del self.interior
        if hasattr(self, 'npcs'):
            for npc in self.npcs:
                npc.removeActive()
                npc.delete()
                del npc

    def generateNPCs(self):
        self.npcs = NPCToons.createNpcsInZone(self.zoneId)
        for i in xrange(len(self.npcs)):
            origin = self.interior.find('**/npc_origin_%d' % i)
            if not origin.isEmpty():
                self.npcs[i].reparentTo(render)
                self.npcs[i].setPosHpr(origin, 0, 0, 0, 0, 0, 0)
                self.npcs[i].origin = origin
                self.npcs[i].addActive()
            else:
                self.notify.warning('generateNPCs(): Could not find npc_origin_%d' % i)
        self.refreshQuestIcons()
    
    def refreshQuestIcons(self):
        for npc in self.npcs:
            for questDesc in base.localAvatar.quests:
                quest = Quests.getQuest(questDesc[0])
                quest.setQuestProgress(questDesc[1])
                if quest.getCompletionStatus() == Quests.COMPLETE or quest.getType() in [Quests.QuestTypeGoTo, Quests.QuestTypeChoose, Quests.QuestTypeDeliver]:
                    if quest.toNpc == npc.getNpcId():
                        if quest.questCategory == Quests.MainQuest:
                            npc.setMainQuest(questDesc[0])
                        else:
                            npc.setSideQuest(questDesc[0])
                        break
                    else:
                        npc.clearQuestIcon()
            # todo: display quest offers on toons

    def startActive(self):
        if self.shopId == 'toonhall':
            self.accept('enterbarn_door_trigger', self.handleDoorTrigger)
        for door in self.interior.findAllMatches('**/door_double_*_ur'):
            if not door.find('**/*_trigger').isEmpty():
                self.accept('enter%s' % door.find('**/*_trigger').getName(), self.handleDoorTrigger)
        self.accept('questsChanged', self.refreshQuestIcons)

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
        if name == 'barn_door':
            door = loader.loadModel('phase_14/models/modules/FF_barn_doors')
        else:
            door = loader.loadModel('phase_3.5/models/modules/doors_practical').find('**/' + name)
        door.reparentTo(self.interior.find('**/' + parent))
        self.fixDoor(door)
        return door

    def fixDoor(self, door):
        door.find('**/*door*hole_left').setColor(0, 0, 0, 1)
        door.find('**/*door*hole_right').setColor(0, 0, 0, 1)
        if door.getName() != 'barn_door':
            door.find('**/*door*hole_left').setDepthOffset(1)
            door.find('**/*door*hole_right').setDepthOffset(1)
