from pandac.PandaModules import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toon import NPCToons
from Interior import Interior
import ToonInteriorColors
import random
import Door

class PetShopInterior(Interior):

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.interiorFile = 'phase_4/models/modules/PetShopInterior'

    def load(self):
        Interior.load(self)
        musicMgr.shopMusicMap[self.zoneId]()
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.colors = ToonInteriorColors.colors[self.zoneId]
        self.generateNPCs()
        self.generateFish()
        self.interior.find('**/door_origin').setScale(0.8, 0.8, 0.8)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        doorColor = self.colors['TI_door'][0]
        self.door.setColor(doorColor)
        self.fixDoor(self.door)
        self.acceptOnce('avatarExitDone', self.startActive)
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()

    def unload(self):
        musicMgr.stopAllMusic()
        self.bearSwim.finish()
        del self.bearSwim
        for fish in self.fish:
            fish.stop()
            fish.cleanup()
            fish.removeNode()
            del fish
        del self.fish
        for npc in self.npcs:
            npc.removeActive()
            npc.delete()
            del npc
        del self.npcs
        Interior.unload(self)

    def generateNPCs(self):
        if self.zoneId == FunnyFarmGlobals.FunnyFarm:
            clerk1 = NPCToons.createLocalNPC(2013)
            clerk2 = NPCToons.createLocalNPC(2014)
            clerk3 = NPCToons.createLocalNPC(2015)
        elif self.zoneId == FunnyFarmGlobals.SillySprings:
            clerk1 = NPCToons.createLocalNPC(5009)
            clerk2 = NPCToons.createLocalNPC(5010)
            clerk3 = NPCToons.createLocalNPC(5011)
        origins = [
                self.interior.find('**/npc_origin_0'),
                self.interior.find('**/npc_origin_1'),
                self.interior.find('**/npc_origin_2')
        ]
        key = 0
        self.npcs = [clerk1, clerk2, clerk3]
        for npc in self.npcs:
            key += 1
            pos = origins[key - 1].getPos()
            hpr = origins[key - 1].getHpr()
            npc.reparentTo(render)
            npc.setPosHpr(pos, hpr)
            npc.addActive()
        return

    def generateFish(self):
        self.fish = []
        for fishName in FunnyFarmGlobals.PetShopFish:
            fish = Actor('phase_4/models/char/' + fishName + '-zero.bam',
                                    {'swim':'phase_4/models/char/' + fishName + '-swim.bam'})
            fish.reparentTo(render)
            fish.setPos(FunnyFarmGlobals.PetShopFishPositions[FunnyFarmGlobals.PetShopFish.index(fishName)])
            fish.setHpr(FunnyFarmGlobals.PetShopFishRotations[FunnyFarmGlobals.PetShopFish.index(fishName)])
            fish.setScale(FunnyFarmGlobals.PetShopFishScales[FunnyFarmGlobals.PetShopFish.index(fishName)])
            fish.actorInterval('swim').loop()
            if fishName == 'BearAcuda':
                self.bearSwim = Parallel(
                        Sequence(
                                fish.posInterval(5, FunnyFarmGlobals.PetShopBearSwimPoints[0], blendType='easeInOut'),
                                fish.posInterval(5, FunnyFarmGlobals.PetShopBearSwimPoints[1], blendType='easeInOut'),
                                fish.posInterval(5, FunnyFarmGlobals.PetShopBearSwimPoints[2], blendType='easeInOut'),
                                fish.posInterval(5, FunnyFarmGlobals.PetShopBearSwimPoints[3], blendType='easeInOut')
                        ),
                        fish.hprInterval(20, Vec3(-270, 0, 0))
                )
                self.bearSwim.loop()
            self.fish.append(fish)
        return

    def startActive(self):
        self.acceptOnce('enterdoor_double_round_ur_trigger', self.__handleDoor)

    def __handleDoor(self, entry):
        door = Door.Door(self.door, 'ps_int', self.zoneId)
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.__handleEnterHood)

    def __handleEnterHood(self):
        base.cr.playGame.exitPlace()
        if self.zoneId == FunnyFarmGlobals.FunnyFarm:
            base.cr.playGame.enterFFHood(shop='ps')
        elif self.zoneId == FunnyFarmGlobals.SillySprings:
            base.cr.playGame.enterSSHood(shop='ps')
