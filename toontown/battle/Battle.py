from panda3d.core import *
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from otp.nametag import NametagGlobals
from otp.nametag.NametagConstants import *
from otp.avatar import Emote
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.suit import Suit
from BattleCalculator import BattleCalculator
from BattleBase import *
from SuitBattleGlobals import *
import BattleExperienceAI
import BattleProps
import BattleParticles
import Movie
import MovieUtil
import random

class Battle(DirectObject, NodePath, BattleBase):
    notify = directNotify.newCategory('Battle')
    camPos = ToontownBattleGlobals.BattleCamDefaultPos
    camHpr = ToontownBattleGlobals.BattleCamDefaultHpr
    camFov = ToontownBattleGlobals.BattleCamDefaultFov
    camMenuFov = ToontownBattleGlobals.BattleCamMenuFov
    camJoinPos = ToontownBattleGlobals.BattleCamJoinPos
    camJoinHpr = ToontownBattleGlobals.BattleCamJoinHpr
    camFOFov = ToontownBattleGlobals.BattleCamFaceOffFov
    camFOPos = ToontownBattleGlobals.BattleCamFaceOffPos

    def __init__(self, townBattle, toons = [], suits = [], maxSuits = 2, bldg = 0, tutorialFlag = 0):
        self.doId = id(self)
        NodePath.__init__(self, 'Battle-%d' % self.doId)
        BattleBase.__init__(self)
        self.townBattle = townBattle
        self.toons = toons
        self.suits = suits
        self.maxSuits = maxSuits
        self.bldg = bldg
        self.tutorialFlag = tutorialFlag
        self.movie = Movie.Movie(self)
        self.timerCountdownTaskName = 'timer-countdown'
        self.timer = Timer()
        self.battleCalc = BattleCalculator(self, tutorialFlag)
        self.localToonBattleEvent = 'battleEvent-%d' % self.doId
        self.adjustName = 'battle-%d-adjust' % self.doId
        self.suitTraps = ''
        self.luredSuits = []
        self.__battleCleanedUp = 0
        self.activeIntervals = {}
        self.needAdjust = 0
        self.adjusting = 0
        self.needAdjustTownBattle = 0
        self.movieHasBeenMade = 0
        self.movieHasPlayed = 0
        self.rewardHasPlayed = 0
        self.movieRequested = 0
        self.toonExp = {}
        self.toonOrigQuests = {}
        self.toonItems = {}
        self.toonOrigMerits = {}
        self.toonMerits = {}
        self.toonParts = {}
        self.suitsKilled = []
        self.joinable = 1
        self.joinTrack = None

    def enter(self):
        self.enterFaceOff()
        self.townBattle.enter(self.localToonBattleEvent, bldg=self.bldg, tutorialFlag=self.tutorialFlag)
        self.activeToons = []
        self.activeSuits = []
        self.activeToonIds = [] # for AI functions
        for toon in self.toons:
            self.activeToons.append(toon)

        for toon in self.activeToons:
            self.activeToonIds.append(toon.doId)

        for suit in self.suits:
            self.activeSuits.append(suit)

        for suit in self.activeSuits:
            suit.enterBattle()
            suit.battleTrap = NO_TRAP

        avId = base.localAvatar.doId
        toon = self.getToon(avId)
        if avId not in self.toonExp:
            p = []
            for t in Tracks:
                p.append(toon.experience.getExp(t))

            self.toonExp[avId] = p
        if avId not in self.toonOrigMerits:
            self.toonOrigMerits[avId] = toon.cogMerits[:]
        if avId not in self.toonMerits:
            self.toonMerits[avId] = [0,
             0,
             0,
             0]
        if avId not in self.toonOrigQuests:
            flattenedQuests = []
            for quest in toon.quests:
                flattenedQuests.extend(quest)

            self.toonOrigQuests[avId] = flattenedQuests
        if avId not in self.toonItems:
            self.toonItems[avId] = ([], [])
        self.needAdjustTownBattle = 1

    def cleanupBattle(self):
        if self.__battleCleanedUp:
            return
        self.notify.debug('cleanupBattle(%s)' % self.doId)
        self.__battleCleanedUp = 1
        self.__cleanupIntervals()
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        NametagGlobals.setMasterArrowsOn(1)
        self.ignoreAll()
        for suit in self.suits:
            self.removeSuit(suit)
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
        self.movie.cleanup()
        del self.townBattle
        self.removeNode()
        self.fsm = None
        self.localToonFsm = None
        self.adjustFsm = None
        self.__stopTimer()
        self.timer = None
        return

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval

    def __cleanupIntervals(self):
        for interval in self.activeIntervals.values():
            interval.finish()

        self.activeIntervals = {}

    def clearInterval(self, name, finish = 0):
        if name in self.activeIntervals.keys():
            ival = self.activeIntervals[name]
            if finish:
                ival.finish()
            else:
                ival.pause()
            del self.activeIntervals[name]
        else:
            self.notify.debug('interval: %s already cleared' % name)

    def finishInterval(self, name):
        if self.activeIntervals.has_key(name):
            interval = self.activeIntervals[name]
            interval.finish()

    def faceOff(self, name, callback):
        if len(self.suits) == 0:
            self.notify.warning('faceOff(): no suits.')
            return
        if len(self.toons) == 0:
            self.notify.warning('faceOff(): no toons.')
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
        toon.stopLookAround()
        suit.setState('Battle')
        suitTrack = Sequence()
        toonTrack = Sequence()
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTrack.append(Func(suit.headsUp, toon))
        taunt = getFaceoffTaunt(suit.getStyleName(), suit.doId)
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
        mtrack = Parallel(mtrack, camTrack)
        done = Func(callback)
        track = Sequence(mtrack, done, name=name)
        track.start()
        self.storeInterval(track, name)

    def enterFaceOff(self):
        self.notify.debug('enterFaceOff()')
        self.faceOff('faceoff-%d' % self.doId, self.startCamTrack)

    def startCamTrack(self):
        camera.wrtReparentTo(self)
        camTrack = Parallel()
        camTrack.append(LerpFunctionInterval(base.camLens.setMinFov, duration=1.0, fromData=self.camFov/(4./3.), toData=self.camMenuFov/(4./3.), blendType='easeInOut'))
        camTrack.append(LerpPosInterval(camera, 1.0, self.camPos, blendType='easeInOut'))
        camTrack.append(LerpHprInterval(camera, 1.0, self.camHpr, blendType='easeInOut'))
        menuTrack = Func(self.enterWaitForInput)
        track = Sequence(camTrack, menuTrack)
        track.start()

    def loadTrap(self, suit, trapid):
        self.notify.debug('loadTrap() trap: %d suit: %d' % (trapid, suit.doId))
        trapName = AvProps[TRAP][trapid]
        trap = BattleProps.globalPropPool.getProp(trapName)
        suit.battleTrap = trapid
        suit.battleTrapIsFresh = 0
        suit.battleTrapProp = trap
        self.notify.debug('suit.battleTrapProp = trap %s' % trap)
        if trap.getName() == 'traintrack':
            pass
        else:
            trap.wrtReparentTo(suit)
        distance = MovieUtil.SUIT_TRAP_DISTANCE
        if trapName == 'rake':
            distance = MovieUtil.SUIT_TRAP_RAKE_DISTANCE
            distance += MovieUtil.getSuitRakeOffset(suit)
            trap.setH(180)
            trap.setScale(0.7)
        elif trapName == 'trapdoor' or trapName == 'quicksand':
            trap.setScale(1.7)
        elif trapName == 'marbles':
            distance = MovieUtil.SUIT_TRAP_MARBLES_DISTANCE
            trap.setH(94)
        elif trapName == 'tnt':
            trap.setP(90)
            tip = trap.find('**/joint_attachEmitter')
            sparks = BattleParticles.createParticleEffect(file='tnt')
            trap.sparksEffect = sparks
            sparks.start(tip)
        trap.setPos(0, distance, 0)
        if isinstance(trap, Actor.Actor):
            frame = trap.getNumFrames(trapName) - 1
            trap.pose(trapName, frame)

    def removeTrap(self, suit, removeTrainTrack = False):
        self.notify.debug('removeTrap() from suit: %d, removeTrainTrack=%s' % (suit.doId, removeTrainTrack))
        if suit.battleTrapProp == None:
            self.notify.debug('suit.battleTrapProp == None, suit.battleTrap=%s setting to NO_TRAP, returning' % suit.battleTrap)
            suit.battleTrap = NO_TRAP
            return
        if suit.battleTrap == UBER_GAG_LEVEL_INDEX:
            if removeTrainTrack:
                self.notify.debug('doing removeProp on traintrack')
                MovieUtil.removeProp(suit.battleTrapProp)
                for otherSuit in self.suits:
                    if not otherSuit == suit:
                        otherSuit.battleTrapProp = None
                        self.notify.debug('351 otherSuit=%d otherSuit.battleTrapProp = None' % otherSuit.doId)
                        otherSuit.battleTrap = NO_TRAP
                        otherSuit.battleTrapIsFresh = 0

            else:
                self.notify.debug('deliberately not doing removeProp on traintrack')
        else:
            self.notify.debug('suit.battleTrap != UBER_GAG_LEVEL_INDEX')
            MovieUtil.removeProp(suit.battleTrapProp)
        suit.battleTrapProp = None
        self.notify.debug('360 suit.battleTrapProp = None')
        suit.battleTrap = NO_TRAP
        suit.battleTrapIsFresh = 0
        return

    def enterWaitForInput(self):
        self.clearAttacks()
        self.movieHasBeenMade = 0
        self.movieHasPlayed = 0
        self.rewardHasPlayed = 0
        self.movieRequested = 0
        
        camera.setPosHpr(self.camPos, self.camHpr)
        base.camLens.setMinFov(self.camMenuFov/(4./3.))
        NametagGlobals.setMasterArrowsOn(0)
        self.townBattle.exitOff()
        self.townBattle.setState('Attack')
        for toon in self.activeToons:
            self.townBattle.updateLaffMeter(self.activeToons.index(toon), toon.hp)
        for i in range(len(self.activeSuits)):
            self.townBattle.cogPanels[i].setCogInformation(self.activeSuits[i])
        
        if not self.tutorialFlag:
            self.startTimer()
        if self.needAdjust:
            self.requestAdjust()
        if self.needAdjustTownBattle:
            self.__adjustTownBattle()
        self.accept(self.localToonBattleEvent, self.__handleLocalToonBattleEvent)

    def exitWaitForInput(self):
        self.notify.debug('exitWaitForInput()')
        if self.localToonActive():
            self.townBattle.setState('Off')
            base.camLens.setMinFov(self.camFov/(4./3.))
            self.ignore(self.localToonBattleEvent)
            self.__stopTimer()
        return None

    def __handleLocalToonBattleEvent(self, response):
        self.exitWaitForInput()
        mode = response['mode']
        noAttack = 0
        if mode == 'Attack':
            self.notify.debug('got an attack')
            track = response['track']
            level = response['level']
            target = response['target']
            targetId = target
            if track == HEAL_TRACK:
                targetId = self.activeToons[target].doId
            elif not attackAffectsGroup(track, level):
                if target >= 0 and target < len(self.activeSuits):
                    targetId = self.activeSuits[target].doId
                else:
                    target = -1
            elif attackAffectsGroup(track, level):
                target = -1
                targetId = -1
            if len(self.luredSuits) > 0:
                if track == TRAP or track == LURE and not levelAffectsGroup(LURE, level):
                    if target != -1:
                        suit = self.findSuit(targetId)
                        if self.luredSuits.count(suit) != 0:
                            self.notify.warning('Suit: %d was lured!' % targetId)
                            track = -1
                            level = -1
                            targetId = -1
                elif track == LURE:
                    if levelAffectsGroup(LURE, level) and len(self.activeSuits) == len(self.luredSuits):
                        self.notify.warning('All suits are lured!')
                        track = -1
                        level = -1
                        targetId = -1
            if track == TRAP:
                self.needAdjustTownBattle = 1
                if target != -1:
                    if attackAffectsGroup(track, level):
                        pass
                    else:
                        suit = self.findSuit(targetId)
                        if suit.battleTrap != NO_TRAP:
                            self.notify.warning('Suit: %d was already trapped!' % targetId)
                            track = -1
                            level = -1
                            targetId = -1
            self.requestAttack(track, level, targetId)
            base.localAvatar.inventory.useItem(track, level)
        elif mode == 'Run':
            self.notify.debug('got a run')
            self.requestRun()
        elif mode == 'Pass':
            targetId = response['id']
            self.notify.debug('got a Pass')
            self.requestAttack(PASS, -1, -1)
        return

    def enterPlayMovie(self, ts):
        self.notify.debug('enterPlayMovie()')
        if self.hasLocalToon():
            NametagGlobals.setMasterArrowsOn(0)
        if ToontownBattleGlobals.SkipMovie:
            self.movie.play(ts, self.__handleMovieDone)
            self.movie.finish()
        else:
            self.movie.play(ts, self.__handleMovieDone)
        return None

    def __handleMovieDone(self):
        self.notify.debug('__handleMovieDone()')
        self.movieDone()
        self.movie.reset()

    def exitPlayMovie(self):
        self.notify.debug('exitPlayMovie()')
        self.movie.reset(finish=1)
        self.townBattleAttacks = ([-1,
          -1,
          -1,
          -1],
         [-1,
          -1,
          -1,
          -1],
         [-1,
          -1,
          -1,
          -1],
         [0,
          0,
          0,
          0])
        return None

    def __timedOut(self):
        self.notify.debug('WaitForInput timed out')
        self.exitWaitForInput()
        self.requestAttack(PASS, -1, -1)

    def clearAttacks(self):
        self.toonAttacks = {}
        self.suitAttacks = getDefaultSuitAttacks()

    def requestAttack(self, track, level, av):
        toonId = base.localAvatar.doId
        if self.activeToonIds.count(toonId) == 0:
            self.notify.warning('requestAttack() - toon: %d not in toon list' % toonId)
            return
        self.notify.debug('requestAttack(%d, %d, %d, %d)' % (toonId,
         track,
         level,
         av))
        toon = self.getToon(toonId)
        if toon == None:
            self.notify.warning('requestAttack() - no toon: %d' % toonId)
            return
        validResponse = 1
        if track == SOS:
            self.notify.debug('toon: %d calls for help' % toonId)
            self.toonAttacks[toonId] = getToonAttack(toonId, track=SOS, target=av)
        elif track == NPCSOS:
            self.notify.debug('toon: %d calls for help' % toonId)
            toon = self.getToon(toonId)
            if toon == None:
                return
            if toon.NPCFriendsDict.has_key(av):
                npcCollision = 0
                if self.npcAttacks.has_key(av):
                    callingToon = self.npcAttacks[av]
                    if self.activeToonIds.count(callingToon) == 1:
                        self.toonAttacks[toonId] = getToonAttack(toonId, track=PASS)
                        npcCollision = 1
                if npcCollision == 0:
                    self.toonAttacks[toonId] = getToonAttack(toonId, track=NPCSOS, level=5, target=av)
                    self.numNPCAttacks += 1
                    self.npcAttacks[av] = toonId
        elif track == PETSOS:
            self.notify.debug('toon: %d calls for pet: %d' % (toonId, av))
            toon = self.getToon(toonId)
            if toon == None:
                return
            self.toonAttacks[toonId] = getToonAttack(toonId, track=PETSOS, level=level, target=av)
        elif track == UN_ATTACK:
            self.notify.debug('toon: %d changed its mind' % toonId)
            self.toonAttacks[toonId] = getToonAttack(toonId, track=UN_ATTACK)
            if self.responses.has_key(toonId):
                self.responses[toonId] = 0
            validResponse = 0
        elif track == PASS:
            self.toonAttacks[toonId] = getToonAttack(toonId, track=PASS)
        elif track == FIRE:
            self.toonAttacks[toonId] = getToonAttack(toonId, track=FIRE, target=av)
        else:
            if toon.inventory.numItem(track, level) == 0:
                self.notify.warning('requestAttack() - toon has no item track: %d level: %d' % (track, level))
                self.toonAttacks[toonId] = getToonAttack(toonId)
                return
            if track == HEAL:
                self.toonAttacks[toonId] = getToonAttack(toonId, track=track, level=level, target=av)
            else:
                self.toonAttacks[toonId] = getToonAttack(toonId, track=track, level=level, target=av)
                if av == -1 and not attackAffectsGroup(track, level):
                    validResponse = 0
        self.setChosenToonAttacks(*self.getChosenToonAttacks())
        self.notify.debug('toon: %d chose an attack' % toonId)
        self.__requestMovie()
        return

    def requestRun(self):
        base.localAvatar.enterTeleportOut(callback=self.__runDone)

    def __runDone(self):
        for suit in self.suits:
            self.removeSuit(suit)
        doneStatus = 'run'
        messenger.send(self.townBattle.doneEvent, [doneStatus])
        base.cr.playGame.exitActiveZone()
        base.localAvatar.enable()
        zoneId = FunnyFarmGlobals.getHoodId(base.localAvatar.zoneId)
        base.cr.playGame.enterHood(zoneId)

    def __requestMovie(self, timeout = 0):
        movieDelay = 0
        if len(self.activeToonIds) == 0:
            self.notify.warning('only pending toons left in battle %s, toons = %s' % (self.doId, self.toons))
        elif len(self.activeSuits) == 0:
            self.notify.warning('only pending suits left in battle %s, suits = %s' % (self.doId, self.suits))
        elif len(self.activeToonIds) > 1 and not timeout:
            movieDelay = 1
        if movieDelay:
            taskMgr.doMethodLater(0.8, self.__makeMovie, 'make-movie')
        else:
            self.__makeMovie()

    def __makeMovie(self, task = None):
        self.notify.debug('makeMovie()')
        if self.movieHasBeenMade == 1:
            self.notify.debug('__makeMovie() - movie has already been made')
            return
        self.movieRequested = 0
        self.movieHasBeenMade = 1
        self.movieHasPlayed = 0
        self.rewardHasPlayed = 0
        for t in self.activeToonIds:
            if not self.toonAttacks.has_key(t):
                self.toonAttacks[t] = getToonAttack(t)
            attack = self.toonAttacks[t]
            if attack[TOON_TRACK_COL] == PASS or attack[TOON_TRACK_COL] == UN_ATTACK:
                self.toonAttacks[t] = getToonAttack(t)
            if self.toonAttacks[t][TOON_TRACK_COL] != NO_ATTACK:
                self.addHelpfulToon(t)

        self.battleCalc.calculateRound()
        for t in self.activeToonIds:
            self.sendEarnedExperience(t)

        self.setMovie(*self.getMovie())
        self.enterPlayMovie(0)
        return Task.done

    def sendEarnedExperience(self, toonId):
        toon = self.getToon(toonId)
        if toon != None:
            expList = self.battleCalc.toonSkillPtsGained.get(toonId, None)
            if expList == None:
                toon.setEarnedExperience([])
            else:
                roundList = []
                for exp in expList:
                    roundList.append(int(exp + 0.5))

                toon.setEarnedExperience(roundList)
        return

    def setMovie(self, active, toons, suits, id0, tr0, le0, tg0, hp0, ac0, hpb0, kbb0, died0, revive0, id1, tr1, le1, tg1, hp1, ac1, hpb1, kbb1, died1, revive1, id2, tr2, le2, tg2, hp2, ac2, hpb2, kbb2, died2, revive2, id3, tr3, le3, tg3, hp3, ac3, hpb3, kbb3, died3, revive3, sid0, at0, stg0, dm0, sd0, sb0, st0, hit0, sid1, at1, stg1, dm1, sd1, sb1, st1, hit1, sid2, at2, stg2, dm2, sd2, sb2, st2, hit2, sid3, at3, stg3, dm3, sd3, sb3, st3, hit3):
        if self.__battleCleanedUp:
            return
        self.notify.debug('setMovie()')
        if int(active) == 1:
            self.notify.debug('setMovie() - movie is active')
            self.movie.genAttackDicts(toons, suits, id0, tr0, le0, tg0, hp0, ac0, hpb0, kbb0, died0, revive0, id1, tr1, le1, tg1, hp1, ac1, hpb1, kbb1, died1, revive1, id2, tr2, le2, tg2, hp2, ac2, hpb2, kbb2, died2, revive2, id3, tr3, le3, tg3, hp3, ac3, hpb3, kbb3, died3, revive3, sid0, at0, stg0, dm0, sd0, sb0, st0, hit0, sid1, at1, stg1, dm1, sd1, sb1, st1, hit1, sid2, at2, stg2, dm2, sd2, sb2, st2, hit2, sid3, at3, stg3, dm3, sd3, sb3, st3, hit3)

    def getMovie(self):
        suitIds = []
        for s in self.activeSuits:
            suitIds.append(s.doId)

        p = [self.movieHasBeenMade]
        p.append(self.activeToonIds)
        p.append(suitIds)
        for t in self.activeToonIds:
            if self.toonAttacks.has_key(t):
                ta = self.toonAttacks[t]
                index = -1
                id = ta[TOON_ID_COL]
                if id != -1:
                    index = self.activeToonIds.index(id)
                track = ta[TOON_TRACK_COL]
                if (track == NO_ATTACK or attackAffectsGroup(track, ta[TOON_LVL_COL])) and track != NPCSOS and track != PETSOS:
                    target = -1
                    if track == HEAL:
                        if ta[TOON_LVL_COL] == 1:
                            ta[TOON_HPBONUS_COL] = random.randint(0, 10000)
                elif track == SOS or track == NPCSOS or track == PETSOS:
                    target = ta[TOON_TGT_COL]
                elif track == HEAL:
                    target = t
                elif suitIds.count(ta[TOON_TGT_COL]) != 0:
                    target = suitIds.index(ta[TOON_TGT_COL])
                else:
                    target = -1
                p = p + [index,
                 track,
                 ta[TOON_LVL_COL],
                 target]
                p = p + ta[4:]
            else:
                index = self.activeToonIds.index(t)
                attack = getToonAttack(index)
                p = p + attack

        for i in range(4 - len(self.activeToonIds)):
            p = p + getToonAttack(-1)

        for sa in self.suitAttacks:
            index = -1
            id = sa[SUIT_ID_COL]
            if id != -1:
                index = suitIds.index(id)
            if sa[SUIT_ATK_COL] == -1:
                targetIndex = -1
            else:
                targetIndex = sa[SUIT_TGT_COL]
                if targetIndex == -1:
                    self.notify.debug('suit attack: %d must be group' % sa[SUIT_ATK_COL])
                else:
                    toonId = self.activeToonIds[targetIndex]
            p = p + [index, sa[SUIT_ATK_COL], targetIndex]
            sa[SUIT_TAUNT_COL] = 0
            if sa[SUIT_ATK_COL] != -1:
                suit = self.findSuit(id)
                sa[SUIT_TAUNT_COL] = getAttackTauntIndexFromIndex(suit, sa[SUIT_ATK_COL])
            p = p + sa[3:]

        return p

    def setChosenToonAttacks(self, ids, tracks, levels, targets):
        if self.__battleCleanedUp:
            return
        self.notify.debug('setChosenToonAttacks() - (%s), (%s), (%s), (%s)' % (ids,
         tracks,
         levels,
         targets))
        toonIndices = []
        targetIndices = []
        unAttack = 0
        localToonInList = 0
        for i in range(len(ids)):
            track = tracks[i]
            level = levels[i]
            toon = self.findToon(ids[i])
            if toon == None or self.activeToons.count(toon) == 0:
                self.notify.warning('setChosenToonAttacks() - toon gone or not in battle: %d!' % ids[i])
                toonIndices.append(-1)
                tracks.append(-1)
                levels.append(-1)
                targetIndices.append(-1)
                continue
            if toon == base.localAvatar:
                localToonInList = 1
            toonIndices.append(self.activeToons.index(toon))
            if track == SOS:
                targetIndex = -1
            elif track == NPCSOS:
                targetIndex = -1
            elif track == PETSOS:
                targetIndex = -1
            elif track == PASS:
                targetIndex = -1
                tracks[i] = PASS_ATTACK
            elif attackAffectsGroup(track, level):
                targetIndex = -1
            elif track == HEAL:
                target = self.findToon(targets[i])
                if target != None and self.activeToons.count(target) != 0:
                    targetIndex = self.activeToons.index(target)
                else:
                    targetIndex = -1
            elif track == UN_ATTACK:
                targetIndex = -1
                tracks[i] = NO_ATTACK
                if toon == base.localAvatar:
                    unAttack = 1
                    self.choseAttackAlready = 0
            elif track == NO_ATTACK:
                targetIndex = -1
            else:
                target = self.findSuit(targets[i])
                if target != None and self.activeSuits.count(target) != 0:
                    targetIndex = self.activeSuits.index(target)
                else:
                    targetIndex = -1
            targetIndices.append(targetIndex)

        for i in range(4 - len(ids)):
            toonIndices.append(-1)
            tracks.append(-1)
            levels.append(-1)
            targetIndices.append(-1)

        self.townBattleAttacks = (toonIndices,
         tracks,
         levels,
         targetIndices)
        if self.localToonActive() and localToonInList == 1:
            if unAttack == 1 and self.townBattle.fsm.getCurrentState().getName() != 'Off':
                if self.townBattle.fsm.getCurrentState().getName() != 'Attack':
                    self.townBattle.setState('Attack')
            self.townBattle.updateChosenAttacks(self.townBattleAttacks[0], self.townBattleAttacks[1], self.townBattleAttacks[2], self.townBattleAttacks[3])
        return

    def getChosenToonAttacks(self):
        ids = []
        tracks = []
        levels = []
        targets = []
        for t in self.activeToonIds:
            if t in self.toonAttacks.keys():
                ta = self.toonAttacks[t]
            else:
                ta = getToonAttack(t)
            ids.append(t)
            tracks.append(ta[TOON_TRACK_COL])
            levels.append(ta[TOON_LVL_COL])
            targets.append(ta[TOON_TGT_COL])

        return [ids,
         tracks,
         levels,
         targets]

    def setBattleExperience(self, id0, origExp0, earnedExp0, origQuests0, items0, missedItems0, origMerits0, merits0, parts0, id1, origExp1, earnedExp1, origQuests1, items1, missedItems1, origMerits1, merits1, parts1, id2, origExp2, earnedExp2, origQuests2, items2, missedItems2, origMerits2, merits2, parts2, id3, origExp3, earnedExp3, origQuests3, items3, missedItems3, origMerits3, merits3, parts3, deathList, uberList, helpfulToonsList):
        if self.__battleCleanedUp:
            return
        self.movie.genRewardDicts(id0, origExp0, earnedExp0, origQuests0, items0, missedItems0, origMerits0, merits0, parts0, id1, origExp1, earnedExp1, origQuests1, items1, missedItems1, origMerits1, merits1, parts1, id2, origExp2, earnedExp2, origQuests2, items2, missedItems2, origMerits2, merits2, parts2, id3, origExp3, earnedExp3, origQuests3, items3, missedItems3, origMerits3, merits3, parts3, deathList, uberList, helpfulToonsList)

    def getBattleExperience(self):
        returnValue = BattleExperienceAI.getBattleExperience(4, self.activeToonIds, self.toonExp, self.battleCalc.toonSkillPtsGained, self.toonOrigQuests, self.toonItems, self.toonOrigMerits, self.toonMerits, self.toonParts, self.suitsKilled, self.helpfulToons)
        return returnValue

    def assignRewards(self):
        if self.rewardHasPlayed == 1:
            self.notify.debug('assignRewards() - reward has already played')
            return
        self.rewardHasPlayed = 1
        BattleExperienceAI.assignRewards(self.activeToonIds, self.battleCalc.toonSkillPtsGained, self.suitsKilled, base.localAvatar.getZoneId(), self.helpfulToons)

    def movieDone(self):
        self.exitPlayMovie()
        self.movieHasBeenMade = 0
        self.movieHasPlayed = 1
        self.rewardHasPlayed = 0
        self.movieRequested = 0
        allSuitsDied = 0
        toonDied = 0
        suitsToRemove = []
        for suit in self.suits:
            if suit.getHP() <= 0:
                encounter = {'type': suit.dna.name,
                 'level': suit.getActualLevel(),
                 'track': suit.dna.dept,
                 'isSkelecog': suit.getSkelecog(),
                 'isForeman': suit.isForeman(),
                 'isVP': 0,
                 'isCFO': 0,
                 'isSupervisor': suit.isSupervisor(),
                 'isVirtual': suit.isVirtual(),
                 'hasRevives': suit.getMaxSkeleRevives(),
                 'activeToons': self.activeToonIds[:]}
                self.suitsKilled.append(encounter)
                suitsToRemove.append(suit)
                self.needAdjust = 1
                self.needAdjustTownBattle = 1
        for suit in suitsToRemove:
            self.removeSuit(suit)
        if len(self.suits) == 0:
            allSuitsDied = 1
        for toon in self.toons:
            if toon.hp <= 0:
                self.toons.remove(toon)
                toonDied = 1
        if toonDied:
            for suit in self.suits:
                self.removeSuit(suit)
            doneStatus = 'defeat'
            messenger.send(self.townBattle.doneEvent, [doneStatus])
            return
        if not allSuitsDied:
            if self.needAdjust:
                if len(self.joiningSuits) == 0:
                    self.requestAdjust()
                # If a suit joined at the last minute, it'll wait for him
                self.acceptOnce('battle-%d-adjustDone' % self.doId, self.startCamTrack)
            else:
                self.startCamTrack()
        else:
            for toonId in self.activeToonIds:
                toon = self.getToon(toonId)
                if toon:
                    self.toonItems[toonId] = base.cr.questManager.recoverItems(toon, self.suitsKilled, toon.getZoneId())
                    # Undecided whether we'll have the merits system or not
                    # self.toonMerits[toonId] = self.air.promotionMgr.recoverMerits(toon, self.suitsKilled, self.zoneId)
            self.setJoinable(0)
            self.setBattleExperience(*self.getBattleExperience())
            self.assignRewards()
            if self.tutorialFlag:
                self.movie.playTutorialReward(0, base.localAvatar.getName(), self.battleDone)
            else:
                self.movie.playReward(0, base.localAvatar.getName(), self.battleDone)
            for t in self.activeToons:
                self.activeToons.remove(t)
        return

    def removeSuit(self, suit):
        if self.suits.count(suit) != 0:
            self.suits.remove(suit)
        if self.joiningSuits.count(suit) != 0:
            self.joiningSuits.remove(suit)
        if self.pendingSuits.count(suit) != 0:
            self.pendingSuits.remove(suit)
        if self.activeSuits.count(suit) != 0:
            self.activeSuits.remove(suit)
        self.suitGone = 1
        suit.disable()
        suit.delete()
        messenger.send('removeActiveSuit', [suit.doId])
        messenger.send('upkeepPopulation-%d' % base.localAvatar.zoneId, [None])

    def setMembers(self, suits, suitsJoining, suitsPending, suitsActive, suitsLured, suitTraps):
        if self.__battleCleanedUp:
            return
        self.notify.debug('setMembers() - suits: %s suitsJoining: %s suitsPending: %s suitsActive: %s suitsLured: %s suitTraps: %s' % (suits,
         suitsJoining,
         suitsPending,
         suitsActive,
         suitsLured,
         suitTraps))
        oldsuits = self.suits
        self.suits = []
        suitGone = 0
        for s in suits:
            suit = s
            self.suits.append(suit)
            try:
                suit.battleTrap
            except:
                suit.battleTrap = NO_TRAP
                suit.battleTrapProp = None
                self.notify.debug('496 suit.battleTrapProp = None')
                suit.battleTrapIsFresh = 0

        numSuitsThatDied = 0
        for s in oldsuits:
            if self.suits.count(s) == 0:
                self.removeSuit(s)
                numSuitsThatDied += 1
                self.notify.debug('suit %d dies, numSuitsThatDied=%d' % (s.doId, numSuitsThatDied))

        if numSuitsThatDied == 4:
            trainTrap = self.find('**/traintrack')
            if not trainTrap.isEmpty():
                self.notify.debug('removing old train trap when 4 suits died')
                trainTrap.removeNode()
        for s in suitsJoining:
            suit = self.suits[int(s)]
            if suit != None and self.joiningSuits.count(suit) == 0:
                self.makeSuitJoin(suit)

        for s in suitsPending:
            suit = self.suits[int(s)]
            if suit != None and self.pendingSuits.count(suit) == 0:
                self.__makeSuitPending(suit)

        oldLuredSuits = self.luredSuits
        self.luredSuits = []
        for s in suitsLured:
            suit = self.suits[int(s)]
            if suit != None:
                self.luredSuits.append(suit)
                if oldLuredSuits.count(suit) == 0:
                    self.needAdjustTownBattle = 1

        if self.needAdjustTownBattle == 0:
            for s in oldLuredSuits:
                if self.luredSuits.count(s) == 0:
                    self.needAdjustTownBattle = 1

        index = 0
        oldSuitTraps = self.suitTraps
        self.suitTraps = suitTraps
        for s in suitTraps:
            trapid = int(s)
            if trapid == 9:
                trapid = -1
            suit = self.suits[index]
            index += 1
            if suit != None:
                #if (trapid == NO_TRAP or trapid != suit.battleTrap) and suit.battleTrapProp != None:
                    #self.notify.debug('569 calling self.removeTrap, suit=%d' % suit.doId)
                    #self.removeTrap(suit)
                if trapid != NO_TRAP and suit.battleTrapProp == None:
                    if self.townBattle.fsm.getCurrentState().getName() != 'Off':
                        self.loadTrap(suit, trapid)

        if len(oldSuitTraps) != len(self.suitTraps):
            self.needAdjustTownBattle = 1
        else:
            for i in range(len(oldSuitTraps)):
                if oldSuitTraps[i] == '9' and self.suitTraps[i] != '9' or oldSuitTraps[i] != '9' and self.suitTraps[i] == '9':
                    self.needAdjustTownBattle = 1
                    break
        if suitGone:
            validSuits = []
            for s in self.suits:
                if s != None:
                    validSuits.append(s)

            self.suits = validSuits
            self.needAdjustTownBattle = 1
        self.__requestAdjustTownBattle()
        return

    def getMembers(self):
        suits = []
        for s in self.suits:
            suits.append(s)

        joiningSuits = ''
        for s in self.joiningSuits:
            joiningSuits += str(suits.index(s))

        pendingSuits = ''
        for s in self.pendingSuits:
            pendingSuits += str(suits.index(s))

        activeSuits = ''
        for s in self.activeSuits:
            activeSuits += str(suits.index(s))

        luredSuits = ''
        for s in self.luredSuits:
            luredSuits += str(suits.index(s))

        suitTraps = ''
        for s in self.suits:
            if s.battleTrap == NO_TRAP:
                suitTraps += '9'
            elif s.battleTrap == BattleCalculator.TRAP_CONFLICT:
                suitTraps += '9'
            else:
                suitTraps += str(s.battleTrap)

        self.notify.debug('getMembers() - suits: %s joiningSuits: %s pendingSuits: %s activeSuits: %s luredSuits: %s suitTraps: %s' % (suits,
         joiningSuits,
         pendingSuits,
         activeSuits,
         luredSuits,
         suitTraps))
        return [suits,
         joiningSuits,
         pendingSuits,
         activeSuits,
         luredSuits,
         suitTraps]

    def suitRequestJoin(self, suit):
        self.notify.debug('suitRequestJoin(%d)' % suit.getDoId())
        if self.suitCanJoin():
            self.addSuit(suit)
            self.joinSuit(suit)
            self.setMembers(*self.getMembers())
            self.makeSuitJoin(suit)
            return 1
        else:
            self.notify.warning('suitRequestJoin() - not joinable - joinable state: %s max suits: %d' % (self.isJoinable(), self.maxSuits))
            return 0

    def addSuit(self, suit):
        self.notify.debug('addSuit(%d)' % suit.doId)
        if suit not in self.suits:
            self.suits.append(suit)
        suit.battleTrap = NO_TRAP
        if len(self.suits) == self.maxSuits:
            # We've hit the max; no more suits can join this battle, ever.
            self.setJoinable(0)

    def joinSuit(self, suit):
        self.joiningSuits.append(suit)

    def __createJoinInterval(self, av, destPos, destHpr, name, callback, toon = 0):
        joinTrack = Sequence()
        joinTrack.append(Func(Emote.globalEmote.disableAll, av, 'dbattlebase, createJoinInterval'))
        avPos = av.getPos(self)
        avPos = Point3(avPos[0], avPos[1], 0.0)
        av.setShadowHeight(0)
        plist = self.buildJoinPointList(avPos, destPos, toon)
        if len(plist) == 0:
            joinTrack.append(Func(av.headsUp, self, destPos))
            if toon == 0:
                timeToDest = self.calcSuitMoveTime(avPos, destPos)
                joinTrack.append(Func(av.loop, 'walk'))
            else:
                timeToDest = self.calcToonMoveTime(avPos, destPos)
                joinTrack.append(Func(av.loop, 'run'))
            if timeToDest > BATTLE_SMALL_VALUE:
                joinTrack.append(LerpPosInterval(av, timeToDest, destPos, other=self))
                totalTime = timeToDest
            else:
                totalTime = 0
        else:
            timeToPerimeter = 0
            if toon == 0:
                timeToPerimeter = self.calcSuitMoveTime(plist[0], avPos)
                timePerSegment = 10.0 / BattleBase.suitSpeed
                timeToDest = self.calcSuitMoveTime(BattleBase.posA, destPos)
            else:
                timeToPerimeter = self.calcToonMoveTime(plist[0], avPos)
                timePerSegment = 10.0 / BattleBase.toonSpeed
                timeToDest = self.calcToonMoveTime(BattleBase.posE, destPos)
            totalTime = timeToPerimeter + (len(plist) - 1) * timePerSegment + timeToDest
            if totalTime > MAX_JOIN_T:
                self.notify.warning('__createJoinInterval() - time: %f' % totalTime)
            joinTrack.append(Func(av.headsUp, self, plist[0]))
            if toon == 0:
                joinTrack.append(Func(av.loop, 'walk'))
            else:
                joinTrack.append(Func(av.loop, 'run'))
            joinTrack.append(LerpPosInterval(av, timeToPerimeter, plist[0], other=self))
            for p in plist[1:]:
                joinTrack.append(Func(av.headsUp, self, p))
                joinTrack.append(LerpPosInterval(av, timePerSegment, p, other=self))

            joinTrack.append(Func(av.headsUp, self, destPos))
            joinTrack.append(LerpPosInterval(av, timeToDest, destPos, other=self))
        joinTrack.append(Func(av.loop, 'neutral'))
        joinTrack.append(Func(av.headsUp, self, Point3(0, 0, 0)))
        tval = totalTime
        joinTrack.append(Func(Emote.globalEmote.releaseAll, av, 'dbattlebase, createJoinInterval'))
        joinTrack.append(Func(callback, av))
        if av == base.localAvatar:
            camTrack = Sequence()

            def setCamFov(fov):
                base.camLens.setMinFov(fov/(4./3.))

            camTrack.append(Func(setCamFov, self.camFov))
            camTrack.append(Func(camera.wrtReparentTo, self))
            camTrack.append(Func(camera.setPos, self.camJoinPos))
            camTrack.append(Func(camera.setHpr, self.camJoinHpr))
            return Parallel(joinTrack, camTrack, name=name)
        else:
            return Sequence(joinTrack, name=name)

    def makeSuitJoin(self, suit):
        self.notify.debug('makeSuitJoin(%d)' % suit.doId)
        spotIndex = len(self.pendingSuits) + len(self.joiningSuits)
        # self.joiningSuits.append(suit)
        suit.enterBattle()
        openSpot = self.suitPendingPoints[spotIndex]
        pos = openSpot[0]
        hpr = VBase3(openSpot[1], 0.0, 0.0)
        trackName = 'to-pending-suit-%d' % suit.doId
        track = self.__createJoinInterval(suit, pos, hpr, trackName, self.__handleSuitJoinDone)
        track.start()
        # self.storeInterval(track, trackName)
        if ToontownBattleGlobals.SkipMovie:
            track.finish()

    def __handleSuitJoinDone(self, suit):
        self.notify.debug('suit: %d is now pending' % suit.doId)
        if not suit.isEmpty():
            self.joiningSuits.remove(suit)
            self.pendingSuits.append(suit)
        self.setMembers(*self.getMembers())
        self.needAdjust = 1
        self.requestAdjust()
        self.joinTrack = None

    def __makeSuitPending(self, suit):
        self.notify.debug('__makeSuitPending(%d)' % suit.doId)
        self.clearInterval('to-pending-suit-%d' % suit.doId, finish=1)
        if self.joiningSuits.count(suit):
            self.joiningSuits.remove(suit)

    def requestAdjust(self):
        cstate = self.townBattle.fsm.getCurrentState().getName()
        if self.movieHasPlayed == 1 or cstate != 'Off':
            if not self.adjusting:
                if self.needAdjust == 1:
                    self.adjustingSuits = []
                    for s in self.pendingSuits:
                        self.adjustingSuits.append(s)
                    self.enterAdjusting()
                else:
                    self.notify.debug('requestAdjust() - dont need to')
            else:
                self.notify.debug('requestAdjust() - already adjusting')
        else:
            self.notify.debug('requestAdjust() - in state: %s' % cstate)

    def enterAdjusting(self):
        self.notify.debug('enterAdjusting()')
        self.adjusting = 1
        if self.localToonActive():
            self.__stopTimer()
        self.__adjust()
        return None

    def exitAdjusting(self):
        self.notify.debug('exitAdjusting()')
        self.adjusting = 0
        self.finishInterval(self.adjustName)
        currStateName = self.townBattle.fsm.getCurrentState().getName()
        if currStateName != 'Off':
            self.startTimer()
        return None

    def __adjust(self):
        self.notify.debug('__adjust()')
        adjustTrack = Parallel()
        if len(self.pendingSuits) > 0 or self.suitGone == 1:
            self.suitGone = 0
            numSuits = len(self.pendingSuits) + len(self.activeSuits) - 1
            index = 0
            for suit in self.activeSuits:
                point = self.suitPoints[numSuits][index]
                pos = suit.getPos(self)
                destPos = point[0]
                if self.isSuitLured(suit) == 1:
                    destPos = Point3(destPos[0], destPos[1] - MovieUtil.SUIT_LURE_DISTANCE, destPos[2])
                if pos != destPos:
                    destHpr = VBase3(point[1], 0.0, 0.0)
                    adjustTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
                index += 1

            for suit in self.pendingSuits:
                point = self.suitPoints[numSuits][index]
                destPos = point[0]
                destHpr = VBase3(point[1], 0.0, 0.0)
                adjustTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
                index += 1

        if len(adjustTrack) > 0:
            self.notify.debug('creating adjust multitrack')
            e = Func(self.__handleAdjustDone)
            track = Sequence(adjustTrack, e, name=self.adjustName)
            self.storeInterval(track, self.adjustName)
            track.start()
            if ToontownBattleGlobals.SkipMovie:
                track.finish()
        else:
            self.notify.warning('adjust() - nobody needed adjusting')
            self.__adjustDone()

    def createAdjustInterval(self, av, destPos, destHpr, toon = 0, run = 0):
        if run == 1:
            adjustTime = self.calcToonMoveTime(destPos, av.getPos(self))
        else:
            adjustTime = self.calcSuitMoveTime(destPos, av.getPos(self))
        self.notify.debug('creating adjust interval for: %d' % av.doId)
        adjustTrack = Sequence()
        if run == 1:
            adjustTrack.append(Func(av.loop, 'run'))
        else:
            adjustTrack.append(Func(av.loop, 'walk'))
        adjustTrack.append(Func(av.headsUp, self, destPos))
        adjustTrack.append(LerpPosInterval(av, adjustTime, destPos, other=self))
        adjustTrack.append(Func(av.setHpr, self, destHpr))
        adjustTrack.append(Func(av.loop, 'neutral'))
        return adjustTrack

    def __handleAdjustDone(self):
        self.notify.debug('__handleAdjustDone() - client adjust finished')
        self.clearInterval(self.adjustName)
        self.__adjustDone()

    def __addTrainTrapForNewSuits(self):
        hasTrainTrap = False
        trapInfo = None
        for otherSuit in self.activeSuits:
            if otherSuit.battleTrap == UBER_GAG_LEVEL_INDEX:
                hasTrainTrap = True

        if hasTrainTrap:
            for curSuit in self.activeSuits:
                if not curSuit.battleTrap == UBER_GAG_LEVEL_INDEX:
                    oldBattleTrap = curSuit.battleTrap
                    curSuit.battleTrap = UBER_GAG_LEVEL_INDEX
                    self.battleCalc.addTrainTrapForJoiningSuit(curSuit.doId)
                    self.notify.debug('setting traintrack trap for joining suit %d oldTrap=%s' % (curSuit.doId, oldBattleTrap))
        return

    def __adjustDone(self):
        self.notify.debug('__adjustDone()')
        self.exitAdjusting()
        for s in self.adjustingSuits:
            self.pendingSuits.remove(s)
            self.activeSuits.append(s)
        self.adjustingSuits = []
        self.adjustingToons = []
        self.__addTrainTrapForNewSuits()
        self.setMembers(*self.getMembers())
        self.needAdjust = 0
        if len(self.pendingSuits) > 0:
            self.notify.debug('__adjustDone() - need to adjust again')
            self.needAdjust = 1
            self.requestAdjust()
            return
        messenger.send('battle-%d-adjustDone' % self.doId)

    def __stopAdjusting(self):
        self.notify.debug('__stopAdjusting()')
        self.clearInterval(self.adjustName)

    def __requestAdjustTownBattle(self):
        self.notify.debug('__requestAdjustTownBattle() curstate = %s' % self.townBattle.fsm.getCurrentState().getName())
        if self.townBattle.fsm.getCurrentState().getName() != 'Off':
            self.__adjustTownBattle()
        else:
            self.needAdjustTownBattle = 1

    def __adjustTownBattle(self):
        self.notify.debug('__adjustTownBattle()')
        if self.localToonActive() and len(self.activeSuits) > 0:
            self.notify.debug('__adjustTownBattle() - adjusting town battle')
            luredSuits = []
            for suit in self.luredSuits:
                if suit not in self.activeSuits:
                    self.notify.error('lured suit not in self.activeSuits')
                luredSuits.append(self.activeSuits.index(suit))

            trappedSuits = []
            for suit in self.activeSuits:
                if suit.battleTrap != NO_TRAP:
                    trappedSuits.append(self.activeSuits.index(suit))

            self.townBattle.adjustCogsAndToons(self.activeSuits, luredSuits, trappedSuits, self.activeToons)
            if hasattr(self, 'townBattleAttacks'):
                self.townBattle.updateChosenAttacks(self.townBattleAttacks[0], self.townBattleAttacks[1], self.townBattleAttacks[2], self.townBattleAttacks[3])
        self.needAdjustTownBattle = 0

    def isSuitLured(self, suit):
        if self.luredSuits.count(suit) != 0:
            return 1
        return 0

    def unlureSuit(self, suit):
        self.notify.debug('movie unluring suit %s' % suit.doId)
        if self.luredSuits.count(suit) != 0:
            self.luredSuits.remove(suit)
            self.needAdjustTownBattle = 1
        return None

    def lureSuit(self, suit):
        self.notify.debug('movie luring suit %s' % suit.doId)
        if self.luredSuits.count(suit) == 0:
            self.luredSuits.append(suit)
            self.needAdjustTownBattle = 1
        return None

    def getActorPosHpr(self, actor, actorList = []):
        if isinstance(actor, Suit.Suit):
            if actorList == []:
                actorList = self.activeSuits
            if actorList.count(actor) != 0:
                numSuits = len(actorList) - 1
                index = actorList.index(actor)
                point = self.suitPoints[numSuits][index]
                return (Point3(point[0]), VBase3(point[1], 0.0, 0.0))
            else:
                self.notify.warning('getActorPosHpr() - suit not active')
        else:
            if actorList == []:
                actorList = self.activeToons
            if actorList.count(actor) != 0:
                numToons = len(actorList) - 1
                index = actorList.index(actor)
                point = self.toonPoints[numToons][index]
                return (Point3(point[0]), VBase3(point[1], 0.0, 0.0))
            else:
                self.notify.warning('getActorPosHpr() - toon not active')

    def findSuit(self, id):
        for s in self.suits:
            if s.doId == id:
                return s
        return None

    def findToon(self, id):
        toon = self.getToon(id)
        if toon == None:
            return
        for t in self.toons:
            if t == toon:
                return t
        return None

    def getToon(self, toonId):
        return base.localAvatar

    def setJoinable(self, flag):
        self.joinable = flag

    def isJoinable(self):
        streetJoinable = base.air.suitPlanners[base.localAvatar.zoneId].battlesJoinable
        return streetJoinable and self.joinable

    def suitCanJoin(self):
        return len(self.suits) < self.maxSuits and self.isJoinable()

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

    def localToonPendingOrActive(self):
        return 1

    def localToonActive(self):
        return 1

    def hasLocalToon(self):
        return 1

    def battleDone(self):
        doneStatus = 'victory'
        messenger.send(self.townBattle.doneEvent, [doneStatus])
