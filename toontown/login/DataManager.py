from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toon import ToonDNA
from toontown.toon.LocalToon import LocalToon
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
import __builtin__
import yaml.dist as yaml
import shutil
import os

# NOTE: The encrypt() and decrypt() functions should only be called in THIS FILE to avoid confusion and repitition.

class DataManager:
    notify = directNotify.newCategory('DataManager')
    notify.setInfo(True)

    def __init__(self):
        self.fileExt = '.yaml'
        self.oldDir = Filename.getUserAppdataDirectory() + '/FunnyFarm/db/'
        self.newDir = Filename.getUserAppdataDirectory() + '/FunnyFarm' + '/database/'
        self.toons = [
            '1000001',
            '1000002',
            '1000003',
            '1000004',
            '1000005',
            '1000006'
        ]
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

    def saveToonData(self, data):
        index = data.index
        filename = Filename(self.newDir + self.toons[index - 1] + self.fileExt)
        if not os.path.exists(filename.toOsSpecific()):
            filename.makeDir()
        with open(filename.toOsSpecific(), 'w') as toonData:
            data.encrypt()
            yaml.dump(data, toonData, default_flow_style=False)
            data.decrypt()
        return

    def loadToonData(self, index):
        filename = Filename(self.newDir + self.toons[index - 1] + self.fileExt)
        if os.path.exists(filename.toOsSpecific()):
            with open(filename.toOsSpecific(), 'r') as toonData:
                data = yaml.load(toonData)
                data.decrypt()
            return data
        return None

    def deleteToonData(self, index):
        filename = Filename(self.newDir + self.toons[index - 1] + self.fileExt)
        if os.path.exists(filename.toOsSpecific()):
            os.remove(filename.toOsSpecific())

    def createLocalAvatar(self, data):
        self.notify.info('================')
        self.notify.info('Chose avatar id: %s' % self.getToonFilename(data.index).getBasenameWoExtension())
        self.notify.info('Chose avatar name: %s' % data.setName)
        self.notify.info('================')
        base.localAvatar = LocalToon()
        base.avatarData = data
        __builtin__.localAvatar = base.localAvatar
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(*data.setDNA)
        base.localAvatar.setDNA(dna)
        base.localAvatar.setName(data.setName)
        base.localAvatar.startBlink()
        base.localAvatar.setHealth(data.setHp, data.setMaxHp)
        base.localAvatar.setMoney(data.setMoney)
        base.localAvatar.setMaxMoney(data.setMaxMoney)
        base.localAvatar.setBankMoney(data.setBankMoney)
        base.localAvatar.setMaxBankMoney(data.setMaxBankMoney)
        base.localAvatar.setNametagFont(FunnyFarmGlobals.getVar(data.setNametagStyle))
        base.localAvatar.setCheesyEffect(data.setCheesyEffect)
        base.localAvatar.setHat(*data.setHat)
        base.localAvatar.setGlasses(*data.setGlasses)
        base.localAvatar.setBackpack(*data.setBackpack)
        base.localAvatar.setShoes(*data.setShoes)
