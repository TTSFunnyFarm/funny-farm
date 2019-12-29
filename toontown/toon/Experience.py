from panda3d.core import *
from toontown.toonbase.ToontownBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
from otp.otpbase import OTPGlobals

class Experience:
    notify = DirectNotifyGlobal.directNotify.newCategory('Experience')

    def __init__(self, expData = None, owner = None):
        self.owner = owner
        if expData == None:
            self.experience = []
            for track in range(0, len(Tracks)):
                self.experience.append(StartingLevel)

        else:
            self.experience = self.makeFromExperienceData(expData)
        return

    def __str__(self):
        return str(self.experience)

    def exportExperienceData(self):
        dataList = self.experience
        experienceData = []
        for track in range(0, len(Tracks)):
            experienceData.append(dataList[track])

        return experienceData

    def makeFromExperienceData(self, experienceData):
        dataList = []
        for track in range(0, len(Tracks)):
            dataList.append(experienceData[track])

        return dataList

    def saveExp(self):
        experienceData = self.exportExperienceData()
        if not (base.avatarData.setExperience and base.avatarData.setExperience == experienceData):
            base.avatarData.setExperience = experienceData
            dataMgr.saveToonData(base.avatarData)

    def addExp(self, track, amount = 1):
        if type(track) == type(''):
            track = Tracks.index(track)
        self.notify.debug('adding %d exp to track %d' % (amount, track))
        if self.owner.getGameAccess() == OTPGlobals.AccessFull:
            if self.experience[track] + amount <= MaxSkill:
                self.experience[track] += amount
            else:
                self.experience[track] = MaxSkill
        elif self.experience[track] + amount <= UnpaidMaxSkills[track]:
            self.experience[track] += amount
        elif self.experience[track] > UnpaidMaxSkills[track]:
            self.experience[track] += 0
        else:
            self.experience[track] = UnpaidMaxSkills[track]
        self.saveExp()

    def maxOutExp(self):
        for track in range(0, len(Tracks)):
            if track == HEAL_TRACK:
                self.experience[track] = MaxPowerUpSkill
            else:
                self.experience[track] = MaxSkill
        self.owner.inventory.updateGUI()
        self.saveExp()

    def maxOutExpMinusOne(self):
        for track in range(0, len(Tracks)):
            self.experience[track] = MaxSkill - 1
        self.owner.inventory.updateGUI()
        self.saveExp()

    def makeExpHigh(self):
        for track in range(0, len(Tracks)):
            self.experience[track] = Levels[track][len(Levels[track]) - 1] - 1
        self.owner.inventory.updateGUI()
        self.saveExp()

    def makeExpRegular(self):
        import random
        for track in range(0, len(Tracks)):
            rank = random.choice((0, int(random.random() * 1500.0), int(random.random() * 2000.0)))
            self.experience[track] = Levels[track][len(Levels[track]) - 1] - rank
        self.owner.inventory.updateGUI()
        self.saveExp()

    def zeroOutExp(self):
        for track in range(0, len(Tracks)):
            self.experience[track] = StartingLevel
        self.owner.inventory.updateGUI()
        self.saveExp()

    def setAllExp(self, num):
        for track in range(0, len(Tracks)):
            self.experience[track] = num
        self.owner.inventory.updateGUI()
        self.saveExp()

    def getExp(self, track):
        if type(track) == type(''):
            track = Tracks.index(track)
        return self.experience[track]

    def setExp(self, track, exp):
        if type(track) == type(''):
            track = Tracks.index(track)
        self.experience[track] = exp
        self.owner.inventory.updateGUI()
        self.saveExp()

    def getExpLevel(self, track):
        if type(track) == type(''):
            track = Tracks.index(track)
        level = 0
        for amount in Levels[track]:
            if self.experience[track] >= amount:
                level = Levels[track].index(amount)

        return level

    def getTotalExp(self):
        total = 0
        for level in self.experience:
            total += level

        return total

    def getNextExpValue(self, track, curSkill = None):
        if curSkill == None:
            curSkill = self.experience[track]
        retVal = Levels[track][len(Levels[track]) - 1]
        for amount in Levels[track]:
            if curSkill < amount:
                retVal = amount
                return retVal

        return retVal

    def getNewGagIndexList(self, track, extraSkill):
        retList = []
        curSkill = self.experience[track]
        nextExpValue = self.getNextExpValue(track, curSkill)
        finalGagFlag = 0
        while curSkill + extraSkill >= nextExpValue and curSkill < nextExpValue and not finalGagFlag:
            retList.append(Levels[track].index(nextExpValue))
            newNextExpValue = self.getNextExpValue(track, nextExpValue)
            if newNextExpValue == nextExpValue:
                finalGagFlag = 1
            else:
                nextExpValue = newNextExpValue

        return retList
