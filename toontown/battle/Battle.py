from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from direct.task.Task import Task
from otp.nametag import NametagGlobals
from otp.nametag.NametagConstants import *
from toontown.toonbase import ToontownBattleGlobals
from BattleBase import *
import SuitBattleGlobals
import Movie
import random

class Battle(NodePath, BattleBase):
    notify = directNotify.newCategory('Battle')
    camPos = ToontownBattleGlobals.BattleCamDefaultPos
    camHpr = ToontownBattleGlobals.BattleCamDefaultHpr
    camFov = ToontownBattleGlobals.BattleCamDefaultFov
    camMenuFov = ToontownBattleGlobals.BattleCamMenuFov
    camJoinPos = ToontownBattleGlobals.BattleCamJoinPos
    camJoinHpr = ToontownBattleGlobals.BattleCamJoinHpr
    camFOFov = ToontownBattleGlobals.BattleCamFaceOffFov
    camFOPos = ToontownBattleGlobals.BattleCamFaceOffPos

    def __init__(self, townBattle, toons=[], suits=[]):
        self.doId = id(self)
        NodePath.__init__(self, 'Battle-%d' % self.doId)
        BattleBase.__init__(self)
        self.townBattle = townBattle
        self.toons = toons
        self.suits = suits
        self.movie = Movie.Movie(self)
        self.timerCountdownTaskName = 'timer-countdown'
        self.timer = Timer()
        self.localToonBattleEvent = 'localtoon-battle-event'

    def enter(self):
        self.enterFaceOff()
        self.townBattle.enter('battleEvent-%d' % self.doId)
        self.activeToons = self.toons
        self.activeSuits = self.suits

    def cleanupBattle(self):
        if self.__battleCleanedUp:
            return
        self.notify.debug('cleanupBattle(%s)' % self.doId)
        self.__battleCleanedUp = 1
        self.__cleanupIntervals()
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        self.ignoreAll()
        self.suits = []
        self.pendingSuits = []
        self.joiningSuits = []
        self.activeSuits = []
        self.suitTraps = ''
        self.toons = []
        self.joiningToons = []
        self.pendingToons = []
        self.activeToons = []
        self.runningToons = []
        self.__stopTimer()
        return

    def delete(self):
        self.notify.debug('delete(%s)' % self.doId)
        self.__cleanupIntervals()
        self._removeMembersKeep()
        self.movie.cleanup()
        del self.townBattle
        self.removeNode()
        self.fsm = None
        self.localToonFsm = None
        self.adjustFsm = None
        self.__stopTimer()
        self.timer = None
        DistributedNode.DistributedNode.delete(self)
        return

    def pause(self):
        self.timer.stop()

    def unpause(self):
        self.timer.resume()

    def startTimer(self, ts = 0):
        self.notify.debug('startTimer()')
        self.timer.startCallback(CLIENT_INPUT_TIMEOUT - ts, self.__timedOut)
        timeTask = Task.loop(Task(self.__countdown), Task.pause(0.2))
        taskMgr.add(timeTask, self.timerCountdownTaskName)

    def __stopTimer(self):
        self.notify.debug('__stopTimer()')
        self.timer.stop()
        taskMgr.remove(self.timerCountdownTaskName)

    def __countdown(self, task):
        if hasattr(self.townBattle, 'timer'):
            self.townBattle.updateTimer(int(self.timer.getT()))
        else:
            self.notify.warning('__countdown has tried to update a timer that has been deleted. Stopping timer')
            self.__stopTimer()
        return Task.done

    def __faceOff(self, name, callback):
        if len(self.suits) == 0:
            self.notify.warning('__faceOff(): no suits.')
            return
        if len(self.toons) == 0:
            self.notify.warning('__faceOff(): no toons.')
            return
        suit = self.suits[0]
        point = self.suitPoints[0][0]
        suitPos = point[0]
        suitHpr = VBase3(point[1], 0.0, 0.0)
        toon = self.toons[0]
        point = self.toonPoints[0][0]
        toonPos = point[0]
        toonHpr = VBase3(point[1], 0.0, 0.0)
        p = toon.getPos(self)
        toon.setPos(self, p[0], p[1], 0.0)
        toon.setShadowHeight(0)
        suit.setState('Battle')
        suitTrack = Sequence()
        toonTrack = Sequence()
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTrack.append(Func(suit.headsUp, toon))
        taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
        suitTrack.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        toonTrack.append(Func(toon.loop, 'neutral'))
        toonTrack.append(Func(toon.headsUp, suit))
        suitHeight = suit.getHeight()
        suitOffsetPnt = Point3(0, 0, suitHeight)
        faceoffTime = self.calcFaceoffTime(self.getPos(), self.initialSuitPos)
        faceoffTime = max(faceoffTime, BATTLE_SMALL_VALUE)
        delay = FACEOFF_TAUNT_T
        MidTauntCamHeight = suitHeight * 0.66
        MidTauntCamHeightLim = suitHeight - 1.8
        if MidTauntCamHeight < MidTauntCamHeightLim:
            MidTauntCamHeight = MidTauntCamHeightLim
        TauntCamY = 16
        TauntCamX = random.choice((-5, 5))
        TauntCamHeight = random.choice((MidTauntCamHeight, 1, 11))
        camTrack = Sequence()
        camTrack.append(Func(camera.wrtReparentTo, suit))
        camTrack.append(Func(base.camLens.setMinFov, self.camFOFov/(4./3.)))
        camTrack.append(Func(camera.setPos, TauntCamX, TauntCamY, TauntCamHeight))
        camTrack.append(Func(camera.lookAt, suit, suitOffsetPnt))
        camTrack.append(Wait(delay))
        camTrack.append(Func(base.camLens.setMinFov, self.camFov/(4./3.)))
        camTrack.append(Func(camera.wrtReparentTo, self))
        camTrack.append(Func(camera.setPos, self.camFOPos))
        camTrack.append(Func(camera.lookAt, suit.getPos(self)))
        camTrack.append(Wait(faceoffTime))
        suitTrack.append(Wait(delay))
        toonTrack.append(Wait(delay))
        suitTrack.append(Func(suit.headsUp, self, suitPos))
        suitTrack.append(Func(suit.clearChat))
        toonTrack.append(Func(toon.headsUp, self, toonPos))
        suitTrack.append(Func(suit.loop, 'walk'))
        suitTrack.append(LerpPosInterval(suit, faceoffTime, suitPos, other=self))
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTrack.append(Func(suit.setHpr, self, suitHpr))
        toonTrack.append(Func(toon.loop, 'run'))
        toonTrack.append(LerpPosInterval(toon, faceoffTime, toonPos, other=self))
        toonTrack.append(Func(toon.loop, 'neutral'))
        toonTrack.append(Func(toon.setHpr, self, toonHpr))
        if base.localAvatar == toon:
            soundTrack = Sequence(Wait(delay), SoundInterval(base.localAvatar.soundRun, loop=1, duration=faceoffTime, node=base.localAvatar))
        else:
            soundTrack = Wait(delay + faceoffTime)
        mtrack = Parallel(suitTrack, toonTrack, soundTrack)
        #NametagGlobals.setWant2dNametags(False)
        mtrack = Parallel(mtrack, camTrack)
        done = Func(callback)
        track = Sequence(mtrack, done, name=name)
        track.start()

    def enterFaceOff(self):
        self.notify.debug('enterFaceOff()')
        base.localAvatar.disable()
        self.__faceOff('faceoff-%d' % self.doId, self.startCamTrack)

    def startCamTrack(self):
        camTrack = Parallel()
        camTrack.append(LerpFunctionInterval(base.camLens.setMinFov, duration=1.0, fromData=self.camFov/(4./3.), toData=self.camMenuFov/(4./3.), blendType='easeInOut'))
        camTrack.append(LerpPosInterval(camera, 1.0, self.camPos, blendType='easeInOut'))
        camTrack.append(LerpHprInterval(camera, 1.0, self.camHpr, blendType='easeInOut'))
        menuTrack = Func(self.enterWaitForInput)
        track = Sequence(camTrack, menuTrack)
        track.start()

    def enterWaitForInput(self):
        camera.setPosHpr(self.camPos, self.camHpr)
        base.camLens.setMinFov(self.camMenuFov/(4./3.))
        NametagGlobals.setMasterArrowsOn(0)
        self.townBattle.setState('Attack')
        #self.accept(self.localToonBattleEvent, self.__handleLocalToonBattleEvent)
        self.startTimer()

    def __timedOut(self):
        pass
