from panda3d.core import *
from direct.interval.IntervalGlobal import *
from otp.nametag.NametagConstants import *
from toontown.quest import Quests
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.battle.Battle import Battle
from toontown.battle.BattleBase import *
from toontown.battle import SuitBattleGlobals
import random

class BattleBldg(Battle):
    camFOFov = 30.0
    camFOPos = Point3(0, -10, 4)

    def __init__(self, bldgClass, townBattle, toons = [], suits = [], maxSuits = 2, bldg = 1, tutorialFlag = 0):
        Battle.__init__(self, townBattle, toons=toons, suits=suits, maxSuits=maxSuits, bldg=bldg, tutorialFlag=tutorialFlag)
        self.bldgClass = bldgClass

    def setBossBattle(self, value):
        self.bossBattle = value
        # if self.bossBattle:
        #     self.battleMusic = base.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.ogg')
        # else:
        #     self.battleMusic = base.loadMusic('phase_7/audio/bgm/encntr_general_bg_indoor.ogg')
        # base.playMusic(self.battleMusic, looping=1, volume=0.9)

    def getBossBattleTaunt(self):
        return TTLocalizer.BattleBldgBossTaunt

    def faceOff(self, name, callback):
        if len(self.suits) == 0:
            self.notify.warning('faceOff(): no suits.')
            return
        if len(self.toons) == 0:
            self.notify.warning('faceOff(): no toons.')
            return
        elevatorPos = self.toons[0].getPos()

        highestLvl = 0
        leaderIndex = 0
        for suit in self.suits:
            if suit.getActualLevel() > highestLvl:
                highestLvl = suit.getActualLevel()
                leaderIndex = self.suits.index(suit)

        delay = FACEOFF_TAUNT_T
        suitTrack = Parallel()
        suitLeader = None
        for suit in self.suits:
            suit.enterBattle()
            suitIsLeader = 0
            oneSuitTrack = Sequence()
            oneSuitTrack.append(Func(suit.loop, 'neutral'))
            oneSuitTrack.append(Func(suit.headsUp, elevatorPos))
            if self.suits.index(suit) == leaderIndex:
                suitLeader = suit
                suitIsLeader = 1
                if self.bossBattle == 1:
                    taunt = self.getBossBattleTaunt()
                else:
                    taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
                oneSuitTrack.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
            destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            oneSuitTrack.append(Wait(delay))
            if suitIsLeader == 1:
                oneSuitTrack.append(Func(suit.clearChat))
            oneSuitTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
            suitTrack.append(oneSuitTrack)

        toonTrack = Parallel()
        for toon in self.toons:
            oneToonTrack = Sequence()
            destPos, destHpr = self.getActorPosHpr(toon, self.toons)
            oneToonTrack.append(Wait(delay))
            oneToonTrack.append(self.createAdjustInterval(toon, destPos, destHpr, toon=1, run=1))
            toonTrack.append(oneToonTrack)

        camTrack = Sequence()

        def setCamFov(fov):
            base.camLens.setMinFov(fov/(4./3.))

        camTrack.append(Func(camera.wrtReparentTo, suitLeader))
        camTrack.append(Func(setCamFov, self.camFOFov))
        suitHeight = suitLeader.getHeight()
        suitOffsetPnt = Point3(0, 0, suitHeight)
        MidTauntCamHeight = suitHeight * 0.66
        MidTauntCamHeightLim = suitHeight - 1.8
        if MidTauntCamHeight < MidTauntCamHeightLim:
            MidTauntCamHeight = MidTauntCamHeightLim
        TauntCamY = 18
        TauntCamX = 0
        TauntCamHeight = random.choice((MidTauntCamHeight, 1, 11))
        camTrack.append(Func(camera.setPos, TauntCamX, TauntCamY, TauntCamHeight))
        camTrack.append(Func(camera.lookAt, suitLeader, suitOffsetPnt))
        camTrack.append(Wait(delay))
        camPos = Point3(0, -6, 4)
        camHpr = Vec3(0, 0, 0)
        camTrack.append(Func(camera.reparentTo, base.localAvatar))
        camTrack.append(Func(setCamFov, self.camFov))
        camTrack.append(Func(camera.setPosHpr, camPos, camHpr))
        mtrack = Parallel(suitTrack, toonTrack, camTrack)
        done = Func(callback)
        track = Sequence(mtrack, done, name=name)
        track.start()
        self.storeInterval(track, name)
        return

    def addSuit(self, suit):
        self.notify.debug('addSuit(%d)' % suit.doId)
        self.suits.append(suit)
        suit.battleTrap = NO_TRAP

    def isJoinable(self):
        return self.joinable

    def suitCanJoin(self):
        return self.joinable

    def __playReward(self, callback):
        toonTracks = Parallel()
        for toon in self.toons:
            toonTracks.append(Sequence(Func(toon.loop, 'victory'), Wait(FLOOR_REWARD_TIMEOUT), Func(toon.loop, 'neutral')))

        name = 'floorReward-%d' % self.doId
        track = Sequence(toonTracks, Func(callback), name=name)
        camera.setPos(0, 0, 1)
        camera.setHpr(180, 10, 0)
        self.storeInterval(track, name)
        track.start()

    def enterReward(self):
        self.notify.debug('enterReward()')
        self.__playReward(self.__handleFloorRewardDone)

    def __handleFloorRewardDone(self):
        self.exitReward()
        doneStatus = 'floorVictory'
        messenger.send(self.townBattle.doneEvent, [doneStatus])

    def exitReward(self):
        self.notify.debug('exitReward()')
        self.clearInterval('floorReward-%d' % self.doId)

    def movieDone(self):
        self.exitPlayMovie()
        self.movieHasBeenMade = 0
        self.movieHasPlayed = 1
        self.rewardHasPlayed = 0
        self.movieRequested = 0
        allSuitsDied = 0
        toonDied = 0
        suitsToRemove = []
        totalHp = 0
        totalMaxHp = 0
        for suit in self.suits:
            totalMaxHp += suit.maxHP
            if suit.currHP > 0:
                totalHp += suit.currHP
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
        if len(self.bldgClass.reserveSuits) > 0:
            if self.needAdjust:
                self.requestAdjust()
            self.bldgClass.handleRoundDone(totalHp, totalMaxHp, suitsToRemove)
        elif not allSuitsDied:
            if self.needAdjust:
                self.requestAdjust()
            self.startCamTrack()
        else:
            if self.bossBattle:
                # Final floor, assign the rewards
                for toonId in self.activeToonIds:
                    toon = self.getToon(toonId)
                    if toon:
                        self.toonItems[toonId] = base.cr.questManager.recoverItems(toon, self.suitsKilled, toon.getZoneId())
                        # See if they have a quest to defeat a cog building
                        for questDesc in toon.quests:
                            quest = Quests.getQuest(questDesc[0])
                            quest.setQuestProgress(questDesc[1])
                            if quest.getType() == Quests.QuestTypeDefeatBuilding:
                                if quest.doesBuildingCount(self.bldgClass.track, self.bldgClass.numFloors, self.bldgClass.zoneId):
                                    toon.setQuestProgress(questDesc[0], questDesc[1] + 1)
                self.setJoinable(0)
                self.setBattleExperience(*self.getBattleExperience())
                self.assignRewards()
                self.movie.playReward(0, base.localAvatar.getName(), self.battleDone)
            else:
                # Save the rewards for the next floor's battle
                self.bldgClass.suitsKilled = self.suitsKilled
                self.bldgClass.toonSkillPtsGained = self.battleCalc.toonSkillPtsGained
                self.bldgClass.toonExp = self.toonExp
                self.bldgClass.toonOrigQuests = self.toonOrigQuests
                self.bldgClass.toonItems = self.toonItems
                self.bldgClass.toonOrigMerits = self.toonOrigMerits
                self.bldgClass.toonMerits = self.toonMerits
                self.bldgClass.toonParts = self.toonParts
                self.bldgClass.helpfulToons = self.helpfulToons
                self.enterReward()
            for t in self.activeToons:
                t.setInBattle(0)
                self.activeToons.remove(t)
        return
