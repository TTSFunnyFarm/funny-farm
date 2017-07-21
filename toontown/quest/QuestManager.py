from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import FunnyFarmGlobals
import Quests

class QuestManager:
    notify = directNotify.newCategory('QuestManager')

    def giveQuest(self, questId):
        base.localAvatar.addQuest(questId)

    def completeQuest(self, questId):
        levelUp = self.giveRewards(questId)
        base.localAvatar.removeQuest(questId)
        if not levelUp:
            base.localAvatar.setHealth(base.localAvatar.maxHp, base.localAvatar.maxHp, 1)

    def requestInteract(self, npc):
        toon = base.localAvatar
        for questDesc in toon.quests:
            questId, progress = questDesc
            quest = Quests.getQuest(questId)
            quest.setProgress(progress)
            complete = quest.getCompletionStatus() is Quests.COMPLETE
            if complete and quest.toNpc == npc.npcId:
                npc.completeQuest(toon.doId, questId)

    def giveRewards(self, questId, choice = None):
        toon = base.localAvatar
        quest = Quests.getQuest(questId)
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
            elif reward[0] == Quests.QuestRewardGagTraining:
                if choice == None:
                    self.notify.error('Cannot reward gag training, no choice given')
            elif reward[0] == Quests.QuestRewardJellybeans:
                jellybeans = reward[1]
            elif reward[0] == Quests.QuestRewardCheesyEffect:
                cheesyEffect = reward[1]
        if trackFrame > 0:
            toon.setTrackProgress(toon.trackProgressId, toon.trackProgress + 1)
        if choice != None:
            toon.setTrackProgress(choice, toon.trackProgress)
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
        levelUp = (toon.levelExp + expGained) >= toon.maxLevelExp and (toon.level + 1) <= FunnyFarmGlobals.ToonLevelCap
        if expGained > 0:
            if carryToonTasks:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryToonTasks, carryAmount=carryToonTasks)
            elif carryJellybeans:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryJellybeans, carryAmount=carryJellybeans)
            elif carryGags:
                toon.addLevelExp(expGained, trackFrame=trackFrame, carryIndex=Quests.QuestRewardCarryGags, carryAmount=carryGags)
            else:
                toon.addLevelExp(expGained, trackFrame=trackFrame)
        return levelUp
