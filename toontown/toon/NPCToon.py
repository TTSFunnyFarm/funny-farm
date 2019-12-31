from panda3d.core import *
from direct.task.Task import Task
from toontown.toon.NPCToonBase import *
from toontown.quest import Quests
from toontown.quest.QuestChoiceGui import QuestChoiceGui
from toontown.quest.TrackChoiceGui import TrackChoiceGui
from toontown.toonbase import TTLocalizer
from toontown.hood import ZoneUtil
from otp.nametag.NametagConstants import *
ChoiceTimeout = 20

class NPCToon(NPCToonBase):

    def __init__(self, hq = 0):
        NPCToonBase.__init__(self)
        self.hq = hq
        self.curQuestMovie = None
        self.questChoiceGui = None
        self.trackChoiceGui = None
        self.pendingAvId = None
        self.pendingQuests = None
        self.pendingTracks = None
        self.pendingTrackQuest = None
        self.busy = 0
        self.canTalk = 1
        return

    def getHq(self):
        return self.hq

    def disable(self):
        self.cleanupMovie()
        NPCToonBase.disable(self)

    def cleanupMovie(self):
        self.clearChat()
        self.ignore('chooseQuest')
        if self.questChoiceGui:
            self.questChoiceGui.destroy()
            self.questChoiceGui = None
        self.ignore(self.uniqueName('doneChatPage'))
        if self.curQuestMovie:
            self.curQuestMovie.timeout(fFinish=1)
            self.curQuestMovie.cleanup()
            self.curQuestMovie = None
        if self.trackChoiceGui:
            self.trackChoiceGui.destroy()
            self.trackChoiceGui = None
        self.nametag3d.clearDepthTest()
        self.nametag3d.clearBin()
        return

    def avatarEnter(self):
        base.cr.questManager.requestInteract(self)

    def setAllowedToTalk(self, canTalk):
        self.canTalk = canTalk

    def allowedToTalk(self):
        return self.canTalk

    def handleCollisionSphereEnter(self, collEntry):
        if self.allowedToTalk():
            base.localAvatar.disable()
            base.localAvatar.setAnimState('neutral', 1)
            self.avatarEnter()
            self.nametag3d.setDepthTest(0)
            self.nametag3d.setBin('fixed', 0)
            self.lookAt(base.localAvatar) # Look at the avatar...
            self.setP(0) # But only change our heading
            self.setR(0)

    def finishMovie(self, av, mode, quests, elapsedTime):
        self.cleanupMovie()
        av.startLookAround()
        self.startLookAround()
        self.detectAvatars()
        if hasattr(self, 'origin'):
            self.setPosHpr(self.origin, 0, 0, 0, 0, 0, 0)
        self.freeAvatar()
        taskMgr.remove(self.uniqueName('clearMovie'))
        
        if mode == NPCToons.QUEST_MOVIE_TRACK_CHOICE_CANCEL:
            self.setMainQuest(1)
        if mode == NPCToons.QUEST_MOVIE_ASSIGN:
            questId, toNpcId = quests
            # For Flippy/Suit intro scene
            if questId == 1003:
                messenger.send('cutscene-done')
        if mode == NPCToons.QUEST_MOVIE_COMPLETE:
            questId, toNpcId = quests
            base.cr.questManager.completeQuest(self, questId)

    def setupCamera(self, mode):
        # if camera.getParent() == render:
        #     return
        camera.wrtReparentTo(render)
        if mode == NPCToons.QUEST_MOVIE_QUEST_CHOICE or mode == NPCToons.QUEST_MOVIE_TRACK_CHOICE:
            quat = Quat()
            quat.setHpr((155, -2, 0))
            camera.posQuatInterval(1, Point3(5, 9, self.getHeight() - 0.5), quat, other=self, blendType='easeOut').start()
        else:
            quat = Quat()
            quat.setHpr((-150, -2, 0))
            camera.posQuatInterval(1, Point3(-5, 9, self.getHeight() - 0.5), quat, other=self, blendType='easeOut').start()

    def setMovie(self, mode, npcId, avId, quests):
        isLocalToon = avId == base.localAvatar.doId
        if mode == NPCToons.QUEST_MOVIE_CLEAR:
            self.cleanupMovie()
            return
        if mode == NPCToons.QUEST_MOVIE_TIMEOUT:
            self.cleanupMovie()
            if isLocalToon:
                self.freeAvatar()
            self.setPageNumber(0, -1)
            self.clearChat()
            self.startLookAround()
            self.detectAvatars()
            return
        av = base.localAvatar
        if av is None:
            self.notify.warning('Avatar %d not found in doId' % avId)
            return
        if mode == NPCToons.QUEST_MOVIE_REJECT:
            rejectString = Quests.chooseQuestDialogReject()
            rejectString = Quests.fillInQuestNames(rejectString, avName=base.avatarData.setName)
            self.setChatAbsolute(rejectString, CFSpeech | CFTimeout)
            self.freeAvatar()
            return
        if mode == NPCToons.QUEST_MOVIE_TIER_NOT_DONE:
            rejectString = Quests.chooseQuestDialogTierNotDone()
            rejectString = Quests.fillInQuestNames(rejectString, avName=av.getName())
            self.setChatAbsolute(rejectString, CFSpeech | CFTimeout)
            self.freeAvatar()
            return
        self.setupAvatars(av)
        fullString = ''
        toNpcId = None
        if mode == NPCToons.QUEST_MOVIE_COMPLETE:
            self.clearQuestIcon()
            questId, toNpcId = quests
            if isLocalToon:
                self.setupCamera(mode)
            greetingString = Quests.chooseQuestDialog(questId, Quests.GREETING)
            if greetingString:
                fullString += greetingString + '\x07'
            fullString += Quests.chooseQuestDialog(questId, Quests.COMPLETE)
            leavingString = Quests.chooseQuestDialog(questId, Quests.LEAVING)
            if leavingString:
                fullString += '\x07' + leavingString
        elif mode == NPCToons.QUEST_MOVIE_QUEST_CHOICE_CANCEL:
            fullString = TTLocalizer.QuestMovieQuestChoiceCancel
        elif mode == NPCToons.QUEST_MOVIE_TRACK_CHOICE_CANCEL:
            fullString = TTLocalizer.QuestMovieTrackChoiceCancel
        elif mode == NPCToons.QUEST_MOVIE_INCOMPLETE:
            questId, completeStatus, toNpcId = quests
            if isLocalToon:
                self.setupCamera(mode)
            greetingString = Quests.chooseQuestDialog(questId, Quests.GREETING)
            if greetingString:
                fullString += greetingString + '\x07'
            fullString += Quests.chooseQuestDialog(questId, completeStatus)
            leavingString = Quests.chooseQuestDialog(questId, Quests.LEAVING)
            if leavingString:
                fullString += '\x07' + leavingString
        elif mode == NPCToons.QUEST_MOVIE_ASSIGN:
            self.clearQuestIcon()
            questId, toNpcId = quests
            if isLocalToon:
                self.setupCamera(mode)
            fullString += Quests.chooseQuestDialog(questId, Quests.QUEST)
            leavingString = Quests.chooseQuestDialog(questId, Quests.LEAVING)
            if leavingString:
                fullString += '\x07' + leavingString
        elif mode == NPCToons.QUEST_MOVIE_QUEST_CHOICE:
            if isLocalToon:
                self.setupCamera(mode)
            self.setChatAbsolute(TTLocalizer.QuestMovieQuestChoice, CFSpeech)
            if isLocalToon:
                self.acceptOnce('chooseQuest', self.sendChooseQuest)
                self.questChoiceGui = QuestChoiceGui()
                self.questChoiceGui.setQuests(quests, ChoiceTimeout)
            return
        elif mode == NPCToons.QUEST_MOVIE_TRACK_CHOICE:
            self.clearQuestIcon()
            if isLocalToon:
                self.setupCamera(mode)
            tracks = quests
            self.setChatAbsolute(TTLocalizer.QuestMovieTrackChoice, CFSpeech)
            if isLocalToon:
                self.acceptOnce('chooseTrack', self.sendChooseTrack)
                self.trackChoiceGui = TrackChoiceGui(tracks, ChoiceTimeout)
            return
        fullString = Quests.fillInQuestNames(fullString, avName=av.getName(), fromNpcId=npcId, toNpcId=toNpcId)
        self.acceptOnce(self.uniqueName('doneChatPage'), self.finishMovie, extraArgs=[av, mode, quests])
        self.clearChat()
        self.setLocalPageChat(fullString, 1)
        return

    def sendChooseQuest(self, questId):
        if self.questChoiceGui:
            self.questChoiceGui.destroy()
            self.questChoiceGui = None
        self.chooseQuest(questId)
        return

    def sendChooseTrack(self, trackId):
        if self.trackChoiceGui:
            self.trackChoiceGui.destroy()
            self.trackChoiceGui = None
        self.chooseTrack(trackId)
        return

    def chooseQuest(self, questId):
        avId = base.localAvatar.doId
        if questId == 0:
            self.pendingAvId = None
            self.pendingQuests = None
            self.cancelChoseQuest(avId)
            return
        for quest in self.pendingQuests:
            if questId == quest:
                self.pendingAvId = None
                self.pendingQuests = None
                base.cr.questManager.avatarChoseQuest(self, questId)
                return
        self.notify.warning('chooseQuest: avatar: %s chose a quest not offered: %s' % (avId, questId))
        self.pendingAvId = None
        self.pendingQuests = None
        return

    def chooseTrack(self, trackId):
        avId = base.localAvatar.doId
        if trackId == -1:
            self.pendingAvId = None
            self.pendingTracks = None
            self.pendingTrackQuest = None
            self.cancelChoseTrack(avId)
            return
        for track in self.pendingTracks:
            if trackId == track:
                base.cr.questManager.avatarChoseTrack(self, self.pendingTrackQuest, trackId)
                self.pendingAvId = None
                self.pendingTracks = None
                self.pendingTrackQuest = None
                return
        self.notify.warning('chooseTrack: avatar: %s chose a track not offered: %s' % (avId, trackId))
        self.pendingAvId = None
        self.pendingTracks = None
        self.pendingTrackQuest = None
        return

    def sendTimeoutMovie(self, task):
        self.pendingAvId = None
        self.pendingQuests = None
        self.pendingTracks = None
        self.pendingTrackQuest = None
        self.setMovie(NPCToons.QUEST_MOVIE_TIMEOUT,
         self.npcId,
         self.busy,
         [])
        self.sendClearMovie(None)
        self.busy = 0
        return Task.done

    def sendClearMovie(self, task):
        self.pendingAvId = None
        self.pendingQuests = None
        self.pendingTracks = None
        self.pendingTrackQuest = None
        self.busy = 0
        self.setMovie(NPCToons.QUEST_MOVIE_CLEAR,
         self.npcId,
         0,
         [])
        return Task.done

    def rejectAvatar(self, avId):
        self.busy = avId
        self.setMovie(NPCToons.QUEST_MOVIE_REJECT,
         self.npcId,
         avId,
         [])
        taskMgr.doMethodLater(5.5, self.sendClearMovie, self.uniqueName('clearMovie'))

    def rejectAvatarTierNotDone(self, avId):
        self.busy = avId
        self.setMovie(NPCToons.QUEST_MOVIE_TIER_NOT_DONE,
         self.npcId,
         avId,
         [])
        taskMgr.doMethodLater(5.5, self.sendClearMovie, self.uniqueName('clearMovie'))

    def completeQuest(self, avId, questId):
        self.busy = avId
        self.setMovie(NPCToons.QUEST_MOVIE_COMPLETE,
         self.npcId,
         avId,
         [questId, 0])
        taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def incompleteQuest(self, avId, questId, completeStatus, toNpcId):
        self.busy = avId
        self.setMovie(NPCToons.QUEST_MOVIE_INCOMPLETE,
         self.npcId,
         avId,
         [questId, completeStatus, toNpcId])
        taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def assignQuest(self, avId, questId, toNpcId):
        self.busy = avId
        # if self.questCallback:
        #     self.questCallback()
        self.setMovie(NPCToons.QUEST_MOVIE_ASSIGN,
         self.npcId,
         avId,
         [questId, toNpcId])
        # taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def presentQuestChoice(self, avId, quests):
        self.busy = avId
        self.pendingAvId = avId
        self.pendingQuests = quests
        # flatQuests = []
        # for quest in quests:
        #     flatQuests.extend(quest)

        self.setMovie(NPCToons.QUEST_MOVIE_QUEST_CHOICE,
         self.npcId,
         avId,
         quests)
        taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def presentTrackChoice(self, avId, questId, tracks):
        self.busy = avId
        self.pendingAvId = avId
        self.pendingTracks = tracks
        self.pendingTrackQuest = questId
        self.setMovie(NPCToons.QUEST_MOVIE_TRACK_CHOICE,
         self.npcId,
         avId,
         tracks)
        taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def cancelChoseQuest(self, avId):
        self.busy = avId
        self.setMovie(NPCToons.QUEST_MOVIE_QUEST_CHOICE_CANCEL,
         self.npcId,
         avId,
         [])
        taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def cancelChoseTrack(self, avId):
        self.busy = avId
        self.setMovie(NPCToons.QUEST_MOVIE_TRACK_CHOICE_CANCEL,
         self.npcId,
         avId,
         [])
        taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))
