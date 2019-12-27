import codecs
import json
import os

from cryptography.fernet import Fernet
from panda3d.core import *

from toontown.toon import ToonDNA
from toontown.toon.LocalToon import LocalToon
from toontown.toon.ToonData import ToonData
from toontown.toonbase import FunnyFarmGlobals

BASE_DB_ID = 1000001
HOUSE_ID_OFFSET = 100


class DataManager:
    notify = directNotify.newCategory('DataManager')
    notify.setInfo(1)

    def __init__(self):
        self.fileExt = '.dat'
        self.fileDir = os.getcwd() + '/database/'
        self.__index2key = {}
        self.corrupted = 0
        self.toons = []
        self.houses = []
        for toonNum in xrange(FunnyFarmGlobals.MaxAvatars):
            self.toons.append(str(BASE_DB_ID + toonNum))
            self.houses.append(str(BASE_DB_ID + toonNum + HOUSE_ID_OFFSET))
        return

    def getToonFilename(self, index):
        filename = Filename(self.fileDir + self.toons[index - 1] + self.fileExt)
        if os.path.exists(filename.toOsSpecific()):
            return filename
        return None

    def checkToonFiles(self):
        for file in self.toons:
            filename = Filename(self.fileDir + file + self.fileExt)
            if os.path.exists(filename.toOsSpecific()):
                return True
        return False

    def createToonData(self, index, dna, name):
        return ToonData.getDefaultToonData(index, dna, name)

    def generateKey(self, size=256):
        return os.urandom(size)

    def saveToonData(self, data):
        if self.corrupted:
            return None

        index = data.index
        filename = Filename(self.fileDir + self.toons[index - 1] + self.fileExt)
        if not os.path.exists(filename.toOsSpecific()):
            filename.makeDir()

        toonDataToWrite = None
        valid, reason, toonDataObj = ToonData.verifyToonData(data, saveToonData=False)
        if not valid:
            self.handleDataError(reason)
            return

        try:
            jsonData = toonDataObj.makeJsonData()
        except Exception as e:
            self.handleDataError(e)
            return

        try:
            fileData = json.dumps(jsonData, indent=4).encode()
        except Exception as e:
            self.handleDataError(e)
            return

        try:
            key = self.__index2key.get(index)
            if not key:
                key = self.generateKey(32)
                key = codecs.encode(key, 'base64')
                self.__index2key[index] = key

            fernet = Fernet(key)
            encryptedData = fernet.encrypt(fileData)
            toonDataToWrite = key.decode() + encryptedData.decode()
        except Exception as e:
            self.handleDataError(e)
            return

        if toonDataToWrite:
            with open(filename.toOsSpecific(), 'w') as f:
                f.write(toonDataToWrite)
                f.close()

        return

    def loadToonData(self, index):
        if self.corrupted:
            return None

        filename = Filename(self.fileDir + self.toons[index - 1] + self.fileExt)
        toonData = None
        if os.path.exists(filename.toOsSpecific()):
            with open(filename.toOsSpecific(), 'r') as f:
                toonData = f.read()
                f.close()

        if toonData:
            try:
                fileData = toonData.encode()
                key, db = fileData[0:45], fileData[45:]
                localKey = self.__index2key.get(index)
                if localKey != key:
                    self.__index2key[index] = key

                fernet = Fernet(key)
                decryptedData = fernet.decrypt(db)
                jsonData = json.loads(decryptedData)
            except Exception as e:
                self.handleDataError(e)
                return None

            try:
                toonDataObj = ToonData.makeFromJsonData(jsonData)
            except Exception as e:
                self.handleDataError(e)
                return None

            return toonDataObj

        return None

    def deleteToonData(self, index):
        filename = Filename(self.fileDir + self.toons[index - 1] + self.fileExt)
        if os.path.exists(filename.toOsSpecific()):
            os.remove(filename.toOsSpecific())
        else:
            self.notify.warning('Tried to delete nonexistent toon data!')

    def handleDataError(self, err=None):
        self.notify.warning('The database has possibly been corrupted due to an error. Notifying user, error below.')
        if err:
            self.notify.warning(err)
        exception = isinstance(err, Exception)
        if exception:
            base.handleGameError(
                'Your database has possibly been corrupted. Please contact The Toontown\'s Funny Farm Team for assistance.\nError: %s' % err.__class__.__name__)
        else:
            base.handleGameError(
                'Your database has failed verification and possibly been corrupted. Please contact The Toontown\'s Funny Farm Team for assistance.')
        self.corrupted = 1

    def createLocalAvatar(self, data):
        self.notify.info('================')
        self.notify.info('Chose avatar id: %s' % self.toons[data.index - 1])
        self.notify.info('Chose avatar name: %s' % data.setName)
        self.notify.info('================')
        base.localAvatar = LocalToon()
        base.avatarData = data
        __builtins__['localAvatar'] = base.localAvatar
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
        base.localAvatar.setQuestingZone(data.setQuestingZone)
        for questDesc in data.setQuests:
            base.localAvatar.addQuest(questDesc[0])
            base.localAvatar.setQuestProgress(questDesc[0], questDesc[1])
        base.localAvatar.setQuestHistory(data.setQuestHistory)
        if type(data.setTrackProgress) != list:
            base.localAvatar.setTrackProgress(-1, -1)
        else:
            base.localAvatar.setTrackProgress(*data.setTrackProgress)
        base.localAvatar.setHoodsVisited(data.setHoodsVisited)
        base.localAvatar.setTeleportAccess(data.setTeleportAccess)
        base.localAvatar.setNametagFont(FunnyFarmGlobals.getVar(data.setNametagStyle))
        base.localAvatar.setCETimer(data.setCETimer)
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
