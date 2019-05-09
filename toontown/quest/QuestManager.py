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
        # This is a special case for delivery quests; we want it to show the 
        # green complete task when they're heading back to whoever assigned it.
        if Quests.getQuestType(questId)[0] == Quests.QuestTypeDeliver and Quests.getFromNpcId(questId) == Quests.getToNpcId(questId):
            base.localAvatar.setQuestProgress(questId, 1)

    def completeQuest(self, npc, questId):
        base.localAvatar.removeQuest(questId)
        # If this was a significant quest, add it to their quest history.
        if questId in Quests.ImportantQuests:
            base.localAvatar.addQuestHistory(questId)
        levelUp = 0
        if Quests.getQuestFinished(questId) == Quests.Finish:
            # It's the last quest in the progression, give them their reward.
            levelUp = self.giveReward(questId)
            if not levelUp:
                base.localAvatar.setHealth(base.localAvatar.maxHp, base.localAvatar.maxHp)
        nextQuest = Quests.getNextQuest(questId)
        if nextQuest == Quests.NA:
            base.localAvatar.enable()
            return
        if Quests.getQuestFinished(questId) == Quests.Finish:
            base.localAvatar.enable()
            base.localAvatar.disable()
            base.localAvatar.setAnimState('neutral')
            taskMgr.doMethodLater(2.0, self.__handleCompleteQuest, 'completeQuest', [npc, nextQuest])
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

    def recoverItems(self, toon, suitsKilled, zoneId):
        recovered, notRecovered = ([] for i in xrange(2))
        for index, questDesc in enumerate(toon.quests):
            quest = Quests.getQuest(questDesc[0])
            quest.setQuestProgress(questDesc[1])
            if quest.getType() == Quests.QuestTypeRecover:
                isComplete = quest.getCompletionStatus()
                if isComplete == Quests.COMPLETE:
                    # This quest is complete, skip.
                    continue
                # It's a quest where we need to recover an item!
                if quest.isLocationMatch(zoneId):
                    # We're in the correct area to recover the item.
                    if quest.getHolder() == Quests.Any or quest.getHolderType() in ['type', 'track', 'level']:
                        for suit in suitsKilled:
                            if quest.getCompletionStatus() == Quests.COMPLETE:
                                # Test if the task has already been completed.
                                # If it has, we don't need to iterate through the cogs anymore.
                                break
                            # Now we'll make sure we killed the right type of cog.
                            if (quest.getHolder() == Quests.Any) \
                            or (quest.getHolderType() == 'type' and quest.getHolder() == suit['type']) \
                            or (quest.getHolderType() == 'track' and quest.getHolder() == suit['track']) \
                            or (quest.getHolderType() == 'level' and quest.getHolder() <= suit['level']):
                                progress = toon.quests[index][1] & pow(2, 16) - 1
                                completion = quest.testRecover(progress)
                                if completion[0]:
                                    # We win! We got the item from the cogs.
                                    recovered.append(quest.getItem())
                                    toon.setQuestProgress(quest.questId, progress + 1)
                                else:
                                    # Tough luck, maybe next time.
                                    notRecovered.append(quest.getItem())
        return (recovered, notRecovered)

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
                    if Quests.getQuestFinished(questId) == Quests.Finish:
                        # They only COMPLETE the quest when the actual quest progression is over.
                        npc.completeQuest(toon.doId, questId)
                    else:
                        # Otherwise, it'll silently complete the continuing quest and smoothly transition to the next one.
                        self.completeQuest(npc, questId)
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
        
        # If we made it here, that means the player has space for a new quest. Let's determine what we should give them.
        # First try to give them the main quest if they don't have it for some odd reason.
        if npc.getMainQuest():
            questId = npc.getMainQuest()
            hasQuest = False
            for questDesc in toon.quests:
                if questDesc[0] == questId:
                    hasQuest = True
            if not hasQuest:
                self.npcGiveQuest(npc, questId)
                return
        # Then check if we can give them a side quest.
        if npc.getSideQuest():
            questId = npc.getSideQuest()
            hasQuest = False
            for questDesc in toon.quests:
                if questDesc[0] == questId:
                    hasQuest = True
            if not hasQuest:
                # todo: maybe make this a quest choice instead of directly assigning it?
                self.npcGiveQuest(npc, questId)
                return
        
        # We don't have a storyline quest or a side quest to give them; 
        # Let's offer them a list of suitable quests for their current quest tier.
        tier = self.determineQuestTier(toon)
        bestQuests = Quests.chooseBestQuests(tier, npc, toon)
        
        # Present the quests to the player.
        npc.presentQuestChoice(toon.doId, bestQuests)

    def determineQuestTier(self, avatar):
        # Determines the current quest tier of the toon using their quest history.
        # Only important quests are added to the history, and we use those to determine if they're ready to start the next tier.
        
        # In this case, 1030 is the final task in tier 1, and they'll also have to have teleport access and carry 30 gags.
        # (I will finish this method as I write the quests.)
        if avatar.hasQuestHistory(1030) and avatar.hasQuestHistory(1046) and avatar.hasQuestHistory(1055): # just a temp number until I write the quest
            return Quests.FF_TIER + 1
        # else if avatar.hasQuestHistory(finalQuestId):
        #     return Quests.SS_TIER
        # etc.
        else:
            return Quests.FF_TIER

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
        teleportAccess = 0
        carryToonTasks = 0
        carryGags = 0
        carryJellybeans = 0
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
            elif reward[2] == Quests.QuestRewardTeleportAccess:
                teleportAccess = reward[3]
            elif reward[2] == Quests.QuestRewardCarryToonTasks:
                carryToonTasks = reward[3]
            elif reward[2] == Quests.QuestRewardCarryGags:
                carryGags = reward[3]
            elif reward[2] == Quests.QuestRewardCarryJellybeans:
                carryJellybeans = reward[3]
        else:
            if reward[0] == Quests.QuestRewardXP:
                expGained = reward[1]
            elif reward[0] == Quests.QuestRewardJellybeans:
                jellybeans = reward[1]
            elif reward[0] == Quests.QuestRewardCheesyEffect:
                cheesyEffect = reward[1]
        if trackFrame > 0:
            toon.setTrackProgress(toon.trackProgressId, trackFrame)
        if gagTrack != -1 and gagLevel != -1:
            trackArray = toon.getTrackAccess()
            trackArray[gagTrack] = 1
            toon.setTrackAccess(trackArray)
            toon.inventory.addItem(gagTrack, gagLevel)
        if teleportAccess:
            newAccess = toon.getTeleportAccess()
            newAccess.append(teleportAccess)
            toon.setTeleportAccess(newAccess)
        if carryToonTasks > 0:
            toon.setQuestCarryLimit(carryToonTasks)
        if carryGags > 0:
            toon.setMaxCarry(carrygags)
        if carryJellybeans > 0:
            toon.setMaxMoney(carryJellybeans)
        if jellybeans > 0:
            toon.addMoney(jellybeans)
        if cheesyEffect > 0:
            # todo figure out best way to set the timers on these
            toon.setCheesyEffect(cheesyEffect)
        levelUp = (toon.levelExp + expGained) >= toon.getMaxLevelExp() and (toon.level + 1) <= FunnyFarmGlobals.ToonLevelCap
        if expGained > 0:
            if carryToonTasks:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryToonTasks, carryAmount=carryToonTasks)
            elif carryGags:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryGags, carryAmount=carryGags)
            elif carryJellybeans:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryJellybeans, carryAmount=carryJellybeans)
            else:
                toon.addLevelExp(expGained, trackFrame=trackFrame)
        if not levelUp:
            base.playSfx(base.localAvatar.rewardSfx)
        return levelUp
