from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle import SuitBattleGlobals
from toontown.toon import NPCToons
from toontown.hood import ZoneUtil
import copy

CompleteString = TTLocalizer.QuestsCompleteString
GREETING = 0
QUEST = 1
INCOMPLETE = 2
INCOMPLETE_PROGRESS = 3
INCOMPLETE_WRONG_NPC = 4
COMPLETE = 5
LEAVING = 6
Any = 1
Start = 1
Cont = 0
Anywhere = 1
NA = 2
Same = 3
AnyFish = 4
ToonHQ = 1000
MainQuest = 0
SideQuest = 1
JustForFun = 2
QuestTypeGoTo = 0
QuestTypeChoose = 1
QuestTypeDefeatCog = 2
QuestTypeDefeatBuilding = 3
QuestTypeRecover = 4
QuestTypeDeliver = 5
QuestTypeDeliverGag = 6
QuestTypeCollect = 7
QuestRewardNone = 0
QuestRewardXP = 1
QuestRewardGagTraining = 2
QuestRewardTrackFrame = 3
QuestRewardNewGag = 4
QuestRewardCarryToonTasks = 5
QuestRewardCarryJellybeans = 6
QuestRewardCarryGags = 7
QuestRewardJellybeans = 8
QuestRewardCheesyEffect = 9
FF_TIER = 0
SS_TIER = 2
CV_TIER = 4
MM_TIER = 6

def getCompleteStatusWithNpc(questComplete, toNpcId, npc):
    if questComplete:
        if npc:
            if npcMatches(toNpcId, npc):
                return COMPLETE
            else:
                return INCOMPLETE_WRONG_NPC
        else:
            return COMPLETE
    elif npc:
        if npcMatches(toNpcId, npc):
            return INCOMPLETE_PROGRESS
        else:
            return INCOMPLETE
    else:
        return INCOMPLETE


def npcMatches(toNpcId, npc):
    return toNpcId == npc.getNpcId() or toNpcId == Any or toNpcId == ToonHQ and npc.getHq() or toNpcId == ToonTailor and npc.getTailor()


def calcRecoverChance(numberNotDone, baseChance, cap = 1):
    chance = baseChance
    avgNum2Kill = 1.0 / (chance / 100.0)
    if numberNotDone >= avgNum2Kill * 1.5 and cap:
        chance = 1000
    elif numberNotDone > avgNum2Kill * 0.5:
        diff = float(numberNotDone - avgNum2Kill * 0.5)
        luck = 1.0 + abs(diff / (avgNum2Kill * 0.5))
        chance *= luck
    return chance

class Quest:
    notify = directNotify.newCategory('Quest')
    trackCodes = ['c',
     'l',
     'm',
     's']
    trackNamesS = [TTLocalizer.BossbotS,
     TTLocalizer.LawbotS,
     TTLocalizer.CashbotS,
     TTLocalizer.SellbotS]
    trackNamesP = [TTLocalizer.BossbotP,
     TTLocalizer.LawbotP,
     TTLocalizer.CashbotP,
     TTLocalizer.SellbotP]

    def __init__(self, questId):
        self.questId = questId
        self.questProgress = 0
        self.generateQuestInfo()

    def generateQuestInfo(self):
        questInfo = QuestDict[self.questId]
        self.questTier = questInfo[0]
        self.questType = questInfo[2]
        if self.questType[0] == QuestTypeChoose:
            trackAccess = base.localAvatar.getTrackAccess()
            if self.questTier == FF_TIER:
                self.trackA = LURE_TRACK
                self.trackB = SOUND_TRACK
            elif self.questTier == SS_TIER:
                if trackAccess[LURE_TRACK]:
                    self.trackA = SOUND_TRACK
                elif trackAccess[SOUND_TRACK]:
                    self.trackA = LURE_TRACK
                self.trackB = DROP_TRACK
            elif self.questTier == CV_TIER:
                if trackAccess[LURE_TRACK] and trackAccess[SOUND_TRACK]:
                    self.trackA = DROP_TRACK
                elif trackAccess[LURE_TRACK] and trackAccess[DROP_TRACK]:
                    self.trackA = SOUND_TRACK
                elif trackAccess[SOUND_TRACK] and trackAccess[DROP_TRACK]:
                    self.trackA = LURE_TRACK
                self.trackB = TRAP_TRACK
            elif self.questTier == MM_TIER:
                if trackAccess[LURE_TRACK] and trackAccess[SOUND_TRACK] and trackAccess[DROP_TRACK]:
                    self.trackA = TRAP_TRACK
                elif trackAccess[LURE_TRACK] and trackAccess[SOUND_TRACK] and trackAccess[TRAP_TRACK]:
                    self.trackA = DROP_TRACK
                elif trackAccess[LURE_TRACK] and trackAccess[DROP_TRACK] and trackAccess[TRAP_TRACK]:
                    self.trackA = SOUND_TRACK
                elif trackAccess[SOUND_TRACK] and trackAccess[DROP_TRACK] and trackAccess[TRAP_TRACK]:
                    self.trackA = LURE_TRACK
                self.trackB = None
        elif self.questType[0] == QuestTypeDefeatCog:
            self.numCogs = self.questType[1]
            self.cogLevel = self.questType[2]
            self.cogTrack = self.questType[3]
            self.cogType = self.questType[4]
            self.cogLocation = self.questType[5]
        # todo finish quest types
        self.fromNpc = questInfo[3]
        self.toNpc = questInfo[4]
        self.fromLocation = questInfo[5]
        self.toLocation = questInfo[6]
        if self.fromNpc == NA:
            self.fromNpc = None
        if self.toNpc == Same:
            self.toNpc = self.fromNpc
        if self.fromLocation == NA:
            self.fromLocation = None
        if self.toLocation == Same:
            self.toLocation = self.fromLocation
        self.questReward = questInfo[7]
        self.category = questInfo[8]
        self.questDialog = questInfo[9]

    def setQuestProgress(self, progress):
        self.questProgress = progress

    def getQuestData(self):
        return [self.questId, self.questProgress]

    def getType(self):
        return self.questType[0]

    def getChoices(self):
        return (self.trackA, self.trackB)

    def getNumCogs(self):
        return self.numCogs

    def getCogLevel(self):
        return self.cogLevel

    def getCogType(self):
        return self.cogType

    def getCogTrack(self):
        return self.cogTrack

    def getNumBuildings(self):
        pass

    def getNumFloors(self):
        pass

    def getNumItems(self):
        pass

    def getItem(self):
        pass

    def getPercentChance(self):
        pass

    def getHolder(self):
        pass

    def getHolderType(self):
        pass

    def getNumQuestItems(self):
        if self.questType[0] == QuestTypeGoTo:
            return 1
        elif self.questType[0] == QuestTypeChoose:
            return 1
        elif self.questType[0] == QuestTypeDefeatCog:
            return self.getNumCogs()
        elif self.questType[0] == QuestTypeDefeatBuilding:
            return self.getNumBuildings()
        elif self.questType[0] == QuestTypeRecover:
            return self.getNumItems()
        elif self.questType[0] == QuestTypeDeliver:
            return 1
        elif self.questType[0] == QuestTypeDeliverGag:
            return self.getNumItems()

    def getCompletionStatus(self):
        questComplete = self.questProgress >= self.getNumQuestItems()
        if questComplete:
            return COMPLETE
        return INCOMPLETE

    def getLocation(self):
        return self.questType[-1]

    def getLocationName(self):
        if self.questType[-1] == Anywhere:
            return ''
        return TTLocalizer.QuestStreetNames.get(self.questType[-1], '')

    def isLocationMatch(self, zoneId):
        loc = self.getLocation()
        if loc is Anywhere:
            return 1
        if ZoneUtil.isPlayground(loc):
            if loc == ZoneUtil.getCanonicalHoodId(zoneId):
                return 1
            else:
                return 0
        elif loc == ZoneUtil.getCanonicalBranchZone(zoneId):
            return 1
        elif loc == zoneId:
            return 1
        else:
            return 0

    def getHeadlineString(self):
        if self.getType() == QuestTypeGoTo:
            return TTLocalizer.QuestsVisitQuestHeadline
        elif self.getType() == QuestTypeChoose:
            return TTLocalizer.QuestsTrackChoiceQuestHeadline
        elif self.getType() == QuestTypeDefeatCog or self.getType() == QuestTypeDefeatBuilding:
            return TTLocalizer.QuestsCogQuestHeadline
        elif self.getType() == QuestTypeRecover:
            return TTLocalizer.QuestsRecoverItemQuestHeadline
        elif self.getType() == QuestTypeDeliver or self.getType() == QuestTypeDeliverGag:
            return TTLocalizer.QuestsDeliverItemQuestHeadline

    def getProgressString(self):
        if self.getCompletionStatus() == COMPLETE:
            return CompleteString
        if self.getType() == QuestTypeDefeatCog:
            if self.getNumCogs() == 1:
                return ''
            else:
                return TTLocalizer.QuestsCogQuestProgress % {'progress': self.questProgress,
                 'numCogs': self.getNumCogs()}
        elif self.getType() == QuestTypeDefeatBuilding:
            if self.numBuildings == 1:
                return ''
            else:
                return TTLocalizer.QuestsBuildingQuestProgressString % {'progress': self.questProgress,
                 'num': self.getNumBuildings()}
        elif self.getType() == QuestTypeRecover:
            if self.numItems == 1:
                return ''
            else:
                return TTLocalizer.QuestsRecoverItemQuestProgress % {'progress': self.questProgress,
                 'numItems': self.getNumItems()}
        else:
            return ''

    def getObjectiveStrings(self):
        if self.getType() == QuestTypeGoTo:
            return ['']
        elif self.getType() == QuestTypeChoose:
            trackAName = Tracks[self.trackA].capitalize()
            trackBName = Tracks[self.trackB].capitalize()
            return [trackAName, trackBName]
        elif self.getType() == QuestTypeDefeatCog:
            cogName = self.getCogNameString()
            numCogs = self.getNumCogs()
            if numCogs == 1:
                text = cogName
            else:
                text = TTLocalizer.QuestsCogQuestDefeatDesc % {'numCogs': numCogs,
                 'cogName': cogName}
            return (text,)
        elif self.getType() == QuestTypeDefeatBuilding:
            count = self.getNumBuildings()
            floors = TTLocalizer.QuestsBuildingQuestFloorNumbers[self.getNumFloors() - 1]
            buildingTrack = self.getBuildingTrack()
            if buildingTrack == Any:
                type = TTLocalizer.Cog
            else:
                type = self.trackNames[self.trackCodes.index(buildingTrack)]
            if count == 1:
                if floors == '':
                    text = TTLocalizer.QuestsBuildingQuestDesc
                else:
                    text = TTLocalizer.QuestsBuildingQuestDescF
            elif floors == '':
                text = TTLocalizer.QuestsBuildingQuestDescC
            else:
                text = TTLocalizer.QuestsBuildingQuestDescCF
            return (text % {'count': count,
              'floors': floors,
              'type': type},)
        elif self.getType() == QuestTypeRecover:
            holder = self.getHolder()
            holderType = self.getHolderType()
            if holder == Any:
                holderName = TTLocalizer.TheCogs
            elif holder == AnyFish:
                holderName = TTLocalizer.AFish
            elif holderType == 'type':
                holderName = SuitBattleGlobals.SuitAttributes[holder]['pluralname']
            elif holderType == 'level':
                holderName = TTLocalizer.QuestsRecoverItemQuestHolderString % {'level': TTLocalizer.Level,
                 'holder': holder,
                 'cogs': TTLocalizer.Cogs}
            elif holderType == 'track':
                if holder == 'c':
                    holderName = TTLocalizer.BossbotP
                elif holder == 's':
                    holderName = TTLocalizer.SellbotP
                elif holder == 'm':
                    holderName = TTLocalizer.CashbotP
                elif holder == 'l':
                    holderName = TTLocalizer.LawbotP
            item = self.getItem()
            num = self.getNumItems()
            if num == 1:
                itemName = ItemDict[item][2] + ItemDict[item][0]
            else:
                itemName = TTLocalizer.QuestsItemNameAndNum % {'num': TTLocalizer.getLocalNum(num),
                 'name': ItemDict[item][1]}
            return [itemName, holderName]
        elif self.getType() == QuestTypeDeliver:
            return [ItemDict[self.getItem()]]
        elif self.getType() == QuestTypeDeliverGag:
            track, item = self.getGagType()
            num = self.getNumGags()
            if num == 1:
                text = AvPropStringsSingular[track][item]
            else:
                gagName = AvPropStringsPlural[track][item]
                text = TTLocalizer.QuestsItemNameAndNum % {'num': TTLocalizer.getLocalNum(num),
                 'name': gagName}
            return (text,)

    def getString(self):
        questString = None
        if self.getType() == QuestTypeGoTo:
            return TTLocalizer.QuestsVisitQuestStringShort
        elif self.getType() == QuestTypeChoose:
            return TTLocalizer.QuestsTrackChoiceQuestString % {'trackA': self.getObjectiveStrings()[0],
             'trackB': self.getObjectiveStrings()[1]}
        elif self.getType() == QuestTypeDefeatCog or self.getType() == QuestTypeDefeatBuilding:
            return TTLocalizer.QuestsCogQuestDefeat % self.getObjectiveStrings()[0]
        elif self.getType() == QuestTypeRecover:
            return TTLocalizer.QuestsRecoverItemQuestString % {'item': self.getObjectiveStrings()[0],
             'holder': self.getObjectiveStrings()[1]}
        elif self.getType() == QuestTypeDeliver or self.getType() == QuestTypeDeliverGag:
            return TTLocalizer.QuestsDeliverItemQuestString % self.getObjectiveStrings()[0]
        return self.getObjectiveStrings()[0]

    def getRewardString(self, progressString):
        if self.getType() == QuestTypeGoTo:
            return TTLocalizer.QuestsVisitQuestStringLong
        elif self.getType() == QuestTypeDeliver:
            return TTLocalizer.QuestsDeliverItemQuestStringLong % self.getObjectiveStrings()[0]
        elif self.getType() == QuestTypeDeliverGag:
            return TTLocalizer.QuestsDeliverGagQuestStringLong % self.getObjectiveStrings()[0]
        return self.getString() + ' : ' + progressString

    def getCogNameString(self):
        numCogs = self.getNumCogs()
        cogType = self.getCogType()
        cogTrack = self.getCogTrack()
        cogLevel = self.getCogLevel()
        if numCogs == 1:
            if cogType != Any:
                name = SuitBattleGlobals.SuitAttributes[cogType]['singularname']
            elif cogTrack != Any:
                if cogTrack == 'c':
                    name = TTLocalizer.BossbotS
                elif cogTrack == 'l':
                    name = TTLocalizer.LawbotS
                elif cogTrack == 'm':
                    name = TTLocalizer.CashbotS
                elif cogTrack == 's':
                    name = TTLocalizer.SellbotS
            else:
                name = TTLocalizer.ACog
            if cogLevel is Any:
                return name
            else:
                return TTLocalizer.QuestsCogLevelQuestDesc % {'level': cogLevel, 'name': name}
        elif cogType is Any:
            name = TTLocalizer.Cogs
            if cogTrack != Any:
                if cogTrack == 'c':
                    name = TTLocalizer.BossbotP
                elif cogTrack == 'l':
                    name = TTLocalizer.LawbotP
                elif cogTrack == 'm':
                    name = TTLocalizer.CashbotP
                elif cogTrack == 's':
                    name = TTLocalizer.SellbotP
            if cogLevel is Any:
                return name
            else:
                return TTLocalizer.QuestsCogLevelQuestDescC % {'level': cogLevel, 'name': name}
        else:
            name = SuitBattleGlobals.SuitAttributes[cogType]['pluralname']
            if cogLevel is Any:
                return name
            else:
                return TTLocalizer.QuestsCogLevelQuestDescC % {'level': cogLevel, 'name': name}

    def doesCogCount(self, avId, cogDict, zoneId, avList):
        if self.getType() == QuestTypeDefeatCog:
            questCogLevel = self.getCogLevel()
            questCogType = self.getCogType()
            questCogTrack = self.getCogTrack()
            if questCogLevel is Any or questCogLevel <= cogDict['level']:
                if questCogType is Any:
                    cogCounts = 1
                elif questCogType == cogDict['type']:
                    cogCounts = 1
                elif questCogTrack == cogDict['track']:
                    cogCounts = 1
                else:
                    cogCounts = 0
            else:
                cogCounts = 0
            return cogCounts and avId in cogDict['activeToons'] and self.isLocationMatch(zoneId)
        else:
            return 0

def getQuest(questId):
    return Quest(questId)

QuestDict = {
 # These first few quests are kind of weird because I'm
 # trying to plan out how cutscenes will fit in and stuff
 1001: (FF_TIER,          # Quest tier
        Start,            # Starts or continues
        (QuestTypeGoTo,), # Quest type (& info)
        NA,               # From npc
        1001,             # To npc
        1514,             # From location
        Same,             # To location
        (QuestRewardXP,   # Reward
         20),
        MainQuest,
        TTLocalizer.QuestDialogDict[1001]), # Dialog dict
 1002: (FF_TIER,
        Start,
        (QuestTypeGoTo,),
        NA,
        Same,
        1514,
        1515,
        (QuestRewardNone,),
        MainQuest,
        None),
 1003: (FF_TIER,
        Start,
        (QuestTypeGoTo,),
        NA,
        1001,
        1515,
        1514,
        (QuestRewardGagTraining,),
        MainQuest,
        None),
 1004: (FF_TIER,
        Cont,
        (QuestTypeChoose,),
        1001,
        Same,
        1514,
        Same,
        (QuestRewardGagTraining,),
        MainQuest,
        TTLocalizer.QuestDialogDict[1004]),
 1005: (FF_TIER,
        Cont,
        (QuestTypeDefeatCog, # Quest type
         4,                  # Number of cogs
         Any,                # Level minimum
         Any,                # Track (c, l, m, s)
         Any,                # Cog type (DNA code)
         FunnyFarmGlobals.RicketyRoad), # Location
        1001,
        Same,
        1514,
        Same,
        (QuestRewardXP,
         30,
         QuestRewardTrackFrame,
         1),
        MainQuest,
        TTLocalizer.QuestDialogDict[1005])
}

def isQuestJustForFun(questId):
    questEntry = QuestDict.get(questId)
    if questEntry[8] == JustForFun:
        return True
    return False

def getNpcInfo(npcId):
    npcName = NPCToons.getNPCName(npcId)
    npcZone = NPCToons.getNPCZone(npcId)
    hoodId = ZoneUtil.getCanonicalHoodId(npcZone)
    hoodName = FunnyFarmGlobals.hoodNameMap[hoodId]
    buildingArticle = NPCToons.getBuildingArticle(npcZone)
    buildingName = NPCToons.getBuildingTitle(npcZone)
    branchId = ZoneUtil.getCanonicalBranchZone(npcZone)
    toStreet = ToontownGlobals.StreetNames[branchId][0]
    streetName = ToontownGlobals.StreetNames[branchId][-1]
    isInPlayground = ZoneUtil.isPlayground(branchId)
    return (npcName,
     hoodName,
     buildingArticle,
     buildingName,
     toStreet,
     streetName,
     isInPlayground)

def getNpcLocationDialog(fromNpcId, toNpcId):
    if not toNpcId:
        return (None, None, None)
    fromNpcZone = None
    fromBranchId = None
    if fromNpcId:
        fromNpcZone = NPCToons.getNPCZone(fromNpcId)
        fromBranchId = ZoneUtil.getCanonicalBranchZone(fromNpcZone)
    toNpcZone = NPCToons.getNPCZone(toNpcId)
    toBranchId = ZoneUtil.getCanonicalBranchZone(toNpcZone)
    toNpcName, toHoodName, toBuildingArticle, toBuildingName, toStreetTo, toStreetName, isInPlayground = getNpcInfo(toNpcId)
    if fromBranchId == toBranchId:
        if isInPlayground:
            streetDesc = TTLocalizer.QuestsStreetLocationThisPlayground
        else:
            streetDesc = TTLocalizer.QuestsStreetLocationThisStreet
    elif isInPlayground:
        streetDesc = TTLocalizer.QuestsStreetLocationNamedPlayground % toHoodName
    else:
        streetDesc = TTLocalizer.QuestsStreetLocationNamedStreet % {'toStreetName': toStreetName,
         'toHoodName': toHoodName}
    paragraph = TTLocalizer.QuestsLocationParagraph % {'building': TTLocalizer.QuestsLocationBuilding % toNpcName,
     'buildingName': toBuildingName,
     'buildingVerb': TTLocalizer.QuestsLocationBuildingVerb,
     'street': streetDesc}
    return (paragraph, toBuildingName, streetDesc)

def fillInQuestNames(text, avName = None, fromNpcId = None, toNpcId = None):
    text = copy.deepcopy(text)
    if avName != None:
        text = text.replace('_avName_', avName)
    if toNpcId:
        if toNpcId == ToonHQ:
            toNpcName = TTLocalizer.QuestsHQOfficerFillin
            where = TTLocalizer.QuestsHQWhereFillin
            buildingName = TTLocalizer.QuestsHQBuildingNameFillin
            streetDesc = TTLocalizer.QuestsHQLocationNameFillin
        else:
            toNpcName = str(NPCToons.getNPCName(toNpcId))
            where, buildingName, streetDesc = getNpcLocationDialog(fromNpcId, toNpcId)
        text = text.replace('_toNpcName_', toNpcName)
        text = text.replace('_where_', where)
        text = text.replace('_buildingName_', buildingName)
        text = text.replace('_streetDesc_', streetDesc)
    return text
