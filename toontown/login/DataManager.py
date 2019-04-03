from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toon import ToonDNA
from toontown.toon.LocalToon import LocalToon
from toontown.toon.ToonData import ToonData
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
import yaml
import shutil
import os

# NOTE: The encrypt() and decrypt() functions should only be called in THIS FILE to avoid confusion and repitition.

BASE_DB_ID = 1000001

class DataManager:
    notify = directNotify.newCategory('DataManager')
    notify.setInfo(1)

    def __init__(self):
        self.fileExt = '.yaml'
        self.oldDir = Filename.getUserAppdataDirectory() + '/FunnyFarm/db/'
        self.newDir = Filename.getUserAppdataDirectory() + '/FunnyFarm' + '/database/'
        self.corrupted = 0
        self.toons = []
        for toonNum in range(FunnyFarmGlobals.MaxAvatars):
            self.toons.append(str(BASE_DB_ID + toonNum))
        self.removeOldData()
        return

    def removeOldData(self):
        filename = Filename(self.oldDir)
        if os.path.exists(filename.toOsSpecific()):
            self.notify.warning('Deprecated data found. Removing...')
            shutil.rmtree(filename.toOsSpecific())

    def getToonFilename(self, index):
        filename = Filename(self.newDir + self.toons[index - 1] + self.fileExt)
        if os.path.exists(filename.toOsSpecific()):
            return filename
        return None

    def checkToonFiles(self):
        for file in self.toons:
            filename = Filename(self.newDir + file + self.fileExt)
            if os.path.exists(filename.toOsSpecific()):
                return True
        return False

    def createToonData(self, index, dna, name):
        return ToonData(index, dna, name, 20, 20, 0, 40, 0, 12000, 20, None, None, [0, 0, 0, 0, 1, 1, 0], 
                        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], 'Mickey', 0, 1000, 1, 0, 
                        [0, 0, 0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [], [], [], [], [], [], 
                        [], [], 1, 1000, [-1, -1], [], [], 0, [], [], 0)

    def saveToonData(self, data):
        if self.corrupted:
            return None
        index = data.index
        filename = Filename(self.newDir + self.toons[index - 1] + self.fileExt)
        if not os.path.exists(filename.toOsSpecific()):
            filename.makeDir()
        with open(filename.toOsSpecific(), 'w') as toonData:
            data.encrypt()
            yaml.dump(data, toonData, default_flow_style=False)
            try:
                data.decrypt()
            except:
                self.handleDataError()
        return

    def loadToonData(self, index):
        if self.corrupted:
            return None
        filename = Filename(self.newDir + self.toons[index - 1] + self.fileExt)
        if os.path.exists(filename.toOsSpecific()):
            with open(filename.toOsSpecific(), 'r') as toonData:
                data = yaml.load(toonData, Loader=yaml.FullLoader)
                try:
                    data.decrypt()
                except:
                    self.handleDataError()
                    return None
            return data
        return None

    def deleteToonData(self, index):
        filename = Filename(self.newDir + self.toons[index - 1] + self.fileExt)
        if os.path.exists(filename.toOsSpecific()):
            os.remove(filename.toOsSpecific())
        else:
            self.notify.warning('Tried to delete nonexistent toon data!')

    def handleDataError(self):
        self.notify.warning('The database has been corrupted. Notifying user.')
        base.handleGameError('Your database has been corrupted. Please contact The Toontown\'s Funny Farm Team for assistance.')
        self.corrupted = 1

    def createLocalAvatar(self, data):
        self.notify.info('================')
        self.notify.info('Chose avatar id: %s' % self.toons[data.index - 1])
        self.notify.info('Chose avatar name: %s' % data.setName)
        self.notify.info('================')
        base.localAvatar = LocalToon()
        base.avatarData = data
        __builtins__.localAvatar = base.localAvatar
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(*data.setDNA)
        base.localAvatar.setDNA(dna)
        base.localAvatar.setDoId(int(self.toons[data.index - 1]))
        base.localAvatar.setName(data.setName)
        base.localAvatar.setHealth(data.setHp, data.setMaxHp)
        base.localAvatar.setMoney(data.setMoney)
        base.localAvatar.setMaxMoney(data.setMaxMoney)
        base.localAvatar.setBankMoney(data.setBankMoney)
        base.localAvatar.setMaxBankMoney(data.setMaxBankMoney)
        base.localAvatar.setMaxCarry(data.setMaxCarry)
        base.localAvatar.setTrackAccess(data.setTrackAccess)
        base.localAvatar.setExperience(data.setExperience)
        base.localAvatar.setInventory(data.setInventory)
        base.localAvatar.setQuestCarryLimit(data.setQuestCarryLimit)
        for questDesc in data.setQuests:
            base.localAvatar.addQuest(questDesc[0])
            base.localAvatar.setQuestProgress(questDesc[0], questDesc[1])
        base.localAvatar.setQuestHistory(data.setQuestHistory)
        if type(data.setTrackProgress) != list:
            base.localAvatar.setTrackProgress(-1, -1)
        else:
            base.localAvatar.setTrackProgress(*data.setTrackProgress)
        base.localAvatar.setNametagFont(FunnyFarmGlobals.getVar(data.setNametagStyle))
        base.localAvatar.setCheesyEffect(data.setCheesyEffect)
        base.localAvatar.setHat(*data.setHat)
        base.localAvatar.setGlasses(*data.setGlasses)
        base.localAvatar.setBackpack(*data.setBackpack)
        base.localAvatar.setShoes(*data.setShoes)
        base.localAvatar.setLevel(data.setLevel)
        base.localAvatar.setLevelExp(data.setLevelExp)
        base.localAvatar.setDamage(data.setDamage)
        base.localAvatar.setDefense(data.setDefense)
        base.localAvatar.setAccuracy(data.setAccuracy)
        base.localAvatar.setTutorialAck(data.setTutorialAck)
