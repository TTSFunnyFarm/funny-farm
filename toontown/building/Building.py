from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from otp.nametag.NametagGroup import NametagGroup
from otp.nametag.Nametag import Nametag
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.quest.QuestIcon import *
from toontown.suit import Suit, SuitDNA
from Elevator import Elevator
from ElevatorConstants import *
from ElevatorUtils import *
from SuitBuildingGlobals import *
import time, random

class Building(DirectObject):
    notify = directNotify.newCategory('Building')
    TOON_STATE = 'toon'
    SUIT_STATE = 'suit'
    ELITE_STATE = 'elite'
    SUIT_INIT_HEIGHT = 125
    TAKEOVER_SFX_PREFIX = 'phase_5/audio/sfx/'

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.block = self.getBlock()
        self.nametag = None
        self.questOffer = None
        self.mainQuest = None
        self.sideQuest = None
        self.questIcon = None
        self.questIcon2 = None
        self.townTopLevel = base.cr.playGame.getActiveZone().geom
        self.mode = None
        self.suitDoorOrigin = None
        self.elevator = None
        self.elevatorModel = None
        self.elevatorNodePath = None
        self.transitionTrack = None
        self.cogDropSound = None
        self.cogLandSound = None
        self.cogSettleSound = None
        self.cogWeakenSound = None
        self.toonGrowSound = None
        self.toonSettleSound = None
        self.victor = None

    def load(self):
        self.setupNametag()

    def unload(self):
        self.clearNametag()
        self.clearQuestIcon()

    def delete(self):
        if self.elevator:
            self.elevator.delete()
            del self.elevator
        if self.elevatorNodePath:
            self.elevatorNodePath.removeNode()
            del self.elevatorNodePath
            del self.elevatorModel
            del self.leftDoor
            del self.rightDoor
        del self.suitDoorOrigin
        self.cleanupSuitBuilding()
        self.unloadSfx()

    def getBlock(self):
        block = str(self.zoneId)
        block = int(block[2:])
        return block

    def getBuildingNodePath(self):
        geom = base.cr.playGame.getActiveZone().geom
        np = geom.find('**/tb%d:toon_landmark*;+s' % self.block)
        if np.isEmpty():
            np = geom.find('**/sz%d:toon_landmark*;+s' % self.block)
        return np

    def setState(self, state):
        if state not in [self.TOON_STATE, self.SUIT_STATE, self.ELITE_STATE]:
            self.notify.warning('Invalid state change attempted: %s' % str(state))
            return
        if self.mode == self.TOON_STATE:
            if state == self.SUIT_STATE:
                self.animToSuit()
            elif state == self.ELITE_STATE:
                self.animToElite()
            else:
                return
        elif self.mode == self.SUIT_STATE:
            if state == self.TOON_STATE:
                self.animToToon()
            else:
                return
        elif self.mode == self.ELITE_STATE:
            if state == self.TOON_STATE:
                self.animToToonFromElite()
            else:
                return
        self.mode = state

    def setupNametag(self):
        if self.nametag == None:
            self.nametag = NametagGroup()
            self.nametag.setFont(ToontownGlobals.getBuildingNametagFont())
            if TTLocalizer.BuildingNametagShadow:
                self.nametag.setShadow(*TTLocalizer.BuildingNametagShadow)
            self.nametag.setContents(Nametag.CName)
            self.nametag.setColorCode(NametagGroup.CCToonBuilding)
            self.nametag.setActive(0)
            self.nametag.setAvatar(self.getBuildingNodePath().find('**/*door_origin*'))
            self.nametag.setObjectCode(self.block)
            name = TTLocalizer.zone2TitleDict.get(self.zoneId, '')
            self.nametag.setName(name)
            self.nametag.manage(base.marginManager)
        return

    def clearNametag(self):
        if self.nametag != None:
            self.nametag.unmanage(base.marginManager)
            self.nametag.setAvatar(NodePath())
            self.nametag.destroy()
            self.nametag = None
        return

    def setQuestOffer(self, questId, hq=0):
        self.questOffer = questId
        if self.questIcon:
            self.questIcon.unload()
        self.questIcon = QuestIcon(typeId=Offer)
        if hq:
            self.questIcon.reparentTo(self.getBuildingNodePath().find('**/door_origin_0'))
            self.questIcon.setPos(0, -3.5, 10)
            self.questIcon.setScale(3.0)
            self.questIcon.start()
            self.questIcon2 = QuestIcon(typeId=Offer)
            self.questIcon2.reparentTo(self.getBuildingNodePath().find('**/door_origin_1'))
            self.questIcon2.setPos(0, -3.5, 10)
            self.questIcon2.setScale(3.0)
            self.questIcon2.start()
        else:
            self.questIcon.reparentTo(self.getBuildingNodePath().find('**/*door_origin*'))
            self.questIcon.setPos(0, -1, 10)
            self.questIcon.setScale(3.0)
            self.questIcon.start()

    def clearQuestOffer(self):
        self.questOffer = None
        if self.questIcon:
            self.questIcon.unload()
            self.questIcon = None
        if self.questIcon2:
            self.questIcon2.unload()
            self.questIcon2 = None

    def getQuestOffer(self):
        return self.questOffer

    def setMainQuest(self, questId):
        self.mainQuest = questId
        if self.questIcon:
            self.questIcon.unload()
        self.questIcon = QuestIcon(typeId=Main)
        self.questIcon.reparentTo(self.getBuildingNodePath().find('**/*door_origin*'))
        self.questIcon.setPos(0, -1, 10)
        self.questIcon.setScale(3.0)
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
        self.questIcon.reparentTo(self.getBuildingNodePath().find('**/*door_origin*'))
        self.questIcon.setPos(0, -1, 10)
        self.questIcon.setScale(3.0)
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

    def _getMinMaxFloors(self, difficulty):
        return SuitBuildingInfo[difficulty][0]

    def suitTakeOver(self, suitTrack, difficulty, buildingHeight):
        difficulty = min(difficulty, len(SuitBuildingInfo) - 1)
        minFloors, maxFloors = self._getMinMaxFloors(difficulty)
        if buildingHeight == None:
            numFloors = random.randint(minFloors, maxFloors)
        else:
            numFloors = buildingHeight + 1
            if numFloors < minFloors or numFloors > maxFloors:
                numFloors = random.randint(minFloors, maxFloors)
        self.track = suitTrack
        self.difficulty = difficulty
        self.numFloors = numFloors
        self.becameSuitTime = time.time()
        self.setState('suit')
        return

    def eliteTakeOver(self, suitTrack):
        pass

    def toonTakeOver(self):
        self.setState('toon')

    def getNodePaths(self):
        nodePath = []
        npc = self.townTopLevel.findAllMatches('**/?b' + str(self.block) + ':*_DNARoot;+s')
        for i in range(npc.getNumPaths()):
            nodePath.append(npc.getPath(i))

        return nodePath

    def loadElevator(self, newNP, cogdo = False):
        self.floorIndicator = [None,
         None,
         None,
         None,
         None]
        self.elevatorNodePath = hidden.attachNewNode('elevatorNodePath')
        if cogdo:
            self.elevatorModel = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB')
        else:
            self.elevatorModel = loader.loadModel('phase_4/models/modules/elevator')
            npc = self.elevatorModel.findAllMatches('**/floor_light_?;+s')
            for i in range(npc.getNumPaths()):
                np = npc.getPath(i)
                floor = int(np.getName()[-1:]) - 1
                self.floorIndicator[floor] = np

        self.suitDoorOrigin = newNP.find('**/*_door_origin')
        self.elevatorNodePath.reparentTo(self.suitDoorOrigin)
        self.normalizeElevator()
        
        self.elevator = Elevator()
        self.elevator.setup(self.elevatorModel, self.elevatorNodePath, self.track, self.difficulty, self.numFloors, elite=cogdo)
        self.elevator.showCorpIcon()
        self.leftDoor = self.elevator.leftDoor
        self.rightDoor = self.elevator.rightDoor
        return

    def loadAnimToSuitSfx(self):
        if self.cogDropSound == None:
            self.cogDropSound = base.loader.loadSfx(self.TAKEOVER_SFX_PREFIX + 'cogbldg_drop.ogg')
            self.cogLandSound = base.loader.loadSfx(self.TAKEOVER_SFX_PREFIX + 'cogbldg_land.ogg')
            self.cogSettleSound = base.loader.loadSfx(self.TAKEOVER_SFX_PREFIX + 'cogbldg_settle.ogg')
            self.openSfx = base.loader.loadSfx('phase_5/audio/sfx/elevator_door_open.ogg')
        return

    def loadAnimToToonSfx(self):
        if self.cogWeakenSound == None:
            self.cogWeakenSound = base.loader.loadSfx(self.TAKEOVER_SFX_PREFIX + 'cogbldg_weaken.ogg')
            self.toonGrowSound = base.loader.loadSfx(self.TAKEOVER_SFX_PREFIX + 'toonbldg_grow.ogg')
            self.toonSettleSound = base.loader.loadSfx(self.TAKEOVER_SFX_PREFIX + 'toonbldg_settle.ogg')
            self.openSfx = base.loader.loadSfx('phase_5/audio/sfx/elevator_door_open.ogg')
        return

    def unloadSfx(self):
        if self.cogDropSound != None:
            self.cogDropSound = None
            self.cogLandSound = None
            self.cogSettleSound = None
            self.openSfx = None
        if self.cogWeakenSound != None:
            self.cogWeakenSound = None
            self.toonGrowSound = None
            self.toonSettleSound = None
            self.openSfx = None
        return

    def _deleteTransitionTrack(self):
        if self.transitionTrack:
            self.transitionTrack = None
        return

    def animToSuit(self):
        self.stopTransition()
        if self.mode != 'toon':
            self.setToToon()
        self.loadAnimToSuitSfx()
        sideBldgNodes = self.getNodePaths()
        nodePath = self.townTopLevel.find(self.getSbSearchString())
        newNP = self.setupSuitBuilding(nodePath)
        closeDoors(self.leftDoor, self.rightDoor)
        newNP.stash()
        sideBldgNodes.append(newNP)
        soundPlayed = 0
        tracks = Parallel(name='toSuitTrack-%d' % self.zoneId)
        for i in sideBldgNodes:
            name = i.getName()
            timeForDrop = TO_SUIT_BLDG_TIME * 0.85
            if name[0] == 's':
                showTrack = Sequence(name='ToSuitFlatsTrack-%d-%d' % (self.zoneId, sideBldgNodes.index(i)))
                initPos = Point3(0, 0, self.SUIT_INIT_HEIGHT) + i.getPos()
                showTrack.append(Func(i.setPos, initPos))
                showTrack.append(Func(i.unstash))
                showTrack.append(Func(i.show))
                if i == sideBldgNodes[len(sideBldgNodes) - 1]:
                    showTrack.append(Func(self.normalizeElevator))
                if not soundPlayed:
                    showTrack.append(Func(base.playSfx, self.cogDropSound, 0, 1, None, 0.0))
                showTrack.append(LerpPosInterval(i, timeForDrop, i.getPos(), name='ToSuitAnim-%d-%d' % (self.zoneId, sideBldgNodes.index(i))))
                if not soundPlayed:
                    showTrack.append(Func(base.playSfx, self.cogLandSound, 0, 1, None, 0.0))
                showTrack.append(self.createBounceTrack(i, 2, 0.65, TO_SUIT_BLDG_TIME - timeForDrop, slowInitBounce=1.0))
                if not soundPlayed:
                    showTrack.append(Func(base.playSfx, self.cogSettleSound, 0, 1, None, 0.0))
                showTrack.append(Func(self.elevator.openDoors))
                showTrack.append(Func(self.elevator.addActive))
                tracks.append(showTrack)
                if not soundPlayed:
                    soundPlayed = 1
            elif name[0] == 't':
                hideTrack = Sequence(name='ToSuitToonFlatsTrack-%d' % self.zoneId)
                timeTillSquish = (self.SUIT_INIT_HEIGHT - 20.0) / self.SUIT_INIT_HEIGHT
                timeTillSquish *= timeForDrop
                hideTrack.append(LerpFunctionInterval(self.adjustColorScale, fromData=1, toData=0.25, duration=timeTillSquish, extraArgs=[i]))
                hideTrack.append(LerpScaleInterval(i, timeForDrop - timeTillSquish, Vec3(1, 1, 0.01)))
                hideTrack.append(Func(i.stash))
                hideTrack.append(Func(i.setScale, Vec3(1)))
                hideTrack.append(Func(i.clearColorScale))
                tracks.append(hideTrack)

        self.stopTransition()
        self._deleteTransitionTrack()
        self.transitionTrack = tracks
        self.transitionTrack.start()
        return

    def setupSuitBuilding(self, nodePath):
        suitNP = loader.loadModel(FunnyFarmGlobals.SuitBuildingMap[self.track])
        newParentNP = self.getBuildingNodePath().getParent()
        suitBuildingNP = suitNP.copyTo(newParentNP)
        suitBuildingNP.hide()
        buildingTitle = TTLocalizer.zone2TitleDict.get(self.zoneId, '')
        if not buildingTitle:
            buildingTitle = TTLocalizer.CogsInc
        else:
            buildingTitle += TTLocalizer.CogsIncExt
        buildingTitle += '\n%s' % SuitDNA.getDeptFullname(self.track)
        textNode = TextNode('sign')
        textNode.setTextColor(1.0, 1.0, 1.0, 1.0)
        textNode.setFont(ToontownGlobals.getSuitFont())
        textNode.setAlign(TextNode.ACenter)
        textNode.setWordwrap(17.0)
        textNode.setText(buildingTitle)
        textHeight = textNode.getHeight()
        zScale = (textHeight + 2) / 3.0
        signOrigin = suitBuildingNP.find('**/sign_origin;+s')
        backgroundNP = loader.loadModel('phase_5/models/modules/suit_sign').find('**/suitSign')
        backgroundNP.reparentTo(signOrigin)
        backgroundNP.setPosHprScale(0.0, 0.0, textHeight * 0.8 / zScale, 0.0, 0.0, 0.0, 8.0, 8.0, 8.0 * zScale)
        backgroundNP.node().setEffect(DecalEffect.make())
        signTextNodePath = backgroundNP.attachNewNode(textNode.generate())
        signTextNodePath.setPosHprScale(0.0, 0.0, -0.21 + textHeight * 0.1 / zScale, 0.0, 0.0, 0.0, 0.1, 0.1, 0.1 / zScale)
        signTextNodePath.setColor(1.0, 1.0, 1.0, 1.0)
        frontNP = suitBuildingNP.find('**/*_front/+GeomNode;+s')
        backgroundNP.wrtReparentTo(frontNP)
        frontNP.node().setEffect(DecalEffect.make())
        suitBuildingNP.setName('sb' + str(self.block) + ':_landmark__DNARoot')
        suitBuildingNP.setPosHprScale(nodePath, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        suitBuildingNP.flattenMedium()
        self.loadElevator(suitBuildingNP)
        return suitBuildingNP

    def cleanupSuitBuilding(self):
        if hasattr(self, 'floorIndicator'):
            del self.floorIndicator

    def setupCogdo(self, nodePath):
        pass

    def adjustColorScale(self, scale, node):
        node.setColorScale(scale, scale, scale, 1)

    def animToElite(self):
        pass

    def setupElite(self):
        pass

    def animToToon(self):
        self.stopTransition()
        if self.mode != 'suit':
            self.setToSuit()
        self.loadAnimToToonSfx()
        suitSoundPlayed = 0
        toonSoundPlayed = 0
        bldgNodes = self.getNodePaths()
        tracks = Parallel()
        for i in bldgNodes:
            name = i.getName()
            if name[0] == 's':
                hideTrack = Sequence(name='ToToonSuitFlatsTrack-%d' % self.zoneId)
                if not suitSoundPlayed:
                    hideTrack.append(Func(base.playSfx, self.cogWeakenSound, 0, 1, None, 0.0))
                hideTrack.append(self.createBounceTrack(i, 3, 1.2, TO_TOON_BLDG_TIME * 0.05, slowInitBounce=0.0))
                hideTrack.append(self.createBounceTrack(i, 5, 0.8, TO_TOON_BLDG_TIME * 0.1, slowInitBounce=0.0))
                hideTrack.append(self.createBounceTrack(i, 7, 1.2, TO_TOON_BLDG_TIME * 0.17, slowInitBounce=0.0))
                hideTrack.append(self.createBounceTrack(i, 9, 1.2, TO_TOON_BLDG_TIME * 0.18, slowInitBounce=0.0))
                realScale = i.getScale()
                hideTrack.append(LerpScaleInterval(i, TO_TOON_BLDG_TIME * 0.1, Vec3(realScale[0], realScale[1], 0.01)))
                if name.find(':_landmark__') != -1:
                    hideTrack.append(Func(i.removeNode))
                elif name.find('_landmark_') != -1:
                    hideTrack.append(Func(i.stash))
                    hideTrack.append(Func(i.setScale, Vec3(i.getSx(), i.getSy(), 1.0)))
                else:
                    hideTrack.append(Func(i.stash))
                    hideTrack.append(Func(i.setScale, Vec3(1)))
                if not suitSoundPlayed:
                    suitSoundPlayed = 1
                tracks.append(hideTrack)
            elif name[0] == 't':
                hideTrack = Sequence(name='ToToonFlatsTrack-%d' % self.zoneId)
                hideTrack.append(Wait(TO_TOON_BLDG_TIME * 0.5))
                if not toonSoundPlayed:
                    hideTrack.append(Func(base.playSfx, self.toonGrowSound, 0, 1, None, 0.0))
                hideTrack.append(Func(i.unstash))
                hideTrack.append(Func(i.setScale, Vec3(1, 1, 0.01)))
                if not toonSoundPlayed:
                    hideTrack.append(Func(base.playSfx, self.toonSettleSound, 0, 1, None, 0.0))
                hideTrack.append(self.createBounceTrack(i, 11, 1.2, TO_TOON_BLDG_TIME * 0.5, slowInitBounce=4.0))
                tracks.append(hideTrack)
                if not toonSoundPlayed:
                    toonSoundPlayed = 1

        self.stopTransition()
        bldgMTrack = tracks
        localToonIsVictor = self.localToonIsVictor()
        if localToonIsVictor:
            camTrack = self.walkOutCameraTrack()
        # victoryRunTrack = self.getVictoryRunTrack()
        trackName = 'toToonTrack-%d' % self.zoneId
        self._deleteTransitionTrack()
        if localToonIsVictor:
            freedomTrack1 = Func(self.cr.playGame.getPlace().setState, 'walk')
            freedomTrack2 = Func(base.localAvatar.wrtReparentTo, render)
            self.transitionTrack = Parallel(camTrack, Sequence(victoryRunTrack, bldgMTrack, freedomTrack1, freedomTrack2), name=trackName)
        else:
            # self.transitionTrack = Sequence(victoryRunTrack, bldgMTrack, name=trackName)
            self.transitionTrack = bldgMTrack
        self.transitionTrack.start()
        return

    def animToToonFromElite(self):
        pass

    def localToonIsVictor(self):
        return self.victor == base.localAvatar.getDoId()

    def createBounceTrack(self, nodeObj, numBounces, startScale, totalTime, slowInitBounce = 0.0):
        if not nodeObj or numBounces < 1 or startScale == 0.0 or totalTime == 0:
            self.notify.warning('createBounceTrack called with invalid parameter')
            return
        result = Sequence()
        numBounces += 1
        if slowInitBounce:
            bounceTime = totalTime / (numBounces + slowInitBounce - 1.0)
        else:
            bounceTime = totalTime / float(numBounces)
        if slowInitBounce:
            currTime = bounceTime * float(slowInitBounce)
        else:
            currTime = bounceTime
        realScale = nodeObj.getScale()
        currScaleDiff = startScale - realScale[2]
        for currBounceScale in range(numBounces):
            if currBounceScale == numBounces - 1:
                currScale = realScale[2]
            elif currBounceScale % 2:
                currScale = realScale[2] - currScaleDiff
            else:
                currScale = realScale[2] + currScaleDiff
            result.append(LerpScaleInterval(nodeObj, currTime, Vec3(realScale[0], realScale[1], currScale), blendType='easeInOut'))
            currScaleDiff *= 0.5
            currTime = bounceTime

        return result

    def stopTransition(self):
        if self.transitionTrack:
            self.transitionTrack.finish()
            self._deleteTransitionTrack()

    def setToSuit(self):
        self.stopTransition()
        if self.mode == 'suit':
            return
        self.mode = 'suit'
        nodes = self.getNodePaths()
        for i in nodes:
            name = i.getName()
            if name[0] == 's':
                if name.find(':_landmark__') != -1:
                    i.removeNode()
                else:
                    i.unstash()
            elif name[0] == 't':
                if name.find('_landmark_') != -1:
                    i.stash()
                else:
                    i.stash()
            elif name[0] == 'c':
                if name.find(':_landmark__') != -1:
                    i.removeNode()
                else:
                    i.stash()

        npc = self.townTopLevel.findAllMatches(self.getSbSearchString())
        for i in range(npc.getNumPaths()):
            nodePath = npc.getPath(i)
            self.setupSuitBuilding(nodePath).show()
            self.elevator.addActive()

    def setToElite(self):
        self.stopTransition()
        if self.mode == 'elite':
            return
        self.mode = 'elite'
        nodes = self.getNodePaths()
        for i in nodes:
            name = i.getName()
            if name[0] == 'c':
                if name.find(':_landmark__') != -1:
                    i.removeNode()
                else:
                    i.unstash()
            elif name[0] == 't':
                if name.find('_landmark_') != -1:
                    i.stash()
                else:
                    i.stash()
            elif name[0] == 's':
                if name.find(':_landmark__') != -1:
                    i.removeNode()
                else:
                    i.stash()

        for np in nodes:
            if not np.isEmpty():
                np.setColorScale(0.6, 0.6, 0.6, 1.0)

        npc = self.townTopLevel.findAllMatches(self.getSbSearchString())
        for i in range(npc.getNumPaths()):
            nodePath = npc.getPath(i)
            self.setupCogdo(nodePath) #.show()

    def setToToon(self):
        self.stopTransition()
        if self.mode == 'toon':
            return
        self.mode = 'toon'
        self.suitDoorOrigin = None
        nodes = self.getNodePaths()
        for i in nodes:
            i.clearColorScale()
            name = i.getName()
            if name[0] == 's':
                if name.find(':_landmark__') != -1:
                    i.removeNode()
                else:
                    i.stash()
            elif name[0] == 't':
                if name.find('_landmark_') != -1:
                    i.unstash()
                else:
                    i.unstash()
            elif name[0] == 'c':
                if name.find(':_landmark__') != -1:
                    i.removeNode()
                else:
                    i.stash()

        return

    def normalizeElevator(self):
        self.elevatorNodePath.setScale(render, Vec3(1, 1, 1))
        self.elevatorNodePath.setPosHpr(0, 0, 0, 0, 0, 0)

    def getSbSearchString(self):
        zone = self.getBuildingNodePath().getAncestor(2)
        result = '**/' + zone.getName() + '/buildings/sb' + str(self.block) + ':*_landmark_*_DNARoot;+s'
        return result
