from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toon import NPCToons
from Interior import Interior
import ToonInteriorColors
import random
import Door

class HQInterior(Interior):

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.interiorFile = 'phase_3.5/models/modules/HQ_interior'

    def load(self):
        Interior.load(self)
        soundMgr.shopMusicMap[self.zoneId]()
        self.interior.find('**/cream').removeNode() # gotta clean up all the jizz
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.colors = ToonInteriorColors.colors[self.zoneId]
        self.generateNPCs()
        self.interior.find('**/door_origin_0').setScale(0.8, 0.8, 0.8)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin_0')
        doorColor = self.colors['TI_door'][1]
        self.door.setColor(doorColor)
        self.fixDoor(self.door)
        self.door.find('**/door_double_round_ur_trigger').setName('Door0Trigger')
        if self.zoneId in [3000, 3100, 4100, 5000, 5100]:
            self.interior.find('**/door_origin_1').setScale(0.8, 0.8, 0.8)
            self.door2 = self.setupDoor('door_double_round_ur', 'door_origin_1')
            self.door2.setColor(doorColor)
            self.fixDoor(self.door2)
            self.door2.find('**/door_double_round_ur_trigger').setName('Door1Trigger')
        self.acceptOnce('avatarExitDone', self.startActive)
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()

    def unload(self):
        soundMgr.stopAllMusic()
        for npc in self.npcs:
            npc.removeActive()
            npc.delete()
            del npc
        Interior.unload(self)

    def generateNPCs(self):
        if self.zoneId == FunnyFarmGlobals.FunnyFarm:
            clerk1 = NPCToons.createLocalNPC(2007)
            clerk2 = NPCToons.createLocalNPC(2008)
            clerk3 = NPCToons.createLocalNPC(2009)
            clerk4 = NPCToons.createLocalNPC(2010)
        elif self.zoneId == FunnyFarmGlobals.SillySprings:
            clerk1 = NPCToons.createLocalNPC(5001)
            clerk2 = NPCToons.createLocalNPC(5002)
            clerk3 = NPCToons.createLocalNPC(5003)
            clerk4 = NPCToons.createLocalNPC(5004)
        origins = [
                self.interior.find('**/npc_origin_0'),
                self.interior.find('**/npc_origin_1'),
                self.interior.find('**/npc_origin_2'),
                self.interior.find('**/npc_origin_3')
        ]
        key = -1
        self.npcs = [clerk1, clerk2, clerk3, clerk4]
        for npc in self.npcs:
            key += 1
            pos = origins[key].getPos()
            hpr = origins[key].getHpr()
            npc.reparentTo(render)
            npc.setPosHpr(pos, hpr)
            npc.initializeBodyCollisions('toon')
            npc.addActive()

    def startActive(self):
        self.acceptOnce('enterDoor0Trigger', self.__handleDoor, ['hq0'])
        if self.zoneId in [3000, 3100, 4100, 5000, 5100]:
            self.acceptOnce('enterDoor1Trigger', self.__handleDoor, ['hq1'])

    def __handleDoor(self, code, entry):
        if code == 'hq0':
            door = Door.Door(self.door, 'hq_int0', self.zoneId)
        else:
            door = Door.Door(self.door2, 'hq_int1', self.zoneId)
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.__handleEnterHood, [code])

    def __handleEnterHood(self, code):
        base.cr.playGame.exitPlace()
        if self.zoneId == FunnyFarmGlobals.FunnyFarm:
            base.cr.playGame.enterFFHood(shop=code)
        elif self.zoneId == FunnyFarmGlobals.SillySprings:
            base.cr.playGame.enterSSHood(shop=code)
