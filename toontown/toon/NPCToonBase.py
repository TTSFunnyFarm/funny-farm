from panda3d.core import *
from otp.nametag.NametagGroup import NametagGroup
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.hood import ZoneUtil
import Toon
from direct.distributed import DistributedObject
import NPCToons
# from toontown.quest import Quests
from direct.distributed import ClockDelta
# from toontown.quest import QuestParser
# from toontown.quest import QuestChoiceGui
from direct.interval.IntervalGlobal import *
import random, copy

class NPCToonBase(Toon.Toon):
    deferFor = 2

    def __init__(self):
        try:
            self.NPCToon_initialized
        except:
            self.NPCToon_initialized = 1
            Toon.Toon.__init__(self)
            self.__initCollisions()
            self.setPickable(0)
            self.setPlayerType(NametagGroup.CCNonPlayer)
            self.cSphereNode.setName(self.uniqueName('NPCToon'))
            self.detectAvatars()
            self.reparentTo(render)
            self.startLookAround()
            self.npcId = 0
            self.busy = 0

    def disable(self):
        self.ignore('enter' + self.cSphereNode.getName())
        Toon.Toon.disable(self)

    def delete(self):
        try:
            self.NPCToon_deleted
        except:
            self.NPCToon_deleted = 1
            self.__deleteCollisions()
            Toon.Toon.delete(self)

    def generateToon(self):
        self.setLODs()
        self.generateToonLegs()
        self.generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.rightHands = []
        self.leftHands = []
        self.headParts = []
        self.hipsParts = []
        self.torsoParts = []
        self.legsParts = []
        self.__bookActors = []
        self.__holeActors = []
        self.setBlend(frameBlend=True)

    def wantsSmoothing(self):
        return 0

    def detectAvatars(self):
        self.accept('enter' + self.cSphereNode.getName(), self.handleCollisionSphereEnter)

    def ignoreAvatars(self):
        self.ignore('enter' + self.cSphereNode.getName())

    def getCollSphereRadius(self):
        return 3.25

    def __initCollisions(self):
        self.cSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, self.getCollSphereRadius())
        self.cSphere.setTangible(0)
        self.cSphereNode = CollisionNode('cSphereNode')
        self.cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = self.attachNewNode(self.cSphereNode)
        self.cSphereNodePath.hide()
        self.cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)

    def __deleteCollisions(self):
        del self.cSphere
        del self.cSphereNode
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath

    def handleCollisionSphereEnter(self, collEntry):
        pass

    def setupAvatars(self, av):
        self.ignoreAvatars()
        av.disable()
        av.headsUp(self, 0, 0, 0)
        self.headsUp(av, 0, 0, 0)
        av.stopLookAround()
        av.lerpLookAt(Point3(-0.5, 4, 0), time=0.5)
        self.stopLookAround()
        self.lerpLookAt(Point3(av.getPos(self)), time=0.5)

    def freeAvatar(self):
        base.localAvatar.enable()

    def setPositionIndex(self, posIndex):
        self.posIndex = posIndex

    def _startZombieCheck(self):
        pass

    def _stopZombieCheck(self):
        pass

    def avatarEnter(self):
        pass

    def chooseQuestDialogReject(self):
        return random.choice(TTLocalizer.QuestsDefaultReject)

    def chooseQuestDialogTierNotDone(self):
        return random.choice(TTLocalizer.QuestsDefaultTierNotDone)

    def isBusy(self):
        return self.busy > 0

    def fillInQuestNames(self, text, avName = None, fromNpcId = None, toNpcId = None):
        ToonTailor = 999
        ToonHQ = 1000
        text = copy.deepcopy(text)
        if avName != None:
            text = text.replace('_avName_', avName)
        if toNpcId:
            if toNpcId == ToonHQ:
                toNpcName = TTLocalizer.QuestsHQOfficerFillin
                where = TTLocalizer.QuestsHQWhereFillin
                buildingName = TTLocalizer.QuestsHQBuildingNameFillin
                streetDesc = TTLocalizer.QuestsHQLocationNameFillin
            elif toNpcId == ToonTailor:
                toNpcName = TTLocalizer.QuestsTailorFillin
                where = TTLocalizer.QuestsTailorWhereFillin
                buildingName = TTLocalizer.QuestsTailorBuildingNameFillin
                streetDesc = TTLocalizer.QuestsTailorLocationNameFillin
            else:
                toNpcName = str(NPCToons.getNPCName(toNpcId))
                where, buildingName, streetDesc = self.getNpcLocationDialog(fromNpcId, toNpcId)
            text = text.replace('_toNpcName_', toNpcName)
            text = text.replace('_where_', where)
            text = text.replace('_buildingName_', buildingName)
            text = text.replace('_streetDesc_', streetDesc)
        return text

    def getNpcLocationDialog(self, fromNpcId, toNpcId):
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

    def getNpcInfo(self, npcId):
        npcName = NPCToons.getNPCName(npcId)
        npcZone = NPCToons.getNPCZone(npcId)
        hoodId = ZoneUtil.getCanonicalHoodId(npcZone)
        hoodName = base.cr.hoodMgr.getFullnameFromId(hoodId)
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
