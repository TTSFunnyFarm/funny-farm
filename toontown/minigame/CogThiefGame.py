from panda3d.core import Point3, CollisionSphere, CollisionNode, CollisionHandlerEvent, NodePath, TextNode
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Wait, LerpFunctionInterval, LerpHprInterval, Sequence, Parallel, Func, SoundInterval, ActorInterval, ProjectileInterval, Track, LerpScaleInterval, WaitInterval, LerpPosHprInterval
from direct.gui.DirectGui import DirectLabel
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.showbase import RandomNumGen
from direct.task import Task
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownTimer
from toontown.minigame import CogThiefGameToonSD
from toontown.minigame.OrthoDrive import OrthoDrive
from toontown.minigame.OrthoWalk import OrthoWalk
from toontown.minigame import CogThiefGameGlobals
from toontown.minigame import CogThief
from toontown.minigame.Minigame import Minigame
from toontown.minigame import Trajectory
from toontown.minigame import MinigameGlobals
from toontown.minigame import CogThiefWalk
import random
CTGG = CogThiefGameGlobals

class CogThiefGame(Minigame):
    notify = directNotify.newCategory('CogThiefGame')
    ToonSpeed = CTGG.ToonSpeed
    StageHalfWidth = 200.0
    StageHalfHeight = 100.0
    BarrelScale = 0.25
    TOON_Z = 0
    UPDATE_SUITS_TASK = 'CogThiefGameUpdateSuitsTask'
    REWARD_COUNTDOWN_TASK = 'cogThiefGameRewardCountdown'
    ControlKeyLimitTime = 1.0
    ExplodeWaitTime = 6.0 + CTGG.LyingDownDuration

    def __init__(self):
        Minigame.__init__(self)
        self.gameFSM = ClassicFSM.ClassicFSM('CogThiefGame', [State.State('off', self.enterOff, self.exitOff, ['play']), State.State('play', self.enterPlay, self.exitPlay, ['cleanup']), State.State('cleanup', self.enterCleanup, self.exitCleanup, [])], 'off', 'cleanup')
        self.addChildGameFSM(self.gameFSM)
        self.cameraTopView = (0, 0, 53, 0, -90.0, 0)
        self.barrels = []
        self.cogInfo = {}
        self.barrelInfo = {}
        self.initBarrelInfo()
        self.lastTimeControlPressed = 0
        self.stolenBarrels = []
        self.useOrthoWalk = base.config.GetBool('cog-thief-ortho', 1)
        self.resultIval = None
        self.gameIsEnding = False
        self.scoreDict = {}
        self.__textGen = TextNode('cogThiefGame')
        self.__textGen.setFont(ToontownGlobals.getSignFont())
        self.__textGen.setAlign(TextNode.ACenter)
        return

    def getTitle(self):
        return TTLocalizer.CogThiefGameTitle

    def getInstructions(self):
        return TTLocalizer.CogThiefGameInstructions

    def getMaxDuration(self):
        return 0

    def load(self):
        self.notify.debug('load')
        Minigame.load(self)
        self.music = base.loader.loadMusic('phase_4/audio/bgm/MG_CogThief.ogg')
        self.initCogInfo()
        for barrelIndex in range(CTGG.NumBarrels):
            barrel = loader.loadModel('phase_4/models/minigames/cogthief_game_gagTank')
            barrel.setPos(CTGG.BarrelStartingPositions[barrelIndex])
            barrel.setScale(self.BarrelScale)
            barrel.reparentTo(render)
            barrel.setTag('barrelIndex', str(barrelIndex))
            collSphere = CollisionSphere(0, 0, 0, 4)
            collSphere.setTangible(0)
            name = 'BarrelSphere-%d' % barrelIndex
            collSphereName = self.uniqueName(name)
            collNode = CollisionNode(collSphereName)
            collNode.setFromCollideMask(CTGG.BarrelBitmask)
            collNode.addSolid(collSphere)
            colNp = barrel.attachNewNode(collNode)
            handler = CollisionHandlerEvent()
            handler.setInPattern('barrelHit-%fn')
            base.cTrav.addCollider(colNp, handler)
            self.accept('barrelHit-' + collSphereName, self.handleEnterBarrel)
            nodeToHide = '**/gagMoneyTen'
            if barrelIndex % 2:
                nodeToHide = '**/gagMoneyFive'
            iconToHide = barrel.find(nodeToHide)
            if not iconToHide.isEmpty():
                iconToHide.hide()
            self.barrels.append(barrel)

        self.gameBoard = loader.loadModel('phase_4/models/minigames/cogthief_game')
        self.gameBoard.find('**/floor_TT').hide()
        self.gameBoard.find('**/floor_DD').hide()
        self.gameBoard.find('**/floor_DG').hide()
        self.gameBoard.find('**/floor_MM').hide()
        self.gameBoard.find('**/floor_BR').hide()
        self.gameBoard.find('**/floor_DL').hide()
        zone = self.getSafezoneId()
        if zone == ToontownGlobals.ToontownCentral:
            self.gameBoard.find('**/floor_TT').show()
        elif zone == ToontownGlobals.DonaldsDock:
            self.gameBoard.find('**/floor_DD').show()
        elif zone == ToontownGlobals.DaisyGardens:
            self.gameBoard.find('**/floor_DG').show()
        elif zone == ToontownGlobals.MinniesMelodyland:
            self.gameBoard.find('**/floor_MM').show()
        elif zone == ToontownGlobals.TheBrrrgh:
            self.gameBoard.find('**/floor_BR').show()
        elif zone == ToontownGlobals.DonaldsDreamland:
            self.gameBoard.find('**/floor_DL').show()
        else:
            self.gameBoard.find('**/floor_TT').show()
        self.toonSDs = {}
        avId = self.localAvId
        toonSD = CogThiefGameToonSD.CogThiefGameToonSD(avId, self)
        self.toonSDs[avId] = toonSD
        toonSD.load()
        self.loadCogs()
        self.toonHitTracks = {}
        self.toonPieTracks = {}
        self.sndOof = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_hit_dirt.ogg')
        self.sndRewardTick = base.loader.loadSfx('phase_3.5/audio/sfx/tick_counter.ogg')
        self.sndPerfect = base.loader.loadSfx('phase_4/audio/sfx/ring_perfect.ogg')
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.posInTopRightCorner()
        self.timer.hide()
        purchaseModels = loader.loadModel('phase_4/models/gui/purchase_gui')
        self.jarImage = purchaseModels.find('**/Jar')
        self.jarImage.reparentTo(hidden)
        self.rewardPanel = DirectLabel(parent=hidden, relief=None, pos=(-0.173, 0.0, -0.55), scale=0.65, text='', text_scale=0.2, text_fg=(0.95, 0.95, 0, 1), text_pos=(0, -.13), text_font=ToontownGlobals.getSignFont(), image=self.jarImage)
        self.rewardPanelTitle = DirectLabel(parent=self.rewardPanel, relief=None, pos=(0, 0, 0.06), scale=0.08, text=TTLocalizer.CannonGameReward, text_fg=(0.95, 0.95, 0, 1), text_shadow=(0, 0, 0, 1))
        return

    def unload(self):
        self.notify.debug('unload')
        Minigame.unload(self)
        del self.music
        self.removeChildGameFSM(self.gameFSM)
        del self.gameFSM
        self.gameBoard.removeNode()
        del self.gameBoard
        for barrel in self.barrels:
            barrel.removeNode()

        del self.barrels
        for avId in self.toonSDs.keys():
            toonSD = self.toonSDs[avId]
            toonSD.unload()

        del self.toonSDs
        self.timer.destroy()
        del self.timer
        self.rewardPanel.destroy()
        del self.rewardPanel
        self.jarImage.removeNode()
        del self.jarImage
        del self.sndRewardTick

    def onstage(self):
        self.notify.debug('onstage')
        Minigame.onstage(self)
        self.gameBoard.reparentTo(render)
        lt = base.localAvatar
        lt.reparentTo(render)
        self.__placeToon(self.localAvId)
        lt.setSpeed(0, 0)
        self.moveCameraToTop()
        toonSD = self.toonSDs[self.localAvId]
        toonSD.enter()
        toonSD.fsm.request('normal')
        self.stopGameWalk()
        for cogIndex in range(self.getNumCogs()):
            suit = self.cogInfo[cogIndex]['suit'].suit
            pos = self.cogInfo[cogIndex]['pos']
            suit.reparentTo(self.gameBoard)
            suit.setPos(pos)

        for avId in self.avIdList:
            self.toonHitTracks[avId] = Wait(0.1)

        self.toonRNGs = []
        for i in range(self.numPlayers):
            self.toonRNGs.append(RandomNumGen.RandomNumGen(self.randomNumGen))

        self.sndTable = {'hitBySuit': [None] * self.numPlayers,
         'falling': [None] * self.numPlayers}
        for i in range(self.numPlayers):
            self.sndTable['hitBySuit'][i] = base.loader.loadSfx('phase_4/audio/sfx/MG_Tag_C.ogg')
            self.sndTable['falling'][i] = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_whizz.ogg')

        musicMgr.playMusic(self.music, looping=1, volume=0.8)
        self.introTrack = self.getIntroTrack()
        self.introTrack.start()
        return

    def offstage(self):
        self.notify.debug('offstage')
        self.gameBoard.hide()
        self.music.stop()
        for barrel in self.barrels:
            barrel.hide()

        for avId in self.toonSDs.keys():
            self.toonSDs[avId].exit()

        for avId in self.avIdList:
            av = self.getAvatar()
            if av:
                av.resetLOD()

        self.timer.reparentTo(hidden)
        self.rewardPanel.reparentTo(hidden)
        if self.introTrack.isPlaying():
            self.introTrack.finish()
        del self.introTrack
        Minigame.offstage(self)

    def handleDisabledAvatar(self, avId):
        self.notify.debug('handleDisabledAvatar')
        self.notify.debug('avatar ' + str(avId) + ' disabled')
        self.toonSDs[avId].exit(unexpectedExit=True)
        del self.toonSDs[avId]
        Minigame.handleDisabledAvatar(self, avId)

    def setGameReady(self):
        if not self.hasLocalToon:
            return
        self.notify.debug('setGameReady')
        #self.initCogInfo()
        if Minigame.setGameReady(self):
            return
        for avId in self.remoteAvIdList:
            toon = self.getAvatar()
            if toon:
                toon.reparentTo(render)
                self.__placeToon(avId)
                toon.useLOD(1000)
                toonSD = CogThiefGameToonSD.CogThiefGameToonSD(avId, self)
                self.toonSDs[avId] = toonSD
                toonSD.load()
                toonSD.enter()
                toonSD.fsm.request('normal')
                toon.startSmooth()

    def setGameStart(self, timestamp):
        if not self.hasLocalToon:
            return
        self.notify.debug('setGameStart')
        Minigame.setGameStart(self, timestamp)
        if not base.config.GetBool('cog-thief-endless', 0):
            self.timer.show()
            self.timer.countdown(CTGG.GameTime, self.__gameTimerExpired)
        self.clockStopTime = None
        self.rewardPanel.reparentTo(base.a2dTopRight)
        self.scoreMult = MinigameGlobals.getScoreMult(base.cr.playGame.hood.TTZoneId)
        self.__startRewardCountdown()
        if self.introTrack.isPlaying():
            self.introTrack.finish()
        self.gameFSM.request('play')
        return

    def enterOff(self):
        self.notify.debug('enterOff')

    def exitOff(self):
        pass

    def enterPlay(self):
        self.notify.debug('enterPlay')
        self.startGameWalk()
        self.spawnUpdateSuitsTask()
        self.startSuitGoals()
        self.accept('control', self.controlKeyPressed)
        self.pieHandler = CollisionHandlerEvent()
        self.pieHandler.setInPattern('pieHit-%fn')

    def exitPlay(self):
        self.ignore('control')
        if self.resultIval and self.resultIval.isPlaying():
            self.resultIval.finish()
            self.resultIval = None
        return

    def enterCleanup(self):
        self.__killRewardCountdown()
        if hasattr(self, 'jarIval'):
            self.jarIval.finish()
            del self.jarIval
        for key in self.toonHitTracks:
            ival = self.toonHitTracks[key]
            if ival.isPlaying():
                ival.finish()

        self.toonHitTracks = {}
        for key in self.toonPieTracks:
            ival = self.toonPieTracks[key]
            if ival.isPlaying():
                ival.finish()

        self.toonPieTracks = {}
        for key in self.cogInfo:
            cogThief = self.cogInfo[key]['suit']
            cogThief.cleanup()

        self.removeUpdateSuitsTask()
        self.notify.debug('enterCleanup')
        taskMgr.remove(self.uniqueName('gameTimer'))

    def exitCleanup(self):
        pass

    def gameOver(self):
        self.notify.debug('gameOver')
        score = int(CTGG.calcScore(self.getCurrentGameTime()))
        for avId in self.avIdList:
            self.scoreDict[avId] = score

        if self.getNumBarrelsStolen() == 0:
            for avId in self.avIdList:
                self.scoreDict[avId] += CTGG.PerfectBonus[len(self.avIdList) - 1]

        self.numJellybeans = self.scoreDict[self.avIdList[0]]

        Minigame.gameOver(self)

    def __placeToon(self, avId):
        toon = self.getAvatar()
        if toon:
            index = self.avIdList.index(avId)
            toon.setPos(CTGG.ToonStartingPositions[index])
            toon.setHpr(0, 0, 0)

    def moveCameraToTop(self):
        camera.reparentTo(render)
        p = self.cameraTopView
        camera.setPosHpr(p[0], p[1], p[2], p[3], p[4], p[5])
        base.camLens.setMinFov(46/(4./3.))
        camera.setZ(camera.getZ() + base.config.GetFloat('cog-thief-z-camera-adjust', 0.0))

    def destroyGameWalk(self):
        self.notify.debug('destroyOrthoWalk')
        if self.useOrthoWalk:
            self.gameWalk.destroy()
            del self.gameWalk
        else:
            self.notify.debug('TODO destroyGameWalk')

    def initGameWalk(self):
        self.notify.debug('startOrthoWalk')
        if self.useOrthoWalk:

            def doCollisions(oldPos, newPos, self = self):
                x = bound(newPos[0], CTGG.StageHalfWidth, -CTGG.StageHalfWidth)
                y = bound(newPos[1], CTGG.StageHalfHeight, -CTGG.StageHalfHeight)
                newPos.setX(x)
                newPos.setY(y)
                return newPos

            orthoDrive = OrthoDrive(self.ToonSpeed, customCollisionCallback=doCollisions, instantTurn=True)
            self.gameWalk = OrthoWalk(orthoDrive, broadcast=not self.isSinglePlayer())
        else:
            self.gameWalk = CogThiefWalk.CogThiefWalk('walkDone')
            forwardSpeed = self.ToonSpeed / 2.0
            base.mouseInterfaceNode.setForwardSpeed(forwardSpeed)
            multiplier = forwardSpeed / ToontownGlobals.ToonForwardSpeed
            base.mouseInterfaceNode.setRotateSpeed(ToontownGlobals.ToonRotateSpeed * 4)

    def initCogInfo(self):
        for cogIndex in range(self.getNumCogs()):
            self.cogInfo[cogIndex] = {'pos': Point3(CTGG.CogStartingPositions[cogIndex]),
             'goal': CTGG.NoGoal,
             'goalId': CTGG.InvalidGoalId,
             'suit': None,
             'barrel': CTGG.NoBarrelCarried}

        return

    def initBarrelInfo(self):
        for barrelIndex in range(CogThiefGameGlobals.NumBarrels):
            self.barrelInfo[barrelIndex] = {'pos': Point3(CogThiefGameGlobals.BarrelStartingPositions[barrelIndex]),
             'carriedBy': CTGG.BarrelOnGround,
             'stolen': False}

    def loadCogs(self):
        suitTypes = ['ds',
         'ac',
         'bc',
         'ms']
        for suitIndex in range(self.getNumCogs()):
            st = self.randomNumGen.choice(suitTypes)
            suit = CogThief.CogThief(suitIndex, st, self, self.getCogSpeed())
            self.cogInfo[suitIndex]['suit'] = suit

    def handleEnterSphere(self, colEntry):
        if self.gameIsEnding:
            return
        intoName = colEntry.getIntoNodePath().getName()
        fromName = colEntry.getFromNodePath().getName()
        debugInto = intoName.split('/')
        debugFrom = fromName.split('/')
        self.notify.debug('handleEnterSphere gametime=%s %s into %s' % (self.getCurrentGameTime(), debugFrom[-1], debugInto[-1]))
        intoName = colEntry.getIntoNodePath().getName()
        if 'CogThiefSphere' in intoName:
            parts = intoName.split('-')
            suitNum = int(parts[1])
            self.localToonHitBySuit(suitNum)

    def localToonHitBySuit(self, suitNum):
        self.notify.debug('localToonHitBySuit %d' % suitNum)
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        pos = self.cogInfo[suitNum]['suit'].suit.getPos()
        self.hitBySuit(self.localAvId, timestamp, suitNum, pos[0], pos[1], pos[2])
        self.showToonHitBySuit(self.localAvId, timestamp)
        self.makeSuitRespondToToonHit(timestamp, suitNum)

    def hitBySuit(self, avId, timestamp, suitNum, x, y, z):
        if not self.hasLocalToon:
            return
        if self.gameFSM.getCurrentState().getName() not in ['play']:
            self.notify.warning('ignoring msg: av %s hit by suit' % avId)
            return
        if self.gameIsEnding:
            return
        self.notify.debug('avatar ' + repr(avId) + ' hit by a suit')
        if suitNum >= self.getNumCogs():
            self.notify.warning('hitBySuit, possible hacker avId=%s' % avId)
            return
        barrelIndex = self.cogInfo[suitNum]['barrel']
        if barrelIndex >= 0:
            barrelPos = Point3(x, y, z)
            self.b_makeCogDropBarrel(timestamp, suitNum, barrelIndex, barrelPos)
        startPos = CTGG.CogStartingPositions[suitNum]
        self.cogInfo[suitNum]['pos'] = startPos
        self.cogInfo[suitNum]['goal'] = CTGG.NoGoal
        self.cogInfo[suitNum]['goalId'] = CTGG.InvalidGoalId
        self.sendSuitSync(timestamp, suitNum)
        self.doMethodLater(self.ExplodeWaitTime, self.chooseSuitGoal, self.uniqueName('choseSuitGoal-%d-' % suitNum), extraArgs=[suitNum])
        if avId != self.localAvId:
            self.showToonHitBySuit(avId, timestamp)
            self.makeSuitRespondToToonHit(timestamp, suitNum)

    def showToonHitBySuit(self, avId, timestamp):
        toon = self.getAvatar()
        if toon == None:
            return
        rng = self.toonRNGs[self.avIdList.index(avId)]
        curPos = toon.getPos(render)
        oldTrack = self.toonHitTracks[avId]
        if oldTrack.isPlaying():
            oldTrack.finish()
        toon.setPos(curPos)
        toon.setZ(self.TOON_Z)
        parentNode = render.attachNewNode('mazeFlyToonParent-' + repr(avId))
        parentNode.setPos(toon.getPos())
        toon.reparentTo(parentNode)
        toon.setPos(0, 0, 0)
        startPos = parentNode.getPos()
        dropShadow = toon.dropShadow.copyTo(parentNode)
        dropShadow.setScale(toon.dropShadow.getScale(render))
        trajectory = Trajectory.Trajectory(0, Point3(0, 0, 0), Point3(0, 0, 20), gravMult=1.0)
        oldFlyDur = trajectory.calcTimeOfImpactOnPlane(0.0)
        trajectory = Trajectory.Trajectory(0, Point3(0, 0, 0), Point3(0, 0, 20), gravMult=0.55)
        flyDur = trajectory.calcTimeOfImpactOnPlane(0.0)
        avIndex = self.avIdList.index(avId)
        endPos = CTGG.ToonStartingPositions[avIndex]

        def flyFunc(t, trajectory, startPos = startPos, endPos = endPos, dur = flyDur, moveNode = parentNode, flyNode = toon):
            u = t / dur
            moveNode.setX(startPos[0] + u * (endPos[0] - startPos[0]))
            moveNode.setY(startPos[1] + u * (endPos[1] - startPos[1]))
            flyNode.setPos(trajectory.getPos(t))

        flyTrack = Sequence(LerpFunctionInterval(flyFunc, fromData=0.0, toData=flyDur, duration=flyDur, extraArgs=[trajectory]), name=toon.uniqueName('hitBySuit-fly'))
        geomNode = toon.getGeomNode()
        startHpr = geomNode.getHpr()
        destHpr = Point3(startHpr)
        hRot = rng.randrange(1, 8)
        if rng.choice([0, 1]):
            hRot = -hRot
        destHpr.setX(destHpr[0] + hRot * 360)
        spinHTrack = Sequence(LerpHprInterval(geomNode, flyDur, destHpr, startHpr=startHpr), Func(geomNode.setHpr, startHpr), name=toon.uniqueName('hitBySuit-spinH'))
        parent = geomNode.getParent()
        rotNode = parent.attachNewNode('rotNode')
        geomNode.reparentTo(rotNode)
        rotNode.setZ(toon.getHeight() / 2.0)
        oldGeomNodeZ = geomNode.getZ()
        geomNode.setZ(-toon.getHeight() / 2.0)
        startHpr = rotNode.getHpr()
        destHpr = Point3(startHpr)
        pRot = rng.randrange(1, 3)
        if rng.choice([0, 1]):
            pRot = -pRot
        destHpr.setY(destHpr[1] + pRot * 360)
        spinPTrack = Sequence(LerpHprInterval(rotNode, flyDur, destHpr, startHpr=startHpr), Func(rotNode.setHpr, startHpr), name=toon.uniqueName('hitBySuit-spinP'))
        i = self.avIdList.index(avId)
        soundTrack = Sequence(Func(base.playSfx, self.sndTable['hitBySuit'][i]), Wait(flyDur * (2.0 / 3.0)), SoundInterval(self.sndTable['falling'][i], duration=flyDur * (1.0 / 3.0)), name=toon.uniqueName('hitBySuit-soundTrack'))

        def preFunc(self = self, avId = avId, toon = toon, dropShadow = dropShadow):
            forwardSpeed = toon.forwardSpeed
            rotateSpeed = toon.rotateSpeed
            if avId == self.localAvId:
                self.stopGameWalk()
            else:
                toon.stopSmooth()
            if forwardSpeed or rotateSpeed:
                toon.setSpeed(forwardSpeed, rotateSpeed)
            toon.dropShadow.hide()

        def postFunc(self = self, avId = avId, oldGeomNodeZ = oldGeomNodeZ, dropShadow = dropShadow, parentNode = parentNode):
            if avId == self.localAvId:
                base.localAvatar.setPos(endPos)
                if hasattr(self, 'gameWalk'):
                    toon = base.localAvatar
                    toon.setSpeed(0, 0)
                    self.startGameWalk()
            dropShadow.removeNode()
            del dropShadow
            toon = self.getAvatar()
            if toon:
                toon.dropShadow.show()
                geomNode = toon.getGeomNode()
                rotNode = geomNode.getParent()
                baseNode = rotNode.getParent()
                geomNode.reparentTo(baseNode)
                rotNode.removeNode()
                del rotNode
                geomNode.setZ(oldGeomNodeZ)
            if toon:
                toon.reparentTo(render)
                toon.setPos(endPos)
            parentNode.removeNode()
            del parentNode
            if avId != self.localAvId:
                if toon:
                    toon.startSmooth()

        preFunc()
        slipBack = Parallel(Sequence(ActorInterval(toon, 'slip-backward', endFrame=24), Wait(CTGG.LyingDownDuration - (flyDur - oldFlyDur)), ActorInterval(toon, 'slip-backward', startFrame=24)))
        if toon.doId == self.localAvId:
            slipBack.append(SoundInterval(self.sndOof))
        hitTrack = Sequence(Parallel(flyTrack, spinHTrack, spinPTrack, soundTrack), slipBack, Func(postFunc), name=toon.uniqueName('hitBySuit'))
        self.notify.debug('hitTrack duration = %s' % hitTrack.getDuration())
        self.toonHitTracks[avId] = hitTrack
        hitTrack.start(globalClockDelta.localElapsedTime(timestamp))
        return

    def startSuitGoals(self):
        delayTimes = []
        for cogIndex in range(self.getNumCogs()):
            delayTimes.append(cogIndex * 1.0)

        random.shuffle(delayTimes)
        for cogIndex in range(self.getNumCogs()):
            self.doMethodLater(delayTimes[cogIndex], self.chooseSuitGoal, self.uniqueName('choseSuitGoal-%d-' % cogIndex), extraArgs=[cogIndex])

    def chooseSuitGoal(self, suitNum):
        if self.gameIsEnding:
            return
        barrelIndex = self.findClosestUnassignedBarrel(suitNum)
        if barrelIndex >= 0:
            self.chaseBarrel(suitNum, barrelIndex)
        else:
            noOneChasing = self.avIdList[:]
            for key in self.cogInfo:
                if self.cogInfo[key]['goal'] == CTGG.ToonGoal:
                    toonId = self.cogInfo[key]['goalId']
                    if toonId in noOneChasing:
                        noOneChasing.remove(toonId)

            chaseToonId = self.avIdList[0]
            if noOneChasing:
                chaseToonId = random.choice(noOneChasing)
            else:
                chaseToonId = random.choice(self.avIdList)
            self.chaseToon(suitNum, chaseToonId)

    def chooseReturnPos(self, cogIndex, cogPos):
        shortestDistance = 10000
        shortestReturnIndex = -1
        for retIndex in range(len(CTGG.CogReturnPositions)):
            retPos = CTGG.CogReturnPositions[retIndex]
            distance = (cogPos - retPos).length()
            if distance < shortestDistance:
                shortestDistance = distance
                shortestReturnIndex = retIndex
                self.notify.debug('shortest distance=%s index=%s' % (shortestDistance, shortestReturnIndex))

        self.notify.debug('chooseReturnpos returning %s' % shortestReturnIndex)
        return shortestReturnIndex

    def runAway(self, clientStamp, cogIndex, cogPos, barrelIndex, returnPosIndex):
        self.cogInfo[cogIndex]['pos'] = cogPos
        self.b_makeCogCarryBarrel(clientStamp, cogIndex, barrelIndex)
        goalType = CTGG.RunAwayGoal
        goalId = returnPosIndex
        self.cogInfo[cogIndex]['goal'] = goalType
        self.cogInfo[cogIndex]['goalId'] = 0
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        gameTime = self.getCurrentGameTime()
        self.updateSuitGoal(timestamp, clientStamp, cogIndex, goalType, goalId, cogPos[0], cogPos[1], cogPos[2])

    def findClosestUnassignedBarrel(self, suitNum):
        possibleBarrels = []
        for key in self.barrelInfo:
            info = self.barrelInfo[key]
            if info['carriedBy'] == CTGG.BarrelOnGround and not info['stolen']:
                if not self.isCogGoingForBarrel(key):
                    possibleBarrels.append(key)

        shortestDistance = 10000
        shortestBarrelIndex = -1
        cogPos = self.cogInfo[suitNum]['pos']
        for possibleIndex in possibleBarrels:
            barrelPos = self.barrelInfo[possibleIndex]['pos']
            distance = (cogPos - barrelPos).length()
            if distance < shortestDistance:
                shortestDistance = distance
                shortestBarrelIndex = possibleIndex

        return shortestBarrelIndex

    def isCogGoingForBarrel(self, barrelIndex):
        result = False
        for suitNum in self.cogInfo:
            cogInfo = self.cogInfo[suitNum]
            if cogInfo['goal'] == CTGG.BarrelGoal and cogInfo['goalId'] == barrelIndex:
                result = True
                break

        return result

    def chaseBarrel(self, suitNum, barrelIndex):
        goalType = CTGG.BarrelGoal
        goalId = barrelIndex
        self.cogInfo[suitNum]['goal'] = goalType
        self.cogInfo[suitNum]['goalId'] = goalId
        pos = self.cogInfo[suitNum]['pos']
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        self.notify.debug('chaseBarrel time=%s suitNum=%s, barrelIndex=%s' % (timestamp, suitNum, barrelIndex))
        gameTime = self.getCurrentGameTime()
        self.updateSuitGoal(timestamp, timestamp, suitNum, goalType, goalId, pos[0], pos[1], pos[2])

    def chaseToon(self, suitNum, avId):
        goalType = CTGG.ToonGoal
        goalId = avId
        self.cogInfo[suitNum]['goal'] = goalType
        self.cogInfo[suitNum]['goalId'] = goalId
        pos = self.cogInfo[suitNum]['pos']
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        self.notify.debug('chaseToon time=%s suitNum=%s, avId=%s' % (timestamp, suitNum, avId))
        gameTime = self.getCurrentGameTime()
        self.updateSuitGoal(timestamp, timestamp, suitNum, goalType, goalId, pos[0], pos[1], pos[2])

    def sendSuitSync(self, clientstamp, suitNum):
        pos = self.cogInfo[suitNum]['pos']
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        goalType = self.cogInfo[suitNum]['goal']
        goalId = self.cogInfo[suitNum]['goalId']
        gameTime = self.getCurrentGameTime()
        self.updateSuitGoal(timestamp, clientstamp, suitNum, goalType, goalId, pos[0], pos[1], pos[2])

    def updateSuitGoal(self, timestamp, inResponseToClientStamp, suitNum, goalType, goalId, x, y, z):
        if not self.hasLocalToon:
            return
        self.notify.debug('updateSuitGoal gameTime=%s timeStamp=%s cog=%s goal=%s goalId=%s (%.1f, %.1f,%.1f)' % (self.getCurrentGameTime(),
         timestamp,
         suitNum,
         CTGG.GoalStr[goalType],
         goalId,
         x,
         y,
         z))
        cog = self.cogInfo[suitNum]
        cog['goal'] = goalType
        cog['goalId'] = goalId
        newPos = Point3(x, y, z)
        cog['pos'] = newPos
        suit = cog['suit']
        suit.updateGoal(timestamp, inResponseToClientStamp, goalType, goalId, newPos)

    def spawnUpdateSuitsTask(self):
        self.notify.debug('spawnUpdateSuitsTask')
        for cogIndex in self.cogInfo:
            suit = self.cogInfo[cogIndex]['suit']
            suit.gameStart(self.gameStartTime)

        taskMgr.remove(self.UPDATE_SUITS_TASK)
        taskMgr.add(self.updateSuitsTask, self.UPDATE_SUITS_TASK)

    def removeUpdateSuitsTask(self):
        taskMgr.remove(self.UPDATE_SUITS_TASK)

    def updateSuitsTask(self, task):
        if self.gameIsEnding:
            return task.done
        for cogIndex in self.cogInfo:
            suit = self.cogInfo[cogIndex]['suit']
            suit.think()

        return task.cont

    def makeSuitRespondToToonHit(self, timestamp, suitNum):
        cog = self.cogInfo[suitNum]['suit']
        cog.respondToToonHit(timestamp)

    def handleEnterBarrel(self, colEntry):
        if self.gameIsEnding:
            return
        intoName = colEntry.getIntoNodePath().getName()
        fromName = colEntry.getFromNodePath().getName()
        debugInto = intoName.split('/')
        debugFrom = fromName.split('/')
        self.notify.debug('handleEnterBarrel gameTime=%s %s into %s' % (self.getCurrentGameTime(), debugFrom[-1], debugInto[-1]))
        if 'CogThiefSphere' in intoName:
            parts = intoName.split('-')
            cogIndex = int(parts[1])
            barrelName = colEntry.getFromNodePath().getName()
            barrelParts = barrelName.split('-')
            barrelIndex = int(barrelParts[1])
            cog = self.cogInfo[cogIndex]['suit']
            if cog.barrel == CTGG.NoBarrelCarried and barrelIndex not in self.stolenBarrels:
                timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
                if cog.suit:
                    cogPos = cog.suit.getPos()
                    collisionPos = colEntry.getContactPos(render)
                    if (cogPos - collisionPos).length() > 4:
                        import pdb
                        pdb.set_trace()
                    self.cogHitBarrel(timestamp, cogIndex, barrelIndex, cogPos[0], cogPos[1], cogPos[2])

    def cogHitBarrel(self, clientStamp, cogIndex, barrelIndex, x, y, z):
        if cogIndex >= self.getNumCogs():
            self.notify.warning('cogHitBarrel, possible hacker cogIndex=%s' % cogIndex)
            return
        if barrelIndex >= CTGG.NumBarrels:
            self.notify.warning('cogHitBarrel, possible hacker barrelIndex=%s' % barrelIndex)
            return
        if self.isCogCarryingABarrel(cogIndex):
            self.notify.debug('cog is already carrying a barrel ignore')
            return
        if self.cogInfo[cogIndex]['goal'] == CTGG.NoGoal:
            self.notify.debug('ignoring barrel hit as cog %d has no goal' % cogIndex)
            return
        if self.getCogCarryingBarrel(barrelIndex) == CTGG.BarrelOnGround:
            pos = Point3(x, y, z)
            returnPosIndex = self.chooseReturnPos(cogIndex, pos)
            self.runAway(clientStamp, cogIndex, pos, barrelIndex, returnPosIndex)

    def isCogCarryingABarrel(self, cogIndex):
        result = self.cogInfo[cogIndex]['barrel'] > CTGG.NoBarrelCarried
        return result

    def getCogCarryingBarrel(self, barrelIndex):
        return self.barrelInfo[barrelIndex]['carriedBy']

    def makeCogCarryBarrelUpdate(self, timestamp, clientStamp, cogIndex, barrelIndex):
        if cogIndex in self.cogInfo and barrelIndex in self.barrelInfo:
            self.barrelInfo[barrelIndex]['carriedBy'] = cogIndex
            self.cogInfo[cogIndex]['barrel'] = barrelIndex
        else:
            self.notify.warning('makeCogCarryBarrel invalid cogIndex=%s barrelIndex=%s' % (cogIndex, barrelIndex))

    def makeCogCarryBarrel(self, timestamp, inResponseToClientStamp, cogIndex, barrelIndex, x, y, z):
        if not self.hasLocalToon:
            return
        if self.gameIsEnding:
            return
        self.notify.debug('makeCogCarryBarrel gameTime=%s timeStamp=%s cog=%s barrel=%s (%.1f, %.1f,%.1f)' % (self.getCurrentGameTime(),
         timestamp,
         cogIndex,
         barrelIndex,
         x,
         y,
         z))
        barrel = self.barrels[barrelIndex]
        self.notify.debug('barrelPos= %s' % barrel.getPos())
        cog = self.cogInfo[cogIndex]['suit']
        cogPos = Point3(x, y, z)
        cog.makeCogCarryBarrel(timestamp, inResponseToClientStamp, barrel, barrelIndex, cogPos)

    def b_makeCogCarryBarrel(self, clientStamp, cogIndex, barrelIndex):
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        self.notify.debug('b_makeCogCarryBarrel timeStamp=%s clientStamp=%s cog=%s barrel=%s' % (timestamp,
         clientStamp,
         cogIndex,
         barrelIndex))
        self.makeCogCarryBarrelUpdate(timestamp, clientStamp, cogIndex, barrelIndex)
        self.d_makeCogCarryBarrel(timestamp, clientStamp, cogIndex, barrelIndex)

    def d_makeCogCarryBarrel(self, timestamp, clientStamp, cogIndex, barrelIndex):
        pos = self.cogInfo[cogIndex]['pos']
        gameTime = self.getCurrentGameTime()
        self.makeCogCarryBarrel(timestamp, clientStamp, cogIndex, barrelIndex, pos[0], pos[1], pos[2])

    def makeCogDropBarrel(self, timestamp, inResponseToClientStamp, cogIndex, barrelIndex, x, y, z):
        if not self.hasLocalToon:
            return
        self.notify.debug('makeCogDropBarrel gameTime=%s timeStamp=%s cog=%s barrel=%s (%.1f, %.1f,%.1f)' % (self.getCurrentGameTime(),
         timestamp,
         cogIndex,
         barrelIndex,
         x,
         y,
         z))
        barrel = self.barrels[barrelIndex]
        self.notify.debug('barrelPos= %s' % barrel.getPos())
        cog = self.cogInfo[cogIndex]['suit']
        cogPos = Point3(x, y, z)
        cog.makeCogDropBarrel(timestamp, inResponseToClientStamp, barrel, barrelIndex, cogPos)

    def makeCogDropBarrelUpdate(self, timestamp, clientStamp, cogIndex, barrelIndex, barrelPos):
        if cogIndex in self.cogInfo and barrelIndex in self.barrelInfo:
            self.barrelInfo[barrelIndex]['carriedBy'] = CTGG.BarrelOnGround
            self.cogInfo[cogIndex]['barrel'] = CTGG.NoBarrelCarried
        else:
            self.notify.warning('makeCogDropBarrel invalid cogIndex=%s barrelIndex=%s' % (cogIndex, barrelIndex))

    def b_makeCogDropBarrel(self, clientStamp, cogIndex, barrelIndex, barrelPos):
        if self.barrelInfo[barrelIndex]['carriedBy'] != cogIndex:
            self.notify.error("self.barrelInfo[%s]['carriedBy'] != %s" % (barrelIndex, cogIndex))
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        self.makeCogDropBarrelUpdate(timestamp, clientStamp, cogIndex, barrelIndex, barrelPos)
        self.d_makeCogDropBarrel(timestamp, clientStamp, cogIndex, barrelIndex, barrelPos)

    def d_makeCogDropBarrel(self, timestamp, clientStamp, cogIndex, barrelIndex, barrelPos):
        pos = barrelPos
        gameTime = self.getCurrentGameTime()
        self.makeCogDropBarrel(timestamp, clientStamp, cogIndex, barrelIndex, pos[0], pos[1], pos[2])

    def controlKeyPressed(self):
        if self.isToonPlayingHitTrack(self.localAvId):
            return
        if self.gameIsEnding:
            return
        if self.getCurrentGameTime() - self.lastTimeControlPressed > self.ControlKeyLimitTime:
            self.lastTimeControlPressed = self.getCurrentGameTime()
            self.notify.debug('controlKeyPressed')
            toonSD = self.toonSDs[self.localAvId]
            curState = toonSD.fsm.getCurrentState().getName()
            toon = self.getAvatar()
            timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
            pos = toon.getPos()
            heading = toon.getH()
            self.throwingPie(self.localAvId, timestamp, heading, pos[0], pos[1], pos[2])
            self.showToonThrowingPie(self.localAvId, timestamp, heading, pos)

    def throwingPie(self, avId, timestamp, heading, x, y, z):
        if not self.hasLocalToon:
            return
        if self.gameFSM.getCurrentState().getName() not in ['play']:
            self.notify.warning('ignoring msg: av %s hit by suit' % avId)
            return
        self.notify.debug('avatar ' + repr(avId) + ' throwing pie')
        if avId != self.localAvId:
            pos = Point3(x, y, z)
            self.showToonThrowingPie(avId, timestamp, heading, pos)

    def showToonThrowingPie(self, avId, timestamp, heading, pos):
        toon = self.getAvatar()
        if toon:
            tossTrack, pieTrack, flyPie = self.getTossPieInterval(toon, pos[0], pos[1], pos[2], heading, 0, 0, 0)

            def removePieFromTraverser(flyPie = flyPie):
                if base.cTrav:
                    if flyPie:
                        base.cTrav.removeCollider(flyPie)

            if avId == self.localAvId:
                flyPie.setTag('throwerId', str(avId))
                collSphere = CollisionSphere(0, 0, 0, 0.5)
                collSphere.setTangible(0)
                name = 'PieSphere-%d' % avId
                collSphereName = self.uniqueName(name)
                collNode = CollisionNode(collSphereName)
                collNode.setFromCollideMask(ToontownGlobals.PieBitmask)
                collNode.addSolid(collSphere)
                colNp = flyPie.attachNewNode(collNode)
                colNp.show()
                base.cTrav.addCollider(colNp, self.pieHandler)
                self.accept('pieHit-' + collSphereName, self.handlePieHitting)

            def matchRunningAnim(toon = toon):
                toon.playingAnim = None
                toon.setSpeed(toon.forwardSpeed, toon.rotateSpeed)
                return

            newTossTrack = Sequence(tossTrack, Func(matchRunningAnim))
            pieTrack = Parallel(newTossTrack, pieTrack)
            elapsedTime = globalClockDelta.localElapsedTime(timestamp)
            if elapsedTime < 16.0 / 24.0:
                elapsedTime = 16.0 / 24.0
            pieTrack.start(elapsedTime)
            self.toonPieTracks[avId] = pieTrack

    def getTossPieInterval(self, toon, x, y, z, h, p, r, power, beginFlyIval = Sequence()):
        from toontown.toonbase import ToontownBattleGlobals
        from toontown.battle import BattleProps
        pie = toon.getPieModel()
        pie.setScale(0.9)
        flyPie = pie.copyTo(NodePath('a'))
        pieName = ToontownBattleGlobals.pieNames[toon.pieType]
        pieType = BattleProps.globalPropPool.getPropType(pieName)
        animPie = Sequence()
        if pieType == 'actor':
            animPie = ActorInterval(pie, pieName, startFrame=48)
        sound = loader.loadSfx('phase_3.5/audio/sfx/AA_pie_throw_only.ogg')
        t = power / 100.0
        dist = 100 - 70 * t
        time = 1 + 0.5 * t
        proj = ProjectileInterval(None, startPos=Point3(0, 0, 0), endPos=Point3(0, dist, 0), duration=time)
        relVel = proj.startVel

        def getVelocity(toon = toon, relVel = relVel):
            return render.getRelativeVector(toon, relVel) * 0.6

        toss = Track((0, Sequence(Func(toon.setPosHpr, x, y, z, h, p, r), Func(pie.reparentTo, toon.rightHand), Func(pie.setPosHpr, 0, 0, 0, 0, 0, 0), Parallel(ActorInterval(toon, 'throw', startFrame=48, partName='torso'), animPie), Func(toon.loop, 'neutral'))), (16.0 / 24.0, Func(pie.detachNode)))
        fly = Track((14.0 / 24.0, SoundInterval(sound, node=toon)), (16.0 / 24.0, Sequence(Func(flyPie.reparentTo, render), Func(flyPie.setPosHpr, toon, 0.52, 0.97, 2.24, 0, -45, 0), beginFlyIval, ProjectileInterval(flyPie, startVel=getVelocity, duration=6), Func(flyPie.detachNode))))
        return (toss, fly, flyPie)

    def handlePieHitting(self, colEntry):
        if self.gameIsEnding:
            return
        into = colEntry.getIntoNodePath()
        intoName = into.getName()
        if 'CogThiefPieSphere' in intoName:
            timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
            parts = intoName.split('-')
            suitNum = int(parts[1])
            pos = self.cogInfo[suitNum]['suit'].suit.getPos()
            if pos in CTGG.CogStartingPositions:
                self.notify.debug('Cog %d hit at starting pos %s, ignoring' % (suitNum, pos))
            else:
                self.pieHitSuit(self.localAvId, timestamp, suitNum, pos[0], pos[1], pos[2])
                self.makeSuitRespondToPieHit(timestamp, suitNum, pos)

    def pieHitSuit(self, avId, timestamp, suitNum, x, y, z):
        if not self.hasLocalToon:
            return
        if self.gameFSM.getCurrentState().getName() not in ['play']:
            self.notify.warning('ignoring msg: av %s hit by suit' % avId)
            return
        if self.gameIsEnding:
            return
        self.notify.debug('avatar ' + repr(avId) + ' hit by a suit')
        if suitNum >= self.getNumCogs():
            self.notify.warning('hitBySuit, possible hacker avId=%s' % avId)
            return
        barrelIndex = self.cogInfo[suitNum]['barrel']
        if barrelIndex >= 0:
            barrelPos = Point3(x, y, z)
            self.b_makeCogDropBarrel(timestamp, suitNum, barrelIndex, barrelPos)
        pos = Point3(x, y, z)
        startPos = CTGG.CogStartingPositions[suitNum]
        self.cogInfo[suitNum]['pos'] = startPos
        self.cogInfo[suitNum]['goal'] = CTGG.NoGoal
        self.cogInfo[suitNum]['goalId'] = CTGG.InvalidGoalId
        self.sendSuitSync(timestamp, suitNum)
        self.doMethodLater(self.ExplodeWaitTime, self.chooseSuitGoal, self.uniqueName('choseSuitGoal-%d-' % suitNum), extraArgs=[suitNum])
        if avId != self.localAvId:
            self.makeSuitRespondToPieHit(timestamp, suitNum, pos)

    def makeSuitRespondToPieHit(self, timestamp, suitNum, pos):
        cog = self.cogInfo[suitNum]['suit']
        cog.respondToPieHit(timestamp, pos)

    def sendCogAtReturnPos(self, cogIndex, barrelIndex):
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        self.cogAtReturnPos(timestamp, cogIndex, barrelIndex)

    def cogAtReturnPos(self, clientstamp, cogIndex, barrelIndex):
        if self.cogInfo[cogIndex]['goal'] == CTGG.RunAwayGoal:
            if self.isCogCarryingThisBarrel(cogIndex, barrelIndex):
                self.markBarrelStolenUpdate(clientstamp, barrelIndex)
                returnPosIndex = self.cogInfo[cogIndex]['goalId']
                retPos = CTGG.CogReturnPositions[returnPosIndex]
                self.b_makeCogDropBarrel(clientstamp, cogIndex, barrelIndex, retPos)
                startPos = CTGG.CogStartingPositions[cogIndex]
                self.cogInfo[cogIndex]['pos'] = startPos
                self.cogInfo[cogIndex]['goal'] = CTGG.NoGoal
                self.cogInfo[cogIndex]['goalId'] = CTGG.InvalidGoalId
                self.doMethodLater(0.5, self.chooseSuitGoal, self.uniqueName('choseSuitGoal-%d-' % cogIndex), extraArgs=[cogIndex])
                self.checkForGameOver()

    def checkForGameOver(self):
        numStolen = 0
        for key in self.barrelInfo:
            if self.barrelInfo[key]['stolen']:
                numStolen += 1

        self.notify.debug('numStolen = %s' % numStolen)
        if base.config.GetBool('cog-thief-check-barrels', 1):
            if not base.config.GetBool('cog-thief-endless', 0):
                if numStolen == len(self.barrelInfo):
                    self.showResults()

    def isCogCarryingThisBarrel(self, cogIndex, barrelIndex):
        result = self.cogInfo[cogIndex]['barrel'] == barrelIndex
        return result

    def getNumBarrelsStolen(self):
        numStolen = 0
        for barrel in self.barrelInfo.values():
            if barrel['stolen']:
                numStolen += 1

        return numStolen

    def markBarrelStolenUpdate(self, clientStamp, barrelIndex):
        timestamp = globalClockDelta.localToNetworkTime(globalClock.getFrameTime(), bits=32)
        self.markBarrelStolen(timestamp, clientStamp, barrelIndex)
        self.barrelInfo[barrelIndex]['stolen'] = True

    def markBarrelStolen(self, timestamp, inResponseToClientStamp, barrelIndex):
        if not self.hasLocalToon:
            return
        if barrelIndex not in self.stolenBarrels:
            self.stolenBarrels.append(barrelIndex)
            barrel = self.barrels[barrelIndex]
            barrel.hide()
        if base.config.GetBool('cog-thief-check-barrels', 1):
            if not base.config.GetBool('cog-thief-endless', 0):
                if len(self.stolenBarrels) == len(self.barrels):
                    localStamp = globalClockDelta.networkToLocalTime(timestamp, bits=32)
                    gameTime = self.local2GameTime(localStamp)
                    self.clockStopTime = gameTime
                    self.notify.debug('clockStopTime = %s' % gameTime)
                    score = int(self.scoreMult * CTGG.calcScore(gameTime) + 0.5)
                    self.rewardPanel['text'] = str(score)
                    self.showResults()

    def __gameTimerExpired(self):
        self.notify.debug('game timer expired')
        self.showResults()

    def __startRewardCountdown(self):
        taskMgr.remove(self.REWARD_COUNTDOWN_TASK)
        taskMgr.add(self.__updateRewardCountdown, self.REWARD_COUNTDOWN_TASK)

    def __killRewardCountdown(self):
        taskMgr.remove(self.REWARD_COUNTDOWN_TASK)

    def __updateRewardCountdown(self, task):
        curTime = self.getCurrentGameTime()
        if self.clockStopTime is not None:
            if self.clockStopTime < curTime:
                self.notify.debug('self.clockStopTime < curTime %s %s' % (self.clockStopTime, curTime))
                self.__killRewardCountdown()
                curTime = self.clockStopTime
        if curTime > CTGG.GameTime:
            curTime = CTGG.GameTime
        score = int(self.scoreMult * CTGG.calcScore(curTime) + 0.5)
        if not hasattr(task, 'curScore'):
            task.curScore = score
        result = Task.cont
        if hasattr(self, 'rewardPanel'):
            self.rewardPanel['text'] = str(score)
            if task.curScore != score:
                if hasattr(self, 'jarIval'):
                    self.jarIval.finish()
                s = self.rewardPanel.getScale()
                self.jarIval = Parallel(Sequence(self.rewardPanel.scaleInterval(0.15, s * 3.0 / 4.0, blendType='easeOut'), self.rewardPanel.scaleInterval(0.15, s, blendType='easeIn')), SoundInterval(self.sndRewardTick), name='cogThiefGameRewardJarThrob')
                self.jarIval.start()
            task.curScore = score
        else:
            result = Task.done
        return result

    def startGameWalk(self):
        if self.useOrthoWalk:
            self.gameWalk.start()
        else:
            self.gameWalk.enter()
            self.gameWalk.fsm.request('walking')

    def stopGameWalk(self):
        if self.useOrthoWalk:
            self.gameWalk.stop()
        else:
            self.gameWalk.exit()

    def getCogThief(self, cogIndex):
        return self.cogInfo[cogIndex]['suit']

    def isToonPlayingHitTrack(self, avId):
        if avId in self.toonHitTracks:
            track = self.toonHitTracks[avId]
            if track.isPlaying():
                return True
        return False

    def getNumCogs(self):
        result = base.config.GetInt('cog-thief-num-cogs', 0)
        if not result:
            safezone = self.getSafezoneId()
            result = CTGG.calculateCogs(self.numPlayers, safezone)
        return result

    def getCogSpeed(self):
        result = 6.0
        safezone = self.getSafezoneId()
        result = CTGG.calculateCogSpeed(self.numPlayers, safezone)
        return result

    def showResults(self):
        if not self.gameIsEnding:
            self.gameIsEnding = True
            for barrel in self.barrels:
                barrel.wrtReparentTo(render)

            for key in self.cogInfo:
                thief = self.cogInfo[key]['suit']
                thief.suit.setPos(100, 0, 0)
                thief.suit.hide()

            self.__killRewardCountdown()
            self.stopGameWalk()
            numBarrelsSaved = len(self.barrels) - len(self.stolenBarrels)
            resultStr = ''
            if numBarrelsSaved == len(self.barrels):
                resultStr = TTLocalizer.CogThiefPerfect
            elif numBarrelsSaved > 1:
                resultStr = TTLocalizer.CogThiefBarrelsSaved % {'num': numBarrelsSaved}
            elif numBarrelsSaved == 1:
                resultStr = TTLocalizer.CogThiefBarrelSaved % {'num': numBarrelsSaved}
            else:
                resultStr = TTLocalizer.CogThiefNoBarrelsSaved
            perfectTextSubnode = hidden.attachNewNode(self.__genText(resultStr))
            perfectText = hidden.attachNewNode('perfectText')
            perfectTextSubnode.reparentTo(perfectText)
            frame = self.__textGen.getCardActual()
            offsetY = -abs(frame[2] + frame[3]) / 2.0
            perfectTextSubnode.setPos(0, 0, offsetY)
            perfectText.setColor(1, 0.1, 0.1, 1)

            def fadeFunc(t, text = perfectText):
                text.setColorScale(1, 1, 1, t)

            def destroyText(text = perfectText):
                text.removeNode()

            def safeGameOver(self = self):
                if not self.frameworkFSM.isInternalStateInFlux():
                    self.gameOver()

            textTrack = Sequence(Func(perfectText.reparentTo, aspect2d), Parallel(LerpScaleInterval(perfectText, duration=0.5, scale=0.3, startScale=0.0), LerpFunctionInterval(fadeFunc, fromData=0.0, toData=1.0, duration=0.5)), Wait(2.0), Parallel(LerpScaleInterval(perfectText, duration=0.5, scale=1.0), LerpFunctionInterval(fadeFunc, fromData=1.0, toData=0.0, duration=0.5, blendType='easeIn')), Func(destroyText), WaitInterval(0.5), Func(safeGameOver))
            if numBarrelsSaved == len(self.barrels):
                soundTrack = SoundInterval(self.sndPerfect)
            else:
                soundTrack = Sequence()
            self.resultIval = Parallel(textTrack, soundTrack)
            self.resultIval.start()

    def __genText(self, text):
        self.__textGen.setText(text)
        return self.__textGen.generate()

    def getIntroTrack(self):
        base.camera.setPosHpr(0, -13.66, 13.59, 0, -51.6, 0)
        result = Sequence(Wait(2), LerpPosHprInterval(base.camera, 13, Point3(self.cameraTopView[0], self.cameraTopView[1], self.cameraTopView[2]), Point3(self.cameraTopView[3], self.cameraTopView[4], self.cameraTopView[5]), blendType='easeIn'))
        return result
