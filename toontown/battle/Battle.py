from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from otp.nametag import NametagGlobals
from otp.nametag.NametagConstants import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.suit import Suit
from BattleCalculator import BattleCalculator
from BattleBase import *
from SuitBattleGlobals import *
import BattleExperienceAI
import Movie
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

    def __init__(self, townBattle, toons=[], suits=[], bldg=0, tutorialFlag=0, secretArea=0):
        self.doId = id(self)
        NodePath.__init__(self, 'Battle-%d' % self.doId)
        BattleBase.__init__(self)
        self.townBattle = townBattle
        self.toons = toons
        self.suits = suits
        self.bldg = bldg
        self.tutorialFlag = tutorialFlag
        self.secretArea = secretArea
        self.movie = Movie.Movie(self)
        self.timerCountdownTaskName = 'timer-countdown'
        self.timer = Timer()
        self.battleCalc = BattleCalculator(self, tutorialFlag)
        self.localToonBattleEvent = 'battleEvent-%d' % self.doId
        self.luredSuits = []
        self.__battleCleanedUp = 0
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

    def enter(self):
        self.enterFaceOff()
        self.townBattle.enter(self.localToonBattleEvent, bldg=self.bldg, tutorialFlag=self.tutorialFlag)
        self.activeToons = self.toons
        self.activeSuits = self.suits
        self.activeToonIds = [] # for AI functions
        for suit in self.activeSuits:
            suit.enterBattle()
        for t in self.activeToons:
            self.activeToonIds.append(t.doId)
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

    def cleanupBattle(self):
        if self.__battleCleanedUp:
            return
        self.notify.debug('cleanupBattle(%s)' % self.doId)
        self.__battleCleanedUp = 1
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        NametagGlobals.setMasterArrowsOn(1)
        self.ignoreAll()
        for suit in self.activeSuits:
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

        return

    def getToon(self, toonId):
        return base.localAvatar

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
        taunt = getFaceoffTaunt(suit.getStyleName(), suit.doId)
        # temporary for the easter egg; will be removed after 1.3.1
        if self.secretArea:
            suitTrack.append(Func(suit.setChatMuted, '...', CFSpeech | CFTimeout))
        else:
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

    def enterFaceOff(self):
        self.notify.debug('enterFaceOff()')
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
        self.clearAttacks()
        camera.setPosHpr(self.camPos, self.camHpr)
        base.camLens.setMinFov(self.camMenuFov/(4./3.))
        NametagGlobals.setMasterArrowsOn(0)
        self.townBattle.exitOff()
        self.townBattle.setState('Attack')
        
        for toon in self.activeToons:
            self.townBattle.updateLaffMeter(self.activeToons.index(toon), toon.hp)
        for i in range(len(self.activeSuits)):
            self.townBattle.cogPanels[i].setCogInformation(self.activeSuits[i])
        
        self.accept(self.localToonBattleEvent, self.__handleLocalToonBattleEvent)
        if not self.tutorialFlag:
            self.startTimer()

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
            targetId = self.activeSuits[target].doId
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
                self.notify.warning('requestAttack() - toon has no item track:                     %d level: %d' % (track, level))
                self.toonAttacks[toonId] = getToonAttack(toonId)
                return
            if track == HEAL:
                if self.runningToons.count(av) == 1 or attackAffectsGroup(track, level) and len(self.activeToonIds) < 2:
                    self.toonAttacks[toonId] = getToonAttack(toonId, track=UN_ATTACK)
                    validResponse = 0
                else:
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
        for suit in self.activeSuits:
            self.removeSuit(suit)
        doneStatus = 'run'
        messenger.send(self.townBattle.doneEvent, [doneStatus])
        if base.cr.playGame.hood:
            base.cr.playGame.exitHood()
        elif base.cr.playGame.street:
            base.cr.playGame.exitStreet()
        elif base.cr.playGame.place:
            base.cr.playGame.exitPlace()
        base.localAvatar.enable()
        zoneId = base.avatarData.setLastHood
        base.cr.enterHood(zoneId)

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

    def setMovie(self, active, toons, suits, id0, tr0, le0, tg0, hp0, ac0, hpb0, kbb0, died0, revive0, id1, tr1, le1, tg1, hp1, ac1, hpb1, kbb1, died1, revive1, id2, tr2, le2, tg2, hp2, ac2, hpb2, kbb2, died2, revive2, id3, tr3, le3, tg3, hp3, ac3, hpb3, kbb3, died3, revive3, sid0, at0, stg0, dm0, sd0, sb0, st0, sid1, at1, stg1, dm1, sd1, sb1, st1, sid2, at2, stg2, dm2, sd2, sb2, st2, sid3, at3, stg3, dm3, sd3, sb3, st3):
        if self.__battleCleanedUp:
            return
        self.notify.debug('setMovie()')
        if int(active) == 1:
            self.notify.debug('setMovie() - movie is active')
            self.movie.genAttackDicts(toons, suits, id0, tr0, le0, tg0, hp0, ac0, hpb0, kbb0, died0, revive0, id1, tr1, le1, tg1, hp1, ac1, hpb1, kbb1, died1, revive1, id2, tr2, le2, tg2, hp2, ac2, hpb2, kbb2, died2, revive2, id3, tr3, le3, tg3, hp3, ac3, hpb3, kbb3, died3, revive3, sid0, at0, stg0, dm0, sd0, sb0, st0, sid1, at1, stg1, dm1, sd1, sb1, st1, sid2, at2, stg2, dm2, sd2, sb2, st2, sid3, at3, stg3, dm3, sd3, sb3, st3)

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
                    if self.activeToonIds.count(ta[TOON_TGT_COL]) != 0:
                        target = self.activeToonIds.index(ta[TOON_TGT_COL])
                    else:
                        target = -1
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
            if unAttack == 1 and self.fsm.getCurrentState().getName() == 'WaitForInput':
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
            if self.toonAttacks.has_key(t):
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
        self.movieHasPlayed = 0
        self.rewardHasPlayed = 0
        self.movieRequested = 0
        allSuitsDied = 0
        toonDied = 0
        for suit in self.activeSuits:
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
                 'activeToons': self.activeToons[:]}
                self.suitsKilled.append(encounter)
                self.removeSuit(suit)
        if len(self.activeSuits) == 0:
            allSuitsDied = 1
        for t in self.activeToons:
            if t.hp <= 0:
                self.activeToons.remove(t)
        if len(self.activeToons) == 0:
            toonDied = 1
        if toonDied:
            for suit in self.activeSuits:
                self.removeSuit(suit)
            doneStatus = 'defeat'
            messenger.send(self.townBattle.doneEvent, [doneStatus])
            return
        if not allSuitsDied:
            self.startCamTrack()
        else:
            self.setBattleExperience(*self.getBattleExperience())
            self.assignRewards()
            if self.tutorialFlag:
                self.movie.playTutorialReward(0, base.localAvatar.getName(), self.__battleDone)
            else:
                self.movie.playReward(0, base.localAvatar.getName(), self.__battleDone)
            for t in self.activeToons:
                self.activeToons.remove(t)
        return

    def removeSuit(self, suit):
        if suit in self.activeSuits:
            self.activeSuits.remove(suit)
        suit.disable()
        suit.delete()

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

    def localToonPendingOrActive(self):
        return 1

    def localToonActive(self):
        return 1

    def hasLocalToon(self):
        return 1

    def __battleDone(self):
        doneStatus = 'victory'
        messenger.send(self.townBattle.doneEvent, [doneStatus])
