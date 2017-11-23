from direct.task.Task import Task
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import FunnyFarmGlobals
import Quests

class QuestManager:
    notify = directNotify.newCategory('QuestManager')

    def npcGiveQuest(self, npc, questId):
        toNpcId = Quests.getToNpcId(questId)
        npc.assignQuest(base.localAvatar.doId, questId, toNpcId)
        base.localAvatar.addQuest(questId)

    def completeQuest(self, npc, questId):
        base.localAvatar.removeQuest(questId)
        # If this was a significant quest, add it to their quest history.
        if questId in Quests.ImportantQuests:
            base.localAvatar.addQuestHistory(questId)
        levelUp = 0
        if Quests.getQuestFinished(questId):
            # It's the last quest in the progression, give them their reward.
            levelUp = self.giveReward(questId)
        if not levelUp:
            base.localAvatar.setHealth(base.localAvatar.maxHp, base.localAvatar.maxHp)
        nextQuest = Quests.getNextQuest(questId)
        if nextQuest == Quests.NA:
            base.localAvatar.enable()
            return
        if Quests.getQuestFinished(questId):
            base.localAvatar.enable()
            base.localAvatar.disable()
            base.localAvatar.setAnimState('neutral')
            taskMgr.doMethodLater(1.5, self.__handleCompleteQuest, 'completeQuest', [npc, nextQuest])
        else:
            self.__handleCompleteQuest(npc, nextQuest)

    def __handleCompleteQuest(self, npc, nextQuest):
        if nextQuest in Quests.Cutscenes:
            if nextQuest == 1004:
                # Loony Labs cutscene is a very special case; unfortunately we have to just hack this in for now.
                base.cr.cutsceneMgr.enterCutscene(1003)
            else:
                base.cr.cutsceneMgr.enterCutscene(nextQuest)
                base.localAvatar.addQuest(nextQuest)
        else:
            self.npcGiveQuest(npc, nextQuest)
        return Task.done

    def requestInteract(self, npc):
        toon = base.localAvatar
        # First check if they need to turn in any quests.
        for questDesc in toon.quests:
            questId, progress = questDesc
            quest = Quests.getQuest(questId)
            quest.setQuestProgress(progress)
            toNpcId = quest.toNpc
            completeStatus = quest.getCompletionStatus()

            if completeStatus != Quests.COMPLETE and quest.getType() not in [Quests.QuestTypeGoTo, Quests.QuestTypeChoose, Quests.QuestTypeDeliver]:
                # Quest isn't complete, skip to the next one.
                continue
            if toNpcId == npc.getNpcId() or toNpcId == Quests.Any or toNpcId == Quests.ToonHQ and npc.getHq():
                # They made it to the right NPC!
                if quest.getType() == Quests.QuestTypeChoose:
                    npc.presentTrackChoice(toon.doId, questId, quest.getChoices())
                else:
                    npc.completeQuest(toon.doId, questId)
                return
            else:
                # Wrong NPC, not much we can do here.
                continue

        # Ok they can't turn in any quests, let's see if we can offer them any new ones.
        if len(toon.quests) >= toon.getQuestCarryLimit():
            # Their quests are full, we should say something to them.
            for questDesc in toon.quests:
                questId, progress = questDesc
                quest = Quests.getQuest(questId)
                quest.setQuestProgress(progress)
                toNpcId = quest.toNpc
                completeStatus = quest.getCompletionStatus()
                if completeStatus == Quests.COMPLETE:
                    # If they still have a quest that's complete, we must be at the wrong NPC.
                    npc.incompleteQuest(toon.doId, questId, Quests.INCOMPLETE_WRONG_NPC, toNpcId)
                else:
                    if toNpcId == npc.getNpcId() or toNpcId == Quests.Any or toNpcId == Quests.ToonHQ and npc.getHq():
                        # They came to the right place, but they still gotta finish!
                        npc.incompleteQuest(toon.doId, questId, Quests.INCOMPLETE_PROGRESS, toNpcId)
                    else:
                        # Keep working on that task, _avName_!
                        npc.incompleteQuest(toon.doId, questId, Quests.INCOMPLETE, toNpcId)
                return # Yes, the NPC's response is only based on the player's first quest.

        # todo: quest tier upgrades
        # todo: present quest choices
        # for now, keep telling them to fuck off, we dont have any quests for them yet
        npc.rejectAvatar(toon.doId)

    def avatarChoseQuest(self, npc, questId):
        toon = base.localAvatar
        if not toon:
            return
        self.npcGiveQuest(npc, questId)

    def avatarChoseTrack(self, npc, questId, trackId):
        toon = base.localAvatar
        if not toon:
            return
        if trackId in [ToontownBattleGlobals.THROW_TRACK, ToontownBattleGlobals.SQUIRT_TRACK]:
            self.notify.warning("toonId %s attempted to select trackId %d, which is a default track!" % (toon.doId, trackId))
            return
        npc.completeQuest(toon.doId, questId)
        toon.setTrackProgress(trackId, 0)

    def giveReward(self, questId):
        toon = base.localAvatar
        reward = Quests.getReward(questId)
        expGained = 0
        trackFrame = 0
        gagTrack = -1
        gagLevel = -1
        carryToonTasks = 0
        carryJellybeans = 0
        carryGags = 0
        carryJellybeans = 0
        jellybeans = 0
        cheesyEffect = 0
        if len(reward) >= 4:
            if reward[0] == Quests.QuestRewardXP:
                expGained = reward[1]
            else:
                self.notify.error('First reward should always be XP')
            if reward[2] == Quests.QuestRewardTrackFrame:
                trackFrame = reward[3]
            elif reward[2] == Quests.QuestRewardNewGag:
                gagTrack, gagLevel = reward[3]
            elif reward[2] == Quests.QuestRewardCarryToonTasks:
                carryToonTasks = reward[3]
            elif reward[2] == Quests.QuestRewardCarryJellybeans:
                carryJellybeans = reward[3]
            elif reward[2] == Quests.QuestRewardCarryGags:
                carryGags = reward[3]
            elif reward[2] == Quests.QuestRewardJellybeans:
                carryJellybeans = reward[3]
        else:
            if reward[0] == Quests.QuestRewardXP:
                expGained = reward[1]
            elif reward[0] == Quests.QuestRewardJellybeans:
                jellybeans = reward[1]
            elif reward[0] == Quests.QuestRewardCheesyEffect:
                cheesyEffect = reward[1]
        if trackFrame > 0:
            toon.setTrackProgress(toon.trackProgressId, toon.trackProgress + 1)
        if gagTrack != -1 and gagLevel != -1:
            trackArray = toon.getTrackAccess()
            trackArray[gagTrack] = 1
            toon.setTrackAccess(trackArray)
            toon.inventory.addItem(gagTrack, gagLevel)
        if carryToonTasks > 0:
            toon.setQuestCarryLimit(carryToonTasks)
        if carryJellybeans > 0:
            toon.setMaxMoney(carryJellybeans)
        if carryGags > 0:
            toon.setMaxCarry(carrygags)
        if jellybeans > 0:
            toon.addMoney(jellybeans)
        if cheesyEffect > 0:
            toon.setCheesyEffect(cheesyEffect)
        levelUp = (toon.levelExp + expGained) >= toon.getMaxLevelExp() and (toon.level + 1) <= FunnyFarmGlobals.ToonLevelCap
        if expGained > 0:
            if carryToonTasks:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryToonTasks, carryAmount=carryToonTasks)
            elif carryJellybeans:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryJellybeans, carryAmount=carryJellybeans)
            elif carryGags:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryGags, carryAmount=carryGags)
            else:
                toon.addLevelExp(expGained, trackFrame=trackFrame)
        if not levelUp:
            base.playSfx(base.localAvatar.rewardSfx)
        return levelUp
