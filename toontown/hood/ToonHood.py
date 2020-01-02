from direct.actor.Actor import Actor
from panda3d.core import *

from toontown.building import Door
from toontown.building import GagShopInterior
from toontown.building import HQInterior
from toontown.building import LoonyLabsInterior
from toontown.building import PetShopInterior
from toontown.building import ToonHallInterior
from toontown.building import ToonInterior
from toontown.building.Building import Building
from toontown.hood.Hood import Hood
from toontown.quest import Quests
from toontown.safezone.Butterfly import Butterfly
from toontown.toonbase import TTLocalizer
from toontown.trolley.Trolley import Trolley
from toontown.fishing import FishingSpot

class ToonHood(Hood):
    Shop2ClassDict = {
        'gag_shop': GagShopInterior.GagShopInterior,
        'pet_shop': PetShopInterior.PetShopInterior,
        'door_0': HQInterior.HQInterior,
        'door_1': HQInterior.HQInterior,
        'toonhall': ToonHallInterior.ToonHallInterior,
        'loonylabs': LoonyLabsInterior.LoonyLabsInterior,
        'default': ToonInterior.ToonInterior
    }

    def __init__(self):
        Hood.__init__(self)
        self.fish = None
        self.trolley = None
        self.telescope = None
        self.animSeq = None
        self.buildings = []
        self.fishingSpots = []
        self.treasurePlanner = None
        self.butterflies = []

    def enter(self, shop=None, tunnel=None, init=0):
        base.localAvatar.setZoneId(self.zoneId)
        self.setupLandmarkBuildings()
        if self.treasurePlanner:
            self.treasurePlanner.loadTreasures()
        self.loadButterflies()
        if shop:
            musicMgr.playCurrentZoneMusic()
            building = self.geom.find('**/tb%s:toon_landmark*' % shop[2:])
            if building.isEmpty():
                building = self.geom.find('**/%s' % shop)
            door = Door.Door(building, shop)
            door.avatarExit(base.localAvatar)
            self.acceptOnce('avatarExitDone', self.startActive)
            return
        Hood.enter(self, shop=shop, tunnel=tunnel, init=init)

    def exit(self):
        Hood.exit(self)
        if len(self.buildings) > 0:
            self.destroyLandmarkBuildings()
        if self.treasurePlanner:
            self.treasurePlanner.unloadTreasures()
        self.unloadButterflies()

    def load(self):
        Hood.load(self)
        if not self.geom.find('**/fish_origin').isEmpty():
            self.fish = Actor('phase_4/models/props/exteriorfish-zero',
                              {'chan': 'phase_4/models/props/exteriorfish-swim'})
            self.fish.reparentTo(self.geom.find('**/fish_origin'))
            if config.GetBool('smooth-animations', True):
                self.fish.setBlend(frameBlend=True)
            self.fish.loop('chan')
        if not self.geom.find('**/*trolley_station*').isEmpty():
            self.trolley = Trolley()
            self.trolley.setup()
        self.createFishingSpots()

    def unload(self):
        Hood.unload(self)
        if self.fish:
            self.fish.stop()
            self.fish.cleanup()
            self.fish.removeNode()
            del self.fish
        if self.trolley:
            self.trolley.removeActive()
            self.trolley.delete()
            del self.trolley
        self.removeFishingSpots()
        if self.treasurePlanner:
            self.treasurePlanner.delete()
            del self.treasurePlanner
        del self.butterflies

    def startActive(self):
        Hood.startActive(self)
        if self.trolley:
            self.trolley.addActive()

    def setupLandmarkBuildings(self):
        for building in self.geom.findAllMatches('**/tb*toon_landmark*'):
            zoneStr = building.getName().split(':')
            block = int(zoneStr[0][2:])
            zoneId = self.zoneId + 500 + block
            self.buildings.append(Building(zoneId))
        for building in self.buildings:
            building.setToToon()
            building.load()
        self.refreshQuestIcons()

    def destroyLandmarkBuildings(self):
        for building in self.buildings:
            building.unload()
            building.delete()
            del building
        self.buildings = []

    def refreshQuestIcons(self):
        Hood.refreshQuestIcons(self)
        for building in self.buildings:
            for questDesc in base.localAvatar.quests:
                quest = Quests.getQuest(questDesc[0])
                quest.setQuestProgress(questDesc[1])
                if quest.getCompletionStatus() == Quests.COMPLETE or quest.getType() in [Quests.QuestTypeGoTo,
                                                                                         Quests.QuestTypeChoose,
                                                                                         Quests.QuestTypeDeliver,
                                                                                         Quests.QuestTypeDeliverGag]:
                    if quest.toLocation == building.zoneId:
                        if quest.questCategory == Quests.MainQuest:
                            building.setMainQuest(questDesc[0])
                        else:
                            building.setSideQuest(questDesc[0])
                        break
                    else:
                        building.clearQuestIcon()
            if 'toon_landmark_hq' in building.getBuildingNodePath().getName() and len(base.localAvatar.quests) < base.localAvatar.getQuestCarryLimit():
                if building.getMainQuest() or building.getSideQuest() or building.getQuestOffer():
                    continue
                flatAvQuests = []
                for questDesc in base.localAvatar.quests:
                    flatAvQuests.extend(questDesc)
                tier = base.cr.questManager.determineQuestTier(base.localAvatar)
                for questId in Quests.mainQuestTiers[tier]:
                    if Quests.getQuestFinished(questId) == Quests.Start \
                    and Quests.getQuestTier(questId) == tier \
                    and len(Quests.getReward(questId)) > 2 \
                    and Quests.getReward(questId)[2] in Quests.SpecialRewards \
                    and questId not in flatAvQuests \
                    and not base.localAvatar.hasQuestHistory(questId):
                        building.setQuestOffer(questId, hq=1)
                        break

    def handleDoorTrigger(self, collEntry):
        building = collEntry.getIntoNodePath().getParent()
        for shopId in self.Shop2ClassDict.keys():
            if shopId in building.getName():
                door = Door.Door(building, shopId)
                door.avatarEnter(base.localAvatar)
                if 'door' in building.getName():
                    building = self.geom.find('**/*toon_landmark_hq*')
                zoneStr = building.getName().split(':')
                block = int(zoneStr[0][2:])
                zoneId = self.zoneId + 500 + block
                self.acceptOnce('avatarEnterDone', self.enterPlace, [shopId, zoneId])
                return
        door = Door.Door(building, 'default')
        door.avatarEnter(base.localAvatar)
        try:
            zoneStr = building.getName()[2:4]
            zoneId = self.zoneId + 500 + int(zoneStr)
        except:
            zoneStr = building.getName()[2]
            zoneId = self.zoneId + 500 + int(zoneStr)
        self.acceptOnce('avatarEnterDone', self.enterPlace, ['default', zoneId])

    def enterPlace(self, shopId, zoneId):
        self.exit()
        self.geom.reparentTo(hidden)
        self.geom.stash()
        self.sky.reparentTo(hidden)
        self.sky.stash()
        if shopId not in self.Shop2ClassDict.keys():
            self.notify.warning('Could not find shopId: %s' % shopId)
            return
        self.place = self.Shop2ClassDict[shopId](shopId, zoneId)
        self.place.load()
        # So that music loops continuously between toon hall and loony labs:
        if shopId == 'toonhall':
            musicMgr.playCurrentZoneMusic()
        if shopId == 'door_1':
            door = Door.Door(self.place.door2, shopId + '_int')
        else:
            door = Door.Door(self.place.door, shopId + '_int')
        door.avatarExit(base.localAvatar)

    def exitPlace(self):
        self.place.unload()
        self.place = None
        self.geom.unstash()
        self.geom.reparentTo(render)

    def setupLandmarkBuildings(self):
        for building in self.geom.findAllMatches('**/tb*toon_landmark*'):
            zoneStr = building.getName().split(':')
            block = int(zoneStr[0][2:])
            zoneId = self.zoneId + 500 + block
            bldg = Building(zoneId)
            self.buildings.append(bldg)
        for building in self.buildings:
            building.load()

    def destroyLandmarkBuildings(self):
        for building in self.buildings:
            building.unload()
            del building
        self.buildings = []

    def createFishingSpots(self):
        for posSpot in self.geom.findAllMatches('**/FishingPier'):
            origin = posSpot.find('**/fishing_spot_origin')
            spot = FishingSpot.FishingSpot()
            spot.setParentNodePath(origin)
            spot.generate()
            self.fishingSpots.append(spot)

    def removeFishingSpots(self):
        for spot in self.fishingSpots:
            spot.disable()
            del spot
        del self.fishingSpots
