from panda3d.core import *
from otp.nametag.NametagGroup import NametagGroup
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.hood import ZoneUtil
from toontown.toon import Toon
from direct.distributed import DistributedObject
from toontown.toon import NPCToons
from toontown.quest import Quests
from direct.distributed import ClockDelta
from toontown.quest.QuestIcon import *
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
            self.questOffer = None
            self.mainQuest = None
            self.sideQuest = None
            self.questIcon = None

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
        if config.GetBool('smooth-animations', True):
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
        if av.animFSM.getCurrentState().getName() != 'neutral':
            av.setAnimState('neutral')
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

    def isBusy(self):
        return self.busy > 0

    def getNpcId(self):
        return self.npcId

    def setQuestOffer(self, questId):
        self.questOffer = questId
        if self.questIcon:
            self.questIcon.unload()
        self.questIcon = QuestIcon(typeId=Offer)
        self.questIcon.reparentTo(self)
        self.questIcon.setPos(0, 0, self.height + 2)
        self.questIcon.setScale(2.0)
        self.questIcon.start()

    def clearQuestOffer(self):
        self.questOffer = None
        if self.questIcon:
            self.questIcon.unload()
            self.questIcon = None

    def getQuestOffer(self):
        return self.questOffer

    def setMainQuest(self, questId):
        self.mainQuest = questId
        if self.questIcon:
            self.questIcon.unload()
        self.questIcon = QuestIcon(typeId=Main)
        self.questIcon.reparentTo(self)
        self.questIcon.setPos(0, 0, self.height + 2)
        self.questIcon.setScale(2.0)
        self.questIcon.start()

    def clearMainQuest(self):
        self.mainQuest = None
        if self.questIcon:
            self.questIcon.unload()
            self.questIcon = None

    def getMainQuest(self):
        return self.mainQuest

    def setSideQuest(self, questId):
        self.sideQuest = questId
        if self.questIcon:
            self.questIcon.unload()
        self.questIcon = QuestIcon(typeId=Bonus)
        self.questIcon.reparentTo(self)
        self.questIcon.setPos(0, 0, self.height + 2)
        self.questIcon.setScale(2.0)
        self.questIcon.start()

    def clearSideQuest(self):
        self.sideQuest = None
        if self.questIcon:
            self.questIcon.unload()
            self.questIcon = None

    def getSideQuest(self):
        return self.sideQuest

    def clearQuestIcon(self):
        if self.questOffer:
            self.clearQuestOffer()
        elif self.mainQuest:
            self.clearMainQuest()
        elif self.sideQuest:
            self.clearSideQuest()
