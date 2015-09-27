from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toon import NPCToons
from Interior import Interior
import ToonInteriorColors
import random
import Door

class GagShopInterior(Interior):

    def __init__(self, zoneId):
        Interior.__init__(self)
        self.zoneId = zoneId
        self.interiorFile = 'phase_4/models/modules/gagShop_interior'

    def replaceRandomInModel(self, model):
        baseTag = 'random_'
        npc = model.findAllMatches('**/' + baseTag + '???_*')
        modelPath = 'phase_3.5/models/modules/'
        wallpaper = loader.loadTexture('phase_3.5/maps/stripeB5.jpg')
        wainscotting = loader.loadTexture('phase_3.5/maps/wall_paper_b4.jpg')
        for i in npc:
            name = i.getName()
            category = name[14:]
            key = name[7:9]
            if key == 'mo':
                np = loader.loadModel(modelPath + category)
                np.reparentTo(i)
            elif key == 'tc':
                if category == 'wallpaper' or category == 'wallpaper_border':
                    i.setTexture(wallpaper, 1)
                    if self.zoneId == FunnyFarmGlobals.FunnyFarm:
                        i.setColorScale(self.colors['TI_wallpaper'][3])
                    elif self.zoneId == FunnyFarmGlobals.SillySprings:
                        i.setColorScale(self.colors['TI_wallpaper'][1])
                elif category == 'wainscotting':
                    if self.zoneId == FunnyFarmGlobals.FunnyFarm:
                        i.setTexture(wainscotting, 1)
                        i.setColorScale(self.colors['TI_wainscotting'][0])
                    elif self.zoneId == FunnyFarmGlobals.SillySprings:
                        i.setColorScale(self.colors['TI_wainscotting'][1])


    def load(self):
        Interior.load(self)
        musicMgr.shopMusicMap[self.zoneId]()
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.colors = ToonInteriorColors.colors[self.zoneId]
        self.generateNPCs()
        self.interior.find('**/door_origin').setScale(0.8, 0.8, 0.8)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        doorColor = self.colors['TI_door'][1]
        self.door.setColor(doorColor)
        self.fixDoor(self.door)
        self.replaceRandomInModel(self.interior)
        self.acceptOnce('avatarExitDone', self.startActive)
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()

    def unload(self):
        musicMgr.stopAllMusic()
        for npc in self.npcs:
            npc.removeActive()
            npc.delete()
            del npc
        Interior.unload(self)

    def generateNPCs(self):
        if self.zoneId == FunnyFarmGlobals.FunnyFarm:
            clerk1 = NPCToons.createLocalNPC(2006)
            clerk2 = NPCToons.createLocalNPC(2011)
        elif self.zoneId == FunnyFarmGlobals.SillySprings:
            clerk1 = NPCToons.createLocalNPC(5005)
            clerk2 = NPCToons.createLocalNPC(5006)
        origins = [
                self.interior.find('**/npc_origin_0'),
                self.interior.find('**/npc_origin_1')
        ]
        key = 0
        self.npcs = [clerk1, clerk2]
        for npc in self.npcs:
            key += 1
            pos = origins[key - 1].getPos()
            hpr = origins[key - 1].getHpr()
            npc.reparentTo(render)
            npc.setPosHpr(pos, hpr)
            npc.addActive()

    def startActive(self):
        self.acceptOnce('enterdoor_double_round_ur_trigger', self.__handleDoor)

    def __handleDoor(self, entry):
        door = Door.Door(self.door, 'gs_int', self.zoneId)
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.__handleEnterHood)

    def __handleEnterHood(self):
        base.cr.playGame.exitPlace()
        if self.zoneId == FunnyFarmGlobals.FunnyFarm:
            base.cr.playGame.enterFFHood(shop='gs')
        elif self.zoneId == FunnyFarmGlobals.SillySprings:
            base.cr.playGame.enterSSHood(shop='gs')
