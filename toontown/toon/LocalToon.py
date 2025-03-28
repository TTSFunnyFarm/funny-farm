from panda3d.core import *
from libotp import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from direct.showbase import PythonUtil
from direct.showbase.PythonUtil import *
from direct.task import Task
from otp.ai.MagicWordGlobal import *
from otp.avatar import LocalAvatar
from otp.otpbase import OTPGlobals
from toontown.chat.ChatManager import ChatManager
from toontown.book import ShtikerBook
from toontown.book import OptionsPage
from toontown.book import MapPage
from toontown.book import ToonPage
from toontown.book import InventoryPage
from toontown.book import QuestPage
from toontown.book import TrackPage
from toontown.book import CogPage
from toontown.cutscenes import CutscenesGlobals
from toontown.cutscenes.BuyGagsScene import BuyGagsScene
from toontown.cutscenes.DualTasksScene import DualTasksScene
from toontown.cutscenes.InfoBubble import InfoBubble
from toontown.quest import Quests
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toon.LaffMeter import LaffMeter
from toontown.toon.PublicWalk import PublicWalk
from toontown.toon.ExperienceBar import ExperienceBar
from toontown.toon import InventoryNew
from toontown.toon import Experience
from toontown.toon import Toon
import random
import math
import time

class LocalToon(Toon.Toon, LocalAvatar.LocalAvatar):
    notify = directNotify.newCategory('LocalToon')
    piePowerSpeed = config.GetDouble('pie-power-speed', 0.2)
    piePowerExponent = config.GetDouble('pie-power-exponent', 0.75)
    HpTextGenerator = TextNode('HpTextGenerator')
    HpTextEnabled = 1

    LevelTextNode = TextNode('LevelText')
    HpTextNode = TextNode('HpText')
    ExpTextNode = TextNode('ExpText')
    TokenTextNode = TextNode('TokenText')

    def __init__(self):
        try:
            self.LocalToon_initialized
        except:
            self.LocalToon_initialized = 1
            Toon.Toon.__init__(self)
            LocalAvatar.LocalAvatar.__init__(self)
            self.chatMgr = ChatManager()
            self.soundRun = base.loader.loadSfx('phase_3.5/audio/sfx/AV_footstep_runloop.ogg')
            self.soundWalk = base.loader.loadSfx('phase_3.5/audio/sfx/AV_footstep_walkloop.ogg')
            self.soundWhisper = base.loader.loadSfx('phase_3.5/audio/sfx/GUI_whisper_3.ogg')
            self.soundPhoneRing = base.loader.loadSfx('phase_3.5/audio/sfx/telephone_ring.ogg')
            self.soundSystemMessage = base.loader.loadSfx('phase_3/audio/sfx/clock03.ogg')
            self.rewardSfx = base.loader.loadSfx('phase_3.5/audio/sfx/tt_s_gui_sbk_cdrSuccess.ogg')
            self.levelUpSfx = base.loader.loadSfx('phase_14/audio/sfx/lvl-up_jingle.ogg')
            self.tunnelX = 0.0
            self.estate = None
            self.__pieBubble = None
            self.allowPies = 0
            self.__pieButton = None
            self.__piePowerMeter = None
            self.__piePowerMeterSequence = None
            self.__pieButtonType = None
            self.__pieButtonCount = None
            self.tossPieStart = None
            self.__presentingPie = 0
            self.__pieSequence = 0
            self.enabled = 0
            self.zoneId = 0
            self.hasGM = False
            self.accessLevel = 0
            self.hp = 15
            self.maxHp = 15
            self.toonUpIncrement = 1
            self.laffMeter = None
            self.money = 0
            self.maxMoney = 0
            self.bankMoney = 0
            self.maxBankMoney = 0
            self.earnedExperience = None
            self.level = 1
            self.levelExp = 0
            self.damage = [0, 0, 0, 0, 0, 0]
            self.defense = [0, 0, 0, 0]
            self.accuracy = [0, 0, 0, 0, 0, 0]
            self.damageEffect = 0
            self.defenseEffect = 0
            self.accuracyEffect = 0
            self.maxNPCFriends = 16
            self.tossTrack = None
            self.pieTracks = {}
            self.splatTracks = {}
            self.lastTossedPie = 0
            self.tunnelTrack = None
            self.tunnelPivotPos = [-14, -6, 0]
            self.tunnelCenterOffset = 9.0
            self.tunnelCenterInfluence = 0.6
            self.pivotAngle = 90 + 45
            self.inventory = None
            self.hpText = None
            self.strText = None
            self.sillySurgeText = False
            self.interactivePropTrackBonus = -1
            self.cogTypes = [0,
             0,
             0,
             0]
            self.cogLevels = [0,
             0,
             0,
             0]
            self.cogParts = [0,
             0,
             0,
             0]
            self.cogMerits = [0,
             0,
             0,
             0]
            self.questCarryLimit = 0
            self.questingZone = 0
            self.quests = []
            self.questHistory = []
            self.experienceBar = None
            self.hoodsVisited = []
            self.teleportAccess = []
            self.CETimer = 0.0
            self.unlimitedGags = False
            self.cogStatus = []
            self.cogCounts = []
            self.eliteCounts = []
            self.skeleCounts = []
            self.addActive()

    def generate(self):
        self.walkDoneEvent = 'walkDone'
        self.walkStateData = PublicWalk(self.walkDoneEvent)
        self.walkStateData.load()

    def delete(self):
        try:
            self.LocalToon_deleted
        except:
            self.LocalToon_deleted = 1
            self.removeActive()
            self.ignoreAll()
            Toon.Toon.delete(self)
            LocalAvatar.LocalAvatar.delete(self)
            del self.walkDoneEvent
            self.walkStateData.unload()
            del self.walkStateData
            self.stopToonUp()
            self.endAllowPies()
            self.laffMeter.destroy()
            self.chatMgr.delete()
            if self.inventory:
                self.inventory.unload()
            self.book.unload()
            self.experienceBar.destroy()
            self.infoBubble.unload()
            del self.laffMeter
            del self.optionsPage
            del self.mapPage
            del self.toonPage
            del self.invPage
            del self.questPage
            del self.chatMgr
            del self.inventory
            del self.book
            del self.experienceBar
            del self.infoBubble

    def isLocal(self):
        return 1

    def setDoId(self, doId):
        self.doId = doId

    def getDoId(self):
        return self.doId

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, str(self.doId)))

    # These functions control the enabling and disabling of the avatar's controls.
    # It's the equivalent of enterWalk() and exitWalk() from the Place class in Toontown,
    # just moved to a higher level so it's easier to access and understand.
    def enable(self):
        if self.enabled == 1:
            return
        else:
            self.enabled = 1
            self.walkStateData.enter()
            self.invPage.acceptOnscreenHooks()
            self.questPage.acceptOnscreenHooks()
            self.walkStateData.fsm.request('walking')

    def disable(self):
        if self.enabled == 0:
            return
        else:
            self.enabled = 0
            self.walkStateData.exit()
            self.invPage.ignoreOnscreenHooks()
            self.invPage.hideInventoryOnscreen()
            self.questPage.ignoreOnscreenHooks()
            self.questPage.hideQuestsOnscreen()

    def setZoneId(self, zoneId):
        self.zoneId = zoneId
        # Check if we need to start the toonup task
        self.considerToonUp(zoneId)

    def getZoneId(self):
        return self.zoneId

    def setTutorialAck(self, tutorialAck):
        self.tutorialAck = tutorialAck
        if base.avatarData.setTutorialAck != tutorialAck:
            base.avatarData.setTutorialAck = tutorialAck
            dataMgr.saveToonData(base.avatarData)

    def considerToonUp(self, zoneId):
        safezones = FunnyFarmGlobals.HoodHierarchy.keys()
        if zoneId in safezones and not self.isToonedUp():
            if taskMgr.hasTaskNamed(self.uniqueName('safeZoneToonUp')):
                # Do nothing, we're already in a safezone
                return None
            self.startToonUp(ToontownGlobals.SafezoneToonupFrequency)
        else:
            # We're heading to an unsafe zone, stop the toonup task
            self.stopToonUp()

    def startChat(self):
        self.chatMgr.createGui()
        self.chatMgr.enableKeyboardShortcuts()
        self.accept(OTPGlobals.ThinkPosHotkey, self.sayLocation)

    def stopChat(self):
        self.ignore(OTPGlobals.ThinkPosHotkey)
        self.chatMgr.deleteGui()
        self.chatMgr.disableKeyboardShortcuts()

    def setChatAbsolute(self, chatString, chatFlags, dialogue = None, interrupt = 1):
        # Only makes the local avatar active when they say something,
        # so that their nametag isn't always showing in the margins
        self.addActive()
        Toon.Toon.setChatAbsolute(self, chatString, chatFlags, dialogue=dialogue, interrupt=interrupt)
        # Message is sent from NametagGroup
        self.accept('%s-clearChat' % self.nametag.getUniqueId(), self.chatTimeout)
        if chatFlags & CFThought:
            # Makes it so thought bubbles don't appear in the margins
            self.chatTimeout()

    def chatTimeout(self):
        self.ignore('%s-clearChat' % self.nametag.getUniqueId())
        self.removeActive()
        self.chatMgr.disableKeyboardShortcuts()

    def initInterface(self):
        self.book = ShtikerBook.ShtikerBook()
        self.book.load()
        self.book.hideButton()
        self.optionsPage = OptionsPage.OptionsPage()
        self.optionsPage.load()
        self.book.addPage(self.optionsPage, pageName=TTLocalizer.OptionsPageTitle)
        self.mapPage = MapPage.MapPage()
        self.mapPage.load()
        self.book.addPage(self.mapPage, pageName=TTLocalizer.MapPageTitle)
        self.toonPage = ToonPage.ToonPage()
        self.toonPage.load()
        self.book.addPage(self.toonPage, pageName=TTLocalizer.ToonPageTitle)
        self.invPage = InventoryPage.InventoryPage()
        self.invPage.load()
        self.book.addPage(self.invPage, pageName=TTLocalizer.InventoryPageTitle)
        self.invPage.acceptOnscreenHooks()
        self.questPage = QuestPage.QuestPage()
        self.questPage.load()
        self.book.addPage(self.questPage, pageName=TTLocalizer.QuestPageToonTasks)
        self.trackPage = TrackPage.TrackPage()
        self.trackPage.load()
        self.book.addPage(self.trackPage, pageName=TTLocalizer.TrackPageShortTitle)
        self.questPage.acceptOnscreenHooks()
        self.cogPage = CogPage.CogPage()
        self.book.addPage(self.cogPage, pageName=TTLocalizer.SuitPageTitle)
        self.laffMeter = LaffMeter(self.style, self.hp, self.maxHp)
        self.laffMeter.setAvatar(self)
        self.laffMeter.setScale(0.075)
        self.laffMeter.reparentTo(base.a2dBottomLeft)
        if self.style.getAnimal() == 'monkey':
            self.laffMeter.setPos(0.153, 0.0, 0.13)
        else:
            self.laffMeter.setPos(0.133, 0.0, 0.13)
        self.laffMeter.stop()
        self.experienceBar = ExperienceBar(self)
        self.experienceBar.reparentTo(base.a2dBottomCenter)
        self.experienceBar.hide()
        self.infoBubble = InfoBubble()
        self.infoBubble.load()
        self.infoBubble.hide()
        self.accept('time-insert', self.__beginTossPie)
        self.accept('time-insert-up', self.__endTossPie)
        self.accept('time-delete', self.__beginTossPie)
        self.accept('time-delete-up', self.__endTossPie)
        self.accept('pieHit', self.__pieHit)
        self.accept('interrupt-pie', self.interruptPie)
        # self.accept('InputState-jump', self.__toonMoved)
        # self.accept('InputState-forward', self.__toonMoved)
        # self.accept('InputState-reverse', self.__toonMoved)
        # self.accept('InputState-turnLeft', self.__toonMoved)
        # self.accept('InputState-turnRight', self.__toonMoved)
        # self.accept('InputState-slide', self.__toonMoved)

    def enableDebug(self):
        onScreenDebug.enabled = True

        def updateOnScreenDebug(task):
            onScreenDebug.add('Avatar Position', self.getPos())
            onScreenDebug.add('Avatar Angle', self.getHpr())
            return Task.cont

        taskMgr.add(updateOnScreenDebug, 'UpdateOSD')

    def setHealth(self, hp, maxHp, showText=0):
        oldHp = self.hp
        try:
            hp = int(hp)
        except ValueError:
            return
        self.hp = hp
        self.maxHp = maxHp
        if self.hp >= self.maxHp:
            self.hp = self.maxHp
            self.stopToonUp()
        if self.hp <= 0:
            self.stopToonUp()
        if self.hp - oldHp == 0:
            return
        if self.laffMeter:
            self.laffMeter.adjustFace(self.hp, self.maxHp)
        if showText:
            self.showHpText(self.hp - oldHp)
        if self.hp > 0 and self.animFSM.getCurrentState().getName() == 'Sad':
            self.setAnimState('Happy')
        self.setToonUpIncrement()

        avatarDataChanged = False
        if base.avatarData.setHp != self.hp:
            base.avatarData.setHp = self.hp
            if not avatarDataChanged:
                avatarDataChanged = True

        if base.avatarData.setMaxHp != self.maxHp:
            base.avatarData.setMaxHp = self.maxHp
            if not avatarDataChanged:
                avatarDataChanged = True

        if avatarDataChanged:
            dataMgr.saveToonData(base.avatarData)

    def setToonUpIncrement(self):
        # At 0 hp, there are roughly 20 toonup intervals in 5 minutes, so if we divide the maxHp by 20
        # and round to the nearest integer, we'll get an increment that will restore the player's health
        # from 0 to max in roughly 5 minutes.
        self.toonUpIncrement = int(round(self.maxHp / 20))

    def setName(self, name):
        self.nametag.setName(name)
        if base.avatarData.setName != name:
            base.avatarData.setName = name
            dataMgr.saveToonData(base.avatarData)

    def getName(self):
        return self.nametag.getName()

    def getMaxNPCFriends(self):
        return self.maxNPCFriends

    def setNametagFont(self, font):
        Toon.Toon.setNametagFont(self, font)
        nametagStyle = FunnyFarmGlobals.nametagDict[font]
        if base.avatarData.setNametagStyle != nametagStyle:
            base.avatarData.setNametagStyle = nametagStyle
            dataMgr.saveToonData(base.avatarData)

    def setHat(self, hatIdx, textureIdx, colorIdx, fromRTM = False):
        Toon.Toon.setHat(self, hatIdx, textureIdx, colorIdx, fromRTM = False)
        hat = [hatIdx, textureIdx, colorIdx]
        if base.avatarData.setHat != hat:
            base.avatarData.setHat = hat[:]
            dataMgr.saveToonData(base.avatarData)

    def setGlasses(self, glassesIdx, textureIdx, colorIdx, fromRTM = False):
        Toon.Toon.setGlasses(self, glassesIdx, textureIdx, colorIdx, fromRTM = False)
        glasses = [glassesIdx, textureIdx, colorIdx]
        if base.avatarData.setGlasses != glasses:
            base.avatarData.setGlasses = glasses[:]
            dataMgr.saveToonData(base.avatarData)

    def setBackpack(self, backpackIdx, textureIdx, colorIdx, fromRTM = False):
        Toon.Toon.setBackpack(self, backpackIdx, textureIdx, colorIdx, fromRTM = False)
        backpack = [backpackIdx, textureIdx, colorIdx]
        if base.avatarData.setBackpack != backpack:
            base.avatarData.setBackpack = backpack[:]
            dataMgr.saveToonData(base.avatarData)

    def setShoes(self, shoesIdx, textureIdx, colorIdx):
        Toon.Toon.setShoes(self, shoesIdx, textureIdx, colorIdx)
        shoes = [shoesIdx, textureIdx, colorIdx]
        if base.avatarData.setShoes != shoes:
            base.avatarData.setShoes = shoes[:]
            dataMgr.saveToonData(base.avatarData)

    def setCheesyEffect(self, effect):
        Toon.Toon.applyCheesyEffect(self, effect, lerpTime=0.5)
        if effect != ToontownGlobals.CENormal:
            # We need to set a timer so the toon isn't stuck like this forever.
            effectDict = FunnyFarmGlobals.CheesyEffectDict[self.getQuestingZone()]
            # Make sure the effect is available in our playground.
            if effect in effectDict.keys():
                unit, duration = effectDict[effect]
                # Did we JUST put on the effect, or was this one already active?
                if self.getCETimer() == 0.0:
                    # Brand new effect, set the startTime to... right now!
                    startTime = time.time()
                    self.setCETimer(startTime)
                else:
                    # There must be an active timer already.
                    startTime = self.getCETimer()
                # Start the timer, AI will take it from here.
                base.air.cheesyEffectMgr.startTimer(unit, duration, startTime)
                self.accept('cheesyEffectTimeout', self.cheesyEffectTimeout)

        if base.avatarData.setCheesyEffect != effect:
            base.avatarData.setCheesyEffect = effect
            dataMgr.saveToonData(base.avatarData)

    def cheesyEffectTimeout(self):
        self.ignore('cheesyEffectTimeout')
        self.setCheesyEffect(ToontownGlobals.CENormal)
        self.setCETimer(0.0)

    def setCETimer(self, startTime):
        self.CETimer = startTime
        if base.avatarData.setCETimer != startTime:
            base.avatarData.setCETimer = startTime
            dataMgr.saveToonData(base.avatarData)

    def getCETimer(self):
        return self.CETimer

    def setAccessLevel(self, level):
        self.accessLevel = level

    def getGameAccess(self):
        return OTPGlobals.AccessFull

    def getAutoRun(self):
        return 0

    def setGMIcon(self):
        if self.accessLevel not in [100, 200, 300]:
            self.notify.warning('LocalToon.setGMIcon(): Invalid access level.')
            return
        if self.hasGM:
            self.removeGMIcon()
        iconInfo = ['phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist', 'phase_3.5/models/gui/tt_m_gui_gm_toontroop_getConnected', 'phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist', 'phase_3.5/models/gui/tt_m_gui_gm_toontroop_whistle']
        levels = {100:1, 200:2, 300:3}
        self.gmIcon = loader.loadModel(iconInfo[levels[self.accessLevel]])
        self.gmIcon.reparentTo(NodePath(self.nametag.getNameIcon()))
        self.gmIcon.find('**/gmPartyHat').removeNode()
        self.gmIcon.setScale(3.25)
        self.gmIcon.setZ(-1.5)
        self.gmIcon.setY(0.0)
        self.gmIcon.setTransparency(1)
        self.gmIconInterval = LerpHprInterval(self.gmIcon, 3.0, Point3(0, 0, 0), Point3(-360, 0, 0))
        self.gmIconInterval.loop()
        self.hasGM = True

    def removeGMIcon(self):
        if not self.hasGM:
            self.notify.warning('LocalToon.removeGMIcon(): LocalToon has no GMIcon to remove.')
            return
        self.hasGM = False
        self.gmIconInterval.finish()
        del self.gmIconInterval
        self.gmIcon.removeNode()
        del self.gmIcon

    def setMoney(self, money):
        self.money = money
        messenger.send(self.uniqueName('moneyChange'), [money])
        if base.avatarData.setMoney != money:
            base.avatarData.setMoney = money
            dataMgr.saveToonData(base.avatarData)

    def getMoney(self):
        return self.money

    def setMaxMoney(self, maxMoney):
        self.maxMoney = maxMoney
        if base.avatarData.setMaxMoney != maxMoney:
            base.avatarData.setMaxMoney = maxMoney
            dataMgr.saveToonData(base.avatarData)

    def getMaxMoney(self):
        return self.maxMoney

    def setBankMoney(self, bankMoney):
        self.bankMoney = bankMoney
        if base.avatarData.setBankMoney != bankMoney:
            base.avatarData.setBankMoney = bankMoney
            dataMgr.saveToonData(base.avatarData)

    def getBankMoney(self):
        return self.bankMoney

    def setMaxBankMoney(self, maxBankMoney):
        self.maxBankMoney = maxBankMoney
        if base.avatarData.setMaxBankMoney != maxBankMoney:
            base.avatarData.setMaxBankMoney = maxBankMoney
            dataMgr.saveToonData(base.avatarData)

    def getMaxBankMoney(self):
        return self.maxBankMoney

    def addMoney(self, money):
        newMoney = self.money + money
        if newMoney > self.maxMoney:
            self.setMoney(self.maxMoney)
            leftover = newMoney - self.maxMoney
            self.setBankMoney(self.bankMoney + leftover)
        else:
            self.setMoney(newMoney)

    def setTrackAccess(self, trackArray):
        self.trackArray = trackArray[:]
        if self.inventory:
            self.inventory.updateGUI()

        if base.avatarData.setTrackAccess != trackArray:
            base.avatarData.setTrackAccess = trackArray[:]
            dataMgr.saveToonData(base.avatarData)

    def getTrackAccess(self):
        return self.trackArray

    def hasTrackAccess(self, track):
        return self.trackArray[track]

    def checkGagBonus(self, track, level):
        return False

    def setMaxCarry(self, maxCarry):
        self.maxCarry = maxCarry
        if self.inventory:
            self.inventory.updateGUI()

        if base.avatarData.setMaxCarry != maxCarry:
            base.avatarData.setMaxCarry = maxCarry
            dataMgr.saveToonData(base.avatarData)

    def getMaxCarry(self):
        return self.maxCarry

    def getPinkSlips(self):
        return 0

    def setInventory(self, inventoryData):
        if not self.inventory:
            if type(inventoryData) != list:
                self.inventory = InventoryNew.InventoryNew(self, inventoryData)
            else:
                self.inventory = InventoryNew.InventoryNew(self, inventoryData[:])
        else:
            if type(inventoryData) != list:
                self.inventory.updateInvData(inventoryData)
            else:
                self.inventory.updateInvData(inventoryData[:])
        self.inventory.updateGUI()
        self.inventory.saveInventory()

    def setExperience(self, experience):
        if type(experience) != list:
            self.experience = Experience.Experience(experience, self)
        else:
            self.experience = Experience.Experience(experience[:], self)
        if self.inventory:
            self.inventory.updateGUI()
        self.experience.saveExp()

    def setQuestCarryLimit(self, limit):
        self.questCarryLimit = limit
        if base.avatarData.setQuestCarryLimit != limit:
            base.avatarData.setQuestCarryLimit = limit
            dataMgr.saveToonData(base.avatarData)

    def getQuestCarryLimit(self):
        return self.questCarryLimit

    def setQuestingZone(self, zone):
        self.questingZone = zone
        if base.avatarData.setQuestingZone != zone:
            base.avatarData.setQuestingZone = zone
            dataMgr.saveToonData(base.avatarData)

    def getQuestingZone(self):
        return self.questingZone

    def addQuest(self, questId):
        if len(self.quests) >= self.questCarryLimit:
            self.notify.warning('Cannot add quest %d; maximum quests reached' % questId)
            return
        self.quests.append([questId, 0])
        messenger.send('questsChanged')
        if base.avatarData.setQuests != self.quests:
            base.avatarData.setQuests = self.quests[:]
            dataMgr.saveToonData(base.avatarData)

    def setQuestProgress(self, questId, progress):
        for questDesc in self.quests:
            if questId == questDesc[0]:
                questDesc[1] = progress
                break
        messenger.send('questsChanged')
        if base.avatarData.setQuests != self.quests:
            base.avatarData.setQuests = self.quests[:]
            dataMgr.saveToonData(base.avatarData)

    def removeQuest(self, questId):
        for questDesc in self.quests[:]:
            if questId == questDesc[0]:
                self.quests.remove(questDesc)
                break
        messenger.send('questsChanged')
        if base.avatarData.setQuests != self.quests:
            base.avatarData.setQuests = self.quests[:]
            dataMgr.saveToonData(base.avatarData)

    def setQuestHistory(self, history):
        self.questHistory = history[:]

    def getQuestHistory(self):
        return self.questHistory

    def addQuestHistory(self, quest):
        if quest in self.questHistory:
            return
        self.questHistory.append(quest)
        if base.avatarData.setQuestHistory != self.questHistory:
            base.avatarData.setQuestHistory = self.questHistory[:]
            dataMgr.saveToonData(base.avatarData)

    def removeQuestHistory(self, quest):
        if quest not in self.questHistory:
            return
        self.questHistory.remove(quest)
        if base.avatarData.setQuestHistory != self.questHistory:
            base.avatarData.setQuestHistory = self.questHistory[:]
            dataMgr.saveToonData(base.avatarData)

    def hasQuestHistory(self, quest):
        if quest in self.questHistory:
            return True
        return False

    def clearQuestHistory(self):
        for quest in self.questHistory[:]:
            self.questHistory.remove(quest)
        if base.avatarData.setQuestHistory != self.questHistory:
            base.avatarData.setQuestHistory = self.questHistory[:]
            dataMgr.saveToonData(base.avatarData)

    def setTrackProgress(self, trackId, progress):
        self.trackProgressId = trackId
        self.trackProgress = progress
        if hasattr(self, 'trackPage'):
            self.trackPage.updatePage()

        trackProgress = self.getTrackProgress()[:]
        if base.avatarData.setTrackProgress != trackProgress:
            base.avatarData.setTrackProgress = trackProgress[:]
            dataMgr.saveToonData(base.avatarData)

    def getTrackProgress(self):
        return [self.trackProgressId, self.trackProgress]

    def setHoodsVisited(self, hoodsVisited):
        self.hoodsVisited = hoodsVisited[:]
        if base.avatarData.setHoodsVisited != hoodsVisited:
            base.avatarData.setHoodsVisited = hoodsVisited[:]
            dataMgr.saveToonData(base.avatarData)

    def getHoodsVisited(self):
        return self.hoodsVisited

    def setTeleportAccess(self, teleportAccess):
        self.teleportAccess = teleportAccess[:]
        if base.avatarData.setTeleportAccess != teleportAccess:
            base.avatarData.setTeleportAccess = teleportAccess[:]
            dataMgr.saveToonData(base.avatarData)

    def getTeleportAccess(self):
        return self.teleportAccess

    def setLevel(self, level):
        self.level = level
        if base.avatarData.setLevel != level:
            base.avatarData.setLevel = level
            dataMgr.saveToonData(base.avatarData)

    def getLevel(self):
        return self.level

    def setLevelExp(self, levelExp):
        self.levelExp = levelExp
        if self.experienceBar:
            self.experienceBar.setExperience(self.levelExp, self.getMaxLevelExp())

        if base.avatarData.setLevelExp != levelExp:
            base.avatarData.setLevelExp = levelExp
            dataMgr.saveToonData(base.avatarData)

    def getLevelExp(self):
        return self.levelExp

    def getMaxLevelExp(self):
        return FunnyFarmGlobals.LevelExperience[self.level - 1]

    def setCogStatus(self, cogStatus):
        self.cogStatus = cogStatus[:]
        if base.avatarData.setCogStatus != cogStatus:
            base.avatarData.setCogStatus = cogStatus[:]
            dataMgr.saveToonData(base.avatarData)

    def getCogStatus(self):
        return self.cogStatus

    def setCogCounts(self, cogCounts):
        self.cogCounts = cogCounts[:]
        if base.avatarData.setCogCounts != cogCounts:
            base.avatarData.setCogCounts = cogCounts[:]
            dataMgr.saveToonData(base.avatarData)

    def getCogCounts(self):
        return self.cogCounts

    def setEliteCounts(self, eliteCounts):
        self.eliteCounts = eliteCounts[:]
        if base.avatarData.setEliteCounts != eliteCounts:
            base.avatarData.setEliteCounts = eliteCounts[:]
            dataMgr.saveToonData(base.avatarData)

    def getEliteCounts(self):
        return self.eliteCounts

    def setSkeleCounts(self, skeleCounts):
        self.skeleCounts = skeleCounts[:]
        if base.avatarData.setSkeleCounts != skeleCounts:
            base.avatarData.setSkeleCounts = skeleCounts[:]
            dataMgr.saveToonData(base.avatarData)

    def getSkeleCounts(self):
        return self.skeleCounts

    def getTotalCogCount(self, suitIndex):
        count = 0
        count += self.getCogCounts()[suitIndex]
        count += self.getSkeleCounts()[suitIndex]
        count += self.getEliteCounts()[suitIndex]
        return count

    def getTotalCogsCount(self):
        count = sum(self.getCogCounts())
        count += sum(self.getSkeleCounts())
        count += sum(self.getEliteCounts())
        return count

    def addLevelExp(self, exp, trackFrame = 0, carryIndex = 0, carryAmount = 0):
        totalExp = self.levelExp + exp
        if totalExp >= self.getMaxLevelExp():
            leftover = totalExp - self.getMaxLevelExp()
            if self.levelUp(exp):
                self.setLevelExp(leftover)
            else:
                self.setLevelExp(self.getMaxLevelExp())
                self.showHpString('%d XP' % exp, duration=1.0, color=Vec4(1.0, 0.5, 1.0, 1.0), trackFrame=trackFrame, carryIndex=carryIndex, carryAmount=carryAmount)
        else:
            self.setLevelExp(totalExp)
            self.showHpString('%d XP' % exp, duration=1.0, color=Vec4(1.0, 0.5, 1.0, 1.0), trackFrame=trackFrame, carryIndex=carryIndex, carryAmount=carryAmount)

    def levelUp(self, exp):
        if (self.level + 1) > FunnyFarmGlobals.ToonLevelCap:
            return False
        self.setLevel(self.level + 1)
        if self.level == 10 or self.level > 30:
            hpGain = 4
        else:
            hpGain = 2
        self.setHealth(self.maxHp + hpGain, self.maxHp + hpGain)
        if self.level > 5 and (self.level % 2) == 0:
            self.showLevelUpText(hpGain, exp, token=1)
        else:
            self.showLevelUpText(hpGain, exp)
        musicMgr.pauseMusic()
        base.playSfx(self.levelUpSfx, volume=0.5)
        Sequence(Wait(self.levelUpSfx.length()), Func(musicMgr.unpauseMusic)).start()
        return True

    def showLevelUpText(self, hp, exp, token = 0):
        for node in (self.LevelTextNode, self.HpTextNode, self.ExpTextNode, self.TokenTextNode):
            node.setFont(OTPGlobals.getSignFont())
            node.clearShadow()
            node.setAlign(TextNode.ACenter)
        self.LevelTextNode.setText('Level Up!')
        self.LevelTextNode.setTextColor(0.5, 0.8, 1.0, 1.0)
        self.HpTextNode.setText('+%d' % hp)
        self.HpTextNode.setTextColor(0, 1.0, 0, 1.0)
        self.ExpTextNode.setText('%d XP' % exp)
        self.ExpTextNode.setTextColor(1.0, 0.5, 1.0, 1.0)
        if token:
            self.TokenTextNode.setText('+1 Token')
            self.TokenTextNode.setTextColor(1.0, 1.0, 0, 1.0)
        else:
            self.TokenTextNode.setText('')
        levelText = self.attachNewNode(self.LevelTextNode.generate())
        hpText = self.attachNewNode(self.HpTextNode.generate())
        expText = self.attachNewNode(self.ExpTextNode.generate())
        tokenText = self.attachNewNode(self.TokenTextNode.generate())
        textOffset = -0.7

        def cleanupText():
            levelText.removeNode()
            hpText.removeNode()
            expText.removeNode()
            tokenText.removeNode()

        if token:
            for text in (expText, tokenText, hpText, levelText):
                textOffset += 0.7
                text.setScale(0.7)
                text.setBillboardAxis()
                text.setPos(0, 0, (self.height / 2) + textOffset)
            seq = Sequence(
                Parallel(
                    levelText.posInterval(1.5, Point3(0, 0, self.height + 3.4), blendType='easeOut'),
                    hpText.posInterval(1.5, Point3(0, 0, self.height + 2.7), blendType='easeOut'),
                    tokenText.posInterval(1.5, Point3(0, 0, self.height + 2.0), blendType='easeOut'),
                    expText.posInterval(1.5, Point3(0, 0, self.height + 1.3), blendType='easeOut')
                ),
                Wait(2.0),
                Parallel(
                    levelText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0)),
                    hpText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0)),
                    tokenText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0)),
                    expText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0))
                ),
                Func(cleanupText)
            )
        else:
            for text in (expText, hpText, levelText):
                textOffset += 0.7
                text.setScale(0.7)
                text.setBillboardAxis()
                text.setPos(0, 0, (self.height / 2) + textOffset)
            seq = Sequence(
                Parallel(
                    levelText.posInterval(1.5, Point3(0, 0, self.height + 2.7), blendType='easeOut'),
                    hpText.posInterval(1.5, Point3(0, 0, self.height + 2.0), blendType='easeOut'),
                    expText.posInterval(1.5, Point3(0, 0, self.height + 1.3), blendType='easeOut')
                ),
                Wait(2.0),
                Parallel(
                    levelText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0)),
                    hpText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0)),
                    expText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0))
                ),
                Func(cleanupText)
            )
        seq.start()

    def setDamage(self, damageArray):
        self.damage = damageArray[:]
        if base.avatarData.setDamage != damageArray:
            base.avatarData.setDamage = damageArray[:]
            dataMgr.saveToonData(base.avatarData)

    def getDamage(self):
        return self.damage

    def setDefense(self, defenseArray):
        self.defense = defenseArray[:]
        if base.avatarData.setDefense != defenseArray:
            base.avatarData.setDefense = defenseArray[:]
            dataMgr.saveToonData(base.avatarData)

    def getDefense(self):
        return self.defense

    def setAccuracy(self, accuracyArray):
        self.accuracy = accuracyArray[:]
        if base.avatarData.setAccuracy != accuracyArray:
            base.avatarData.setAccuracy = accuracyArray[:]
            dataMgr.saveToonData(base.avatarData)

    def getAccuracy(self):
        return self.accuracy

    def setDamageEffect(self, effect):
        self.damageEffect = effect
        for val in self.damage:
            val += self.damageEffect

    def removeDamageEffect(self):
        for val in self.damage:
            val -= self.damageEffect
        self.damageEffect = 0

    def setDefenseEffect(self, effect):
        self.defenseEffect = effect
        for val in self.defense:
            val += self.defenseEffect

    def removeDefenseEffect(self):
        for val in self.defense:
            val -= self.defenseEffect
        self.defenseEffect = 0

    def setAccuracyEffect(self, effect):
        self.accuracyEffect = effect
        for val in self.accuracy:
            val += self.accuracyEffect

    def removeAccuracyEffect(self):
        for val in self.accuracy:
            val -= self.accuracyEffect
        self.accuracyEffect = 0

    def setEarnedExperience(self, earnedExp):
        self.earnedExperience = earnedExp

    def maxToon(self):
        self.setHealth(120, 120, showText=1)
        self.setTrackAccess([1, 1, 1, 1, 1, 1, 1])
        self.setMaxCarry(80)
        self.experience.maxOutExp()
        self.inventory.maxOutInv()
        self.inventory.updateGUI()
        self.setDamage([100, 0, 100, 100, 100, 100])
        self.setDefense([100, 100, 100, 100])
        self.setAccuracy([0, 100, 100, 100, 100, 100])
        self.setMaxMoney(250)
        self.setMoney(250)
        self.setBankMoney(12000)
        self.setLevel(40)
        self.setLevelExp(21000)
        self.setCogStatus([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3])

    def resetToon(self):
        self.setHealth(20, 20, showText=1)
        self.setTrackAccess([0, 0, 0, 0, 1, 1, 0])
        self.setMaxCarry(20)
        self.experience.zeroOutExp()
        self.inventory.zeroInv(killUber=1)
        self.inventory.addItem(4, 0)
        self.inventory.addItem(5, 0)
        self.inventory.updateGUI()
        self.setDamage([0, 0, 0, 0, 0, 0])
        self.setDefense([0, 0, 0, 0])
        self.setAccuracy([0, 0, 0, 0, 0, 0])
        self.setMaxMoney(40)
        self.setMoney(0)
        self.setBankMoney(0)
        self.setLevel(1)
        self.setLevelExp(0)
        self.setTrackProgress(-1, -1)
        self.setCogStatus([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.setCogCounts([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.setEliteCounts([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.setSkeleCounts([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.clearQuestHistory()

    def setRandomSpawn(self, zoneId):
        if zoneId not in FunnyFarmGlobals.SpawnPoints.keys():
            self.setPos(0, 0, 0)
            self.setHpr(0, 0, 0)
            return
        spawnPoints = FunnyFarmGlobals.SpawnPoints[zoneId]
        spawn = random.choice(spawnPoints)
        self.setPos(spawn[0])
        self.setHpr(spawn[1])

    def checkQuestCutscene(self):
        currZone = base.cr.playGame.getActiveZone()
        if currZone.place:
            zoneId = currZone.place.zoneId
        else:
            zoneId = currZone.zoneId
        for questDesc in self.quests:
            if questDesc[0] in CutscenesGlobals.Cutscenes and not self.hasQuestHistory(questDesc[0]):
                if zoneId == Quests.getToNpcLocation(questDesc[0]) and questDesc[1] == 0:
                    base.cr.cutsceneMgr.enterCutscene(questDesc[0])
                    return True
            # Special cases
            # "Ride the trolley" info bubble
            id = BuyGagsScene.id
            if questDesc[0] == id and not self.hasQuestHistory(1):
                if zoneId == FunnyFarmGlobals.FunnyFarm:
                    base.cr.cutsceneMgr.enterCutscene(id)
                    return True
            # Carry 2 ToonTasks info bubble
            id = DualTasksScene.id
            if questDesc[0] == id and not self.hasQuestHistory(4):
                if zoneId == FunnyFarmGlobals.FunnyFarm:
                    base.cr.cutsceneMgr.enterCutscene(id)
                    return True
            # Not a cutscene, but this is the easiest way to do this.
            if questDesc[0] in [1028, 1029]:
                if zoneId == FunnyFarmGlobals.RicketyRoad:
                    for bldg in currZone.buildings:
                        if bldg.mode != 'toon':
                            if questDesc[0] == 1028:
                                bldg.elevator.removeActive()
                            else:
                                bldg.elevator.addActive()
        return False

    def showInfoBubble(self, index, doneEvent, npcId=0):
        self.infoBubble.enter(index, doneEvent, npcId)

    def b_setTunnelIn(self, endX, tunnelOrigin):
        timestamp = globalClockDelta.getFrameNetworkTime()
        pos = tunnelOrigin.getPos(render)
        h = tunnelOrigin.getH(render)
        self.setTunnelIn(timestamp, endX, pos[0], pos[1], pos[2], h)

    def setTunnelIn(self, timestamp, endX, x, y, z, h):
        t = globalClockDelta.networkToLocalTime(timestamp)
        self.handleTunnelIn(t, endX, x, y, z, h)

    def b_setTunnelOut(self, startX, startY, tunnelOrigin):
        timestamp = globalClockDelta.getFrameNetworkTime()
        pos = tunnelOrigin.getPos(render)
        h = tunnelOrigin.getH(render)
        self.setTunnelOut(timestamp, startX, startY, pos[0], pos[1], pos[2], h)

    def setTunnelOut(self, timestamp, startX, startY, x, y, z, h):
        t = globalClockDelta.networkToLocalTime(timestamp)
        self.handleTunnelOut(t, startX, startY, x, y, z, h)

    def tunnelIn(self, tunnelOrigin):
        self.b_setTunnelIn(self.tunnelX * 0.8, tunnelOrigin)

    def tunnelOut(self, tunnelOrigin):
        self.disable()
        self.setZ(ToontownGlobals.FloorOffset)
        self.tunnelX = self.getX(tunnelOrigin)
        tunnelY = self.getY(tunnelOrigin)
        self.b_setTunnelOut(self.tunnelX * 0.95, tunnelY, tunnelOrigin)

    def getTunnelInToonTrack(self, endX, tunnelOrigin):
        pivotNode = tunnelOrigin.attachNewNode(self.uniqueName('pivotNode'))
        pivotNode.setPos(*self.tunnelPivotPos)
        pivotNode.setHpr(0, 0, 0)
        pivotY = pivotNode.getY(tunnelOrigin)
        endY = 5.0
        straightLerpDur = abs(endY - pivotY) / ToontownGlobals.ToonForwardSpeed
        pivotDur = 2.0
        pivotLerpDur = pivotDur * (90.0 / self.pivotAngle)
        self.reparentTo(pivotNode)
        self.setPos(0, 0, 0)
        self.setX(tunnelOrigin, endX)
        targetX = self.getX()
        self.setX(self.tunnelCenterOffset + (targetX - self.tunnelCenterOffset) * (1.0 - self.tunnelCenterInfluence))
        self.setHpr(tunnelOrigin, 0, 0, 0)
        pivotNode.setH(-self.pivotAngle)
        return Sequence(Wait(0.8), Parallel(LerpHprInterval(pivotNode, pivotDur, hpr=Point3(0, 0, 0), name=self.uniqueName('tunnelInPivot')), Sequence(Wait(pivotDur - pivotLerpDur), LerpPosInterval(self, pivotLerpDur, pos=Point3(targetX, 0, 0), name=self.uniqueName('tunnelInPivotLerpPos')))), Func(self.wrtReparentTo, render), Func(pivotNode.removeNode), LerpPosInterval(self, straightLerpDur, pos=Point3(endX, endY, 0.1), other=tunnelOrigin, name=self.uniqueName('tunnelInStraightLerp')))

    def getTunnelOutToonTrack(self, startX, startY, tunnelOrigin):
        startPos = self.getPos(tunnelOrigin)
        startHpr = self.getHpr(tunnelOrigin)
        reducedAvH = PythonUtil.fitDestAngle2Src(startHpr[0], 180)
        pivotNode = tunnelOrigin.attachNewNode(self.uniqueName('pivotNode'))
        pivotNode.setPos(*self.tunnelPivotPos)
        pivotNode.setHpr(0, 0, 0)
        pivotY = pivotNode.getY(tunnelOrigin)
        straightLerpDur = abs(startY - pivotY) / ToontownGlobals.ToonForwardSpeed
        pivotDur = 2.0
        pivotLerpDur = pivotDur * (90.0 / self.pivotAngle)

        def getTargetPos(self = self):
            pos = self.getPos()
            return Point3(self.tunnelCenterOffset + (pos[0] - self.tunnelCenterOffset) * (1.0 - self.tunnelCenterInfluence), pos[1], pos[2])

        return Sequence(Parallel(LerpPosInterval(self, straightLerpDur, pos=Point3(startX, pivotY, 0.1), startPos=startPos, other=tunnelOrigin, name=self.uniqueName('tunnelOutStraightLerp')), LerpHprInterval(self, straightLerpDur * 0.8, hpr=Point3(reducedAvH, 0, 0), startHpr=startHpr, other=tunnelOrigin, name=self.uniqueName('tunnelOutStraightLerpHpr'))), Func(self.wrtReparentTo, pivotNode), Parallel(LerpHprInterval(pivotNode, pivotDur, hpr=Point3(-self.pivotAngle, 0, 0), name=self.uniqueName('tunnelOutPivot')), LerpPosInterval(self, pivotLerpDur, pos=getTargetPos, name=self.uniqueName('tunnelOutPivotLerpPos'))), Func(self.wrtReparentTo, render), Func(pivotNode.removeNode))

    def handleTunnelIn(self, startTime, endX, x, y, z, h):
        self.notify.debug('LocalToon.handleTunnelIn')
        tunnelOrigin = render.attachNewNode('tunnelOrigin')
        tunnelOrigin.setPosHpr(x, y, z, h, 0, 0)
        self.setAnimState('run')
        self.stopLookAround()
        self.reparentTo(render)
        self.runSound()
        camera.reparentTo(render)
        camera.setPosHpr(tunnelOrigin, 0, 20, 12, 180, -20, 0)
        base.transitions.irisIn(0.4)
        toonTrack = self.getTunnelInToonTrack(endX, tunnelOrigin)

        def cleanup(self = self, tunnelOrigin = tunnelOrigin):
            self.stopSound()
            self.enable()
            tunnelOrigin.removeNode()
            messenger.send('tunnelInMovieDone')

        self.tunnelTrack = Sequence(toonTrack, Func(cleanup))
        self.tunnelTrack.start(globalClock.getFrameTime() - startTime)

    def handleTunnelOut(self, startTime, startX, startY, x, y, z, h):
        self.notify.debug('LocalToon.handleTunnelOut')
        tunnelOrigin = render.attachNewNode('tunnelOrigin')
        tunnelOrigin.setPosHpr(x, y, z, h, 0, 0)
        self.setAnimState('run')
        self.runSound()
        self.stopLookAround()
        tracks = Parallel()
        camera.wrtReparentTo(render)
        startPos = camera.getPos(tunnelOrigin)
        startHpr = camera.getHpr(tunnelOrigin)
        camLerpDur = 1.0
        reducedCamH = fitDestAngle2Src(startHpr[0], 180)
        tracks.append(LerpPosHprInterval(camera, camLerpDur, pos=Point3(0, 20, 12), hpr=Point3(reducedCamH, -20, 0), startPos=startPos, startHpr=startHpr, other=tunnelOrigin, blendType='easeInOut', name='tunnelOutLerpCamPos'))
        toonTrack = self.getTunnelOutToonTrack(startX, startY, tunnelOrigin)
        tracks.append(toonTrack)
        irisDur = 0.4
        tracks.append(Sequence(Wait(toonTrack.getDuration() - (irisDur + 0.1)), Func(base.transitions.irisOut, irisDur)))

        def cleanup(self = self, tunnelOrigin = tunnelOrigin):
            self.stopSound()
            self.detachNode()
            tunnelOrigin.removeNode()
            messenger.send('tunnelOutMovieDone')

        self.tunnelTrack = Sequence(tracks, Func(cleanup))
        self.tunnelTrack.start(globalClock.getFrameTime() - startTime)

    def setAnimState(self, animName, animMultiplier = 1.0, timestamp = None, animType = None, callback = None, extraArgs = []):
        if not animName or animName == 'None':
            return
        if timestamp == None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)
        if base.config.GetBool('check-invalid-anims', True):
            if animMultiplier > 1.0 and animName in ['neutral']:
                animMultiplier = 1.0
        if self.animFSM.getStateNamed(animName):
            self.animFSM.request(animName, [animMultiplier,
             ts,
             callback,
             extraArgs])
        self.cleanupPieInHand()
        return

    def givePies(self, type, numPies):
        self.beginAllowPies()
        self.setPieType(type)
        self.setNumPies(numPies)

    def presentPie(self, x, y, z, h, timestamp32):
        if self.numPies <= 0:
            return
        lastTossTrack = Sequence()
        if self.tossTrack:
            lastTossTrack = self.tossTrack
            tossTrack = None
        ts = globalClockDelta.localElapsedTime(timestamp32, bits=32)
        ival = self.getPresentPieInterval(x, y, z, h)
        if ts > 0:
            startTime = ts
            lastTossTrack.finish()
        else:
            ival = Sequence(Wait(-ts), ival)
            lastTossTrack.finish()
            startTime = 0
        ival = Sequence(ival)
        ival.start(startTime)
        self.tossTrack = ival
        return

    def tossPie(self, x, y, z, h, sequence, power, throwType, timestamp32):
        if self.numPies <= 0:
            return
        if self.numPies != ToontownGlobals.FullPies:
            self.setNumPies(self.numPies - 1)
        self.lastTossedPie = globalClock.getFrameTime()
        lastTossTrack = Sequence()
        if self.tossTrack:
            lastTossTrack = self.tossTrack
            tossTrack = None
        lastPieTrack = Sequence()
        if sequence in self.pieTracks:
            lastPieTrack = self.pieTracks[sequence]
            del self.pieTracks[sequence]
        ts = globalClockDelta.localElapsedTime(timestamp32, bits=32)
        toss, pie, flyPie = self.getTossPieInterval(x, y, z, h, power, throwType)
        if ts > 0:
            startTime = ts
            lastTossTrack.finish()
            lastPieTrack.finish()
        else:
            toss = Sequence(Wait(-ts), toss)
            pie = Sequence(Wait(-ts), pie)
            lastTossTrack.finish()
            lastPieTrack.finish()
            startTime = 0
        self.tossTrack = toss
        toss.start(startTime)
        pie = Sequence(pie, Func(self.pieFinishedFlying, sequence))
        self.pieTracks[sequence] = pie
        pie.start(startTime)
        return

    def pieFinishedSplatting(self, sequence):
        if sequence in self.splatTracks:
            del self.splatTracks[sequence]

    def pieSplat(self, x, y, z, sequence, pieCode, timestamp32):
        if self.isLocal():
            return
        elapsed = globalClock.getFrameTime() - self.lastTossedPie
        if elapsed > 30:
            return
        lastPieTrack = Sequence()
        if sequence in self.pieTracks:
            lastPieTrack = self.pieTracks[sequence]
            del self.pieTracks[sequence]
        if sequence in self.splatTracks:
            lastSplatTrack = self.splatTracks[sequence]
            del self.splatTracks[sequence]
            lastSplatTrack.finish()
        ts = globalClockDelta.localElapsedTime(timestamp32, bits=32)
        splat = self.getPieSplatInterval(x, y, z, pieCode)
        splat = Sequence(Func(messenger.send, 'pieSplat', [self, pieCode]), splat)
        if ts > 0:
            startTime = ts
            lastPieTrack.finish()
        else:
            splat = Sequence(Wait(-ts), splat)
            startTime = 0
        splat = Sequence(splat, Func(self.pieFinishedSplatting, sequence))
        self.splatTracks[sequence] = splat
        splat.start(startTime)

    def cleanupPies(self):
        for track in self.pieTracks.values():
            track.finish()

        self.pieTracks = {}
        for track in self.splatTracks.values():
            track.finish()

        self.splatTracks = {}
        self.cleanupPieInHand()

    def cleanupPieInHand(self):
        if self.tossTrack:
            self.tossTrack.finish()
            self.tossTrack = None
        self.cleanupPieModel()
        return

    def setNumPies(self, numPies):
        self.numPies = numPies
        if self.isLocal():
            self.updatePieButton()
            if numPies == 0:
                self.interruptPie()

    def setPieType(self, pieType):
        self.pieType = pieType
        if self.isLocal():
            self.updatePieButton()

    def getPieBubble(self):
        if self.__pieBubble == None:
            bubble = CollisionSphere(0, 0, 0, 1)
            node = CollisionNode('pieBubble')
            node.addSolid(bubble)
            node.setFromCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.CameraBitmask | ToontownGlobals.FloorBitmask)
            node.setIntoCollideMask(BitMask32.allOff())
            self.__pieBubble = NodePath(node)
            self.pieHandler = CollisionHandlerEvent()
            self.pieHandler.addInPattern('pieHit')
            self.pieHandler.addInPattern('pieHit-%in')
        return self.__pieBubble

    def __beginTossPieMouse(self, mouseParam):
        self.__beginTossPie(globalClock.getFrameTime())

    def __endTossPieMouse(self, mouseParam):
        self.__endTossPie(globalClock.getFrameTime())

    def __beginTossPie(self, time):
        if self.tossPieStart != None:
            return
        if not self.allowPies:
            return
        if self.hp < 1:
            return
        if self.numPies == 0:
            messenger.send('outOfPies')
            return
        if self.__pieInHand():
            return
        if getattr(self.controlManager.currentControls, 'isAirborne', 0):
            return
        messenger.send('wakeup')
        self.localPresentPie(time)
        taskName = self.uniqueName('updatePiePower')
        taskMgr.add(self.__updatePiePower, taskName)
        return

    def __endTossPie(self, time):
        if self.tossPieStart == None:
            return
        taskName = self.uniqueName('updatePiePower')
        taskMgr.remove(taskName)
        messenger.send('wakeup')
        power = self.__getPiePower(time)
        self.tossPieStart = None
        self.localTossPie(power)
        return

    def localPresentPie(self, time):
        from toontown.toon import TTEmote
        from otp.avatar import Emote
        self.__stopPresentPie()
        if self.tossTrack:
            tossTrack = self.tossTrack
            self.tossTrack = None
            tossTrack.finish()
        self.interruptPie()
        self.tossPieStart = time
        self.__pieSequence = self.__pieSequence + 1 & 255
        sequence = self.__pieSequence
        self.__presentingPie = 1
        pos = self.getPos()
        hpr = self.getHpr()
        timestamp32 = globalClockDelta.getFrameNetworkTime(bits=32)
        Emote.globalEmote.disableBody(self)
        self.walkStateData.fsm.request('off')
        messenger.send('begin-pie')
        ival = self.getPresentPieInterval(pos[0], pos[1], pos[2], hpr[0])
        ival = Sequence(ival, name=self.uniqueName('localPresentPie'))
        self.tossTrack = ival
        ival.start()
        self.makePiePowerMeter()
        self.__piePowerMeter.show()
        self.__piePowerMeterSequence = sequence
        self.__piePowerMeter['value'] = 0
        return

    def __stopPresentPie(self):
        if self.__presentingPie:
            from toontown.toon import TTEmote
            from otp.avatar import Emote
            Emote.globalEmote.releaseBody(self)
            messenger.send('end-pie')
            self.__presentingPie = 0
        taskName = self.uniqueName('updatePiePower')
        taskMgr.remove(taskName)

    def __getPiePower(self, time):
        elapsed = max(time - self.tossPieStart, 0.0)
        t = elapsed / self.piePowerSpeed
        t = math.pow(t, self.piePowerExponent)
        power = int(t * 100) % 200
        if power > 100:
            power = 200 - power
        return power

    def __updatePiePower(self, task):
        if not self.__piePowerMeter:
            return Task.done
        self.__piePowerMeter['value'] = self.__getPiePower(globalClock.getFrameTime())
        return Task.cont

    def interruptPie(self):
        self.cleanupPieInHand()
        self.__stopPresentPie()
        if self.__piePowerMeter:
            self.__piePowerMeter.hide()
        pie = self.pieTracks.get(self.__pieSequence)
        if pie and pie.getT() < 14.0 / 24.0:
            del self.pieTracks[self.__pieSequence]
            pie.pause()

    def __pieInHand(self):
        pie = self.pieTracks.get(self.__pieSequence)
        return pie and pie.getT() < 15.0 / 24.0

    def __toonMoved(self, isSet):
        if isSet:
            self.interruptPie()

    def localTossPie(self, power):
        if not self.__presentingPie:
            return
        pos = self.getPos()
        hpr = self.getHpr()
        timestamp32 = globalClockDelta.getFrameNetworkTime(bits=32)
        sequence = self.__pieSequence
        if self.tossTrack:
            tossTrack = self.tossTrack
            self.tossTrack = None
            tossTrack.finish()
        if sequence in self.pieTracks:
            pieTrack = self.pieTracks[sequence]
            del self.pieTracks[sequence]
            pieTrack.finish()
        if sequence in self.splatTracks:
            splatTrack = self.splatTracks[sequence]
            del self.splatTracks[sequence]
            splatTrack.finish()
        self.makePiePowerMeter()
        self.__piePowerMeter['value'] = power
        self.__piePowerMeter.show()
        self.__piePowerMeterSequence = sequence
        pieBubble = self.getPieBubble().instanceTo(NodePath())

        def pieFlies(self = self, pos = pos, hpr = hpr, sequence = sequence, power = power, timestamp32 = timestamp32, pieBubble = pieBubble):
            if self.numPies != ToontownGlobals.FullPies:
                self.setNumPies(self.numPies - 1)
            base.cTrav.addCollider(pieBubble, self.pieHandler)

        toss, pie, flyPie = self.getTossPieInterval(pos[0], pos[1], pos[2], hpr[0], power, self.pieThrowType, beginFlyIval=Func(pieFlies))
        pieBubble.reparentTo(flyPie)
        flyPie.setTag('pieSequence', str(sequence))
        toss = Sequence(toss)
        self.tossTrack = toss
        toss.start()
        pie = Sequence(pie, Func(base.cTrav.removeCollider, pieBubble), Func(self.pieFinishedFlying, sequence))
        self.pieTracks[sequence] = pie
        pie.start()
        return

    def pieFinishedFlying(self, sequence):
        if sequence in self.pieTracks:
            del self.pieTracks[sequence]
        if self.__piePowerMeterSequence == sequence:
            self.__piePowerMeter.hide()
        self.walkStateData.fsm.request('walking')

    def __finishPieTrack(self, sequence):
        if sequence in self.pieTracks:
            pieTrack = self.pieTracks[sequence]
            del self.pieTracks[sequence]
            pieTrack.finish()

    def __pieHit(self, entry):
        if not entry.hasSurfacePoint() or not entry.hasInto():
            return
        if not entry.getInto().isTangible():
            return
        sequence = int(entry.getFromNodePath().getNetTag('pieSequence'))
        self.__finishPieTrack(sequence)
        if sequence in self.splatTracks:
            splatTrack = self.splatTracks[sequence]
            del self.splatTracks[sequence]
            splatTrack.finish()
        pieCode = 0
        pieCodeStr = entry.getIntoNodePath().getNetTag('pieCode')
        if pieCodeStr:
            pieCode = int(pieCodeStr)
        pos = entry.getSurfacePoint(render)
        timestamp32 = globalClockDelta.getFrameNetworkTime(bits=32)
        splat = self.getPieSplatInterval(pos[0], pos[1], pos[2], pieCode)
        splat = Sequence(splat, Func(self.pieFinishedSplatting, sequence))
        self.splatTracks[sequence] = splat
        splat.start()
        messenger.send('pieSplat', [pieCode])
        messenger.send('localPieSplat', [pieCode, entry])

    def beginAllowPies(self):
        self.allowPies = 1
        self.updatePieButton()

    def endAllowPies(self):
        self.allowPies = 0
        self.updatePieButton()

    def makePiePowerMeter(self):
        from direct.gui.DirectGui import DirectWaitBar, DGG
        if self.__piePowerMeter == None:
            self.__piePowerMeter = DirectWaitBar(frameSize=(-0.2,
             0.2,
             -0.03,
             0.03), relief=DGG.SUNKEN, borderWidth=(0.005, 0.005), barColor=(0.4, 0.6, 1.0, 1), pos=(0, 0.1, 0.8))
            self.__piePowerMeter.hide()
        return

    def updatePieButton(self):
        from toontown.toonbase import ToontownBattleGlobals
        from direct.gui.DirectGui import DirectButton, DGG
        wantButton = 0
        if self.allowPies and self.numPies > 0:
            wantButton = 1
        haveButton = self.__pieButton != None
        if not haveButton and not wantButton:
            return
        if haveButton and not wantButton:
            self.__pieButton.destroy()
            self.__pieButton = None
            self.__pieButtonType = None
            self.__pieButtonCount = None
            return
        if self.__pieButtonType != self.pieType:
            if self.__pieButton:
                self.__pieButton.destroy()
                self.__pieButton = None
        if self.__pieButton == None:
            inv = self.inventory
            if self.pieType >= len(inv.invModels[ToontownBattleGlobals.THROW_TRACK]):
                gui = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
                pieGui = gui.find('**/summons')
                pieScale = 0.1
            else:
                gui = None
                pieGui = (inv.invModels[ToontownBattleGlobals.THROW_TRACK][self.pieType],)
                pieScale = 0.85
            self.__pieButton = DirectButton(image=(inv.upButton, inv.downButton, inv.rolloverButton), geom=pieGui, text='50', text_scale=0.04, text_align=TextNode.ARight, geom_scale=pieScale, geom_pos=(-0.01, 0, 0), text_fg=Vec4(1, 1, 1, 1), text_pos=(0.07, -0.04), relief=None, image_color=(0, 0.6, 1, 1), pos=(0, 0.1, 0.9))
            self.__pieButton.bind(DGG.B1PRESS, self.__beginTossPieMouse)
            self.__pieButton.bind(DGG.B1RELEASE, self.__endTossPieMouse)
            self.__pieButtonType = self.pieType
            self.__pieButtonCount = None
            if gui:
                del gui
        if self.__pieButtonCount != self.numPies:
            if self.numPies == ToontownGlobals.FullPies:
                self.__pieButton['text'] = ''
            else:
                self.__pieButton['text'] = str(self.numPies)
            self.__pieButtonCount = self.numPies
        return

    def setSystemMessage(self, aboutId, chatString, whisperType = WhisperPopup.WTSystem):
        self.displayWhisper(aboutId, chatString, whisperType)

    def displayWhisper(self, fromId, chatString, whisperType):
        sender = None
        sfx = self.soundWhisper
        if fromId == TTLocalizer.Clarabelle:
            chatString = TTLocalizer.Clarabelle + ': ' + chatString
            sfx = self.soundPhoneRing
        elif fromId != 0:
            sender = base.cr.identifyAvatar(fromId)
        if whisperType == WhisperPopup.WTNormal or whisperType == WhisperPopup.WTQuickTalker:
            if sender == None:
                return
            chatString = sender.getName() + ': ' + chatString
        elif whisperType == WhisperPopup.WTSystem:
            sfx = self.soundSystemMessage
        whisper = WhisperPopup(chatString, OTPGlobals.getInterfaceFont(), whisperType)
        if sender != None:
            whisper.setClickable(sender.getName(), fromId)
        whisper.manage(base.marginManager)
        base.playSfx(sfx)
        return

    def takeDamage(self, hpLost, bonus = 0):
        if self.hp == None or hpLost < 0:
            return
        oldHp = self.hp
        newHp = max(self.hp - hpLost, 0)
        hpLost = oldHp - newHp
        if hpLost >= 0:
            # a little hacky but whatever
            if hasattr(base.cr.playGame.getActiveZone(), 'battle') and base.cr.playGame.getActiveZone().battle:
                if base.cr.playGame.getActiveZone().battle.battleCalc.defenseBoostActive:
                    self.showHpTextBoost(-hpLost, 2)
                else:
                    self.showHpText(-hpLost, bonus)
            else:
                self.showHpText(-hpLost, bonus)
            self.setHealth(newHp, self.maxHp)
            if self.hp <= 0 and oldHp > 0:
                if hasattr(base.cr.playGame.getActiveZone(), 'battle') and base.cr.playGame.getActiveZone().battle:
                    # Give the movie some time to switch camera angles if it needs to before we take control of the camera
                    taskMgr.doMethodLater(0.5, self.goSad, '%d-goSad' % self.doId)
                else:
                    self.goSad(None, callback=self.died)

    def goSad(self, task, callback=None):
        self.enable()
        self.disable()
        camera.wrtReparentTo(render)
        self.setAnimState('Died')
        self.inventory.zeroInv(killUber=1)
        self.inventory.updateGUI()
        self.inventory.saveInventory()
        if callback:
            Sequence(Wait(base.localAvatar.getDuration('lose')), Func(callback)).start()
        if task:
            return Task.done

    def startToonUp(self, healFrequency):
        self.stopToonUp()
        self.healFrequency = healFrequency
        self.__waitForNextToonUp()

    def stopToonUp(self):
        taskMgr.remove(self.uniqueName('safeZoneToonUp'))

    def __waitForNextToonUp(self):
        taskMgr.doMethodLater(self.healFrequency, self.toonUpTask, self.uniqueName('safeZoneToonUp'))

    def toonUpTask(self, task):
        hp = self.hp + self.toonUpIncrement
        self.setHealth(hp, self.maxHp, showText=1)
        if not self.isToonedUp():
            self.__waitForNextToonUp()
        return Task.done

    def isToonedUp(self):
        return self.hp >= self.maxHp

    def showHpText(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpText:
                self.hideHpText()
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            if number <= 0:
                if number == 0:
                    self.HpTextGenerator.setText('-' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                    self.sillySurgeText = True
                    if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                        self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
            else:
                self.HpTextGenerator.setText('+' + str(number))
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            if bonus == 1:
                r = 1.0
                g = 1.0
                b = 0
                a = 1
            elif bonus == 2:
                r = 1.0
                g = 0.5
                b = 0
                a = 1
            elif number <= 0:
                r = 0.9
                g = 0
                b = 0
                a = 1
                if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                    r = 0
                    g = 0
                    b = 1
                    a = 1
            else:
                r = 0
                g = 0.9
                b = 0
                a = 1
            self.HpTextGenerator.setTextColor(r, g, b, a)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            if self.sillySurgeText:
                self.nametag3d.setDepthTest(0)
                self.nametag3d.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(0.85), self.hpText.colorInterval(0.1, Vec4(r, g, b, 0), 0.1), Func(self.hideHpText))
            seq.start()

    def showHpTextBoost(self, number, boost):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpText:
                self.hideHpText()
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            stringText = TextNode('stringText')
            stringText.setFont(OTPGlobals.getSignFont())
            if boost == 1:
                stringText.setText('Boost')
                if number <= 0:
                    if number == 0:
                        self.HpTextGenerator.setText('-%d' % number)
                    else:
                        self.HpTextGenerator.setText(str(number))
                else:
                    self.HpTextGenerator.setText('+%d' % number)
            elif boost == 2:
                stringText.setText('Resist')
                if number <= 0:
                    if number == 0:
                        self.HpTextGenerator.setText('-%d' % number)
                    else:
                        self.HpTextGenerator.setText(str(number))
                else:
                    self.HpTextGenerator.setText('+%d' % number)
            if number <= 0:
                r = 0.9
                g = 0
                b = 0
                a = 1
            else:
                r = 0
                g = 0.9
                b = 0
                a = 1
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            self.HpTextGenerator.setTextColor(r, g, b, a)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(1)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)

            stringText.clearShadow()
            stringText.setAlign(TextNode.ACenter)
            stringText.setTextColor(r, g, b, a)
            strTextNode = stringText.generate()
            self.strText = self.attachNewNode(strTextNode)
            self.strText.setScale(0.5)
            self.strText.setBillboardPointEye()
            self.strText.setBin('fixed', 100)

            self.nametag3d.setDepthTest(0)
            self.nametag3d.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.strText.setPos(0, 0, (self.height / 2) + 1.0)
            seq = Sequence(Parallel(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), self.strText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut')), Wait(0.85), Parallel(self.hpText.colorInterval(0.1, Vec4(r, g, b, 0), 0.1), self.strText.colorInterval(0.1, Vec4(r, g, b, 0), 0.1)), Func(self.hideHpText))
            seq.start()

    def showHpString(self, text, duration = 0.85, scale = 0.7, color = Vec4(1, 0, 0, 1), trackFrame = 0, carryIndex = 0, carryAmount = 0):
        if self.HpTextEnabled and not self.ghostMode:
            if text != '':
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                self.HpTextGenerator.setText(text)
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                self.HpTextGenerator.setTextColor(color)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                offset = 0
                if carryIndex:
                    if carryIndex == 6:
                        self.HpTextGenerator.setText(TTLocalizer.RewardCarryToonTasksText % carryAmount)
                    elif carryIndex == 7:
                        self.HpTextGenerator.setText(TTLocalizer.RewardCarryGagsText % carryAmount)
                    elif carryIndex == 8:
                        self.HpTextGenerator.setText(TTLocalizer.RewardCarryJellybeansText % carryAmount)
                    self.HpTextGenerator.setTextColor(Vec4(0.9, 0.6, 0, 1))
                    self.auxText = self.attachNewNode(self.HpTextGenerator.generate())
                    self.auxText.setScale(scale * 0.7)
                    self.auxText.setBillboardAxis()
                    self.auxText.setPos(0, 0, self.height / 2)
                    offset += 0.7
                elif trackFrame:
                    self.HpTextGenerator.setText(TTLocalizer.RewardTrackFrameText % {'trackName': TTLocalizer.BattleGlobalTracks[self.trackProgressId], 'frameNum': trackFrame})
                    self.HpTextGenerator.setTextColor(Vec4(0.5, 0.5, 0.5, 1))
                    self.auxText = self.attachNewNode(self.HpTextGenerator.generate())
                    self.auxText.setScale(scale * 0.7)
                    self.auxText.setBillboardAxis()
                    self.auxText.setPos(0, 0, self.height / 2)
                    offset += 0.7
                self.hpText.setPos(0, 0, (self.height / 2) + offset)
                if hasattr(self, 'auxText'):
                    seq = Sequence(
                        Parallel(
                            self.hpText.posInterval(1.0, Point3(0, 0, (self.height + 1.3) + offset), blendType='easeOut'),
                            self.auxText.posInterval(1.0, Point3(0, 0, self.height + 1.3), blendType='easeOut')
                        ),
                        Wait(duration),
                        Parallel(
                            self.hpText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0)),
                            self.auxText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0))
                        ),
                        Func(self.hideHpText)
                    )
                else:
                    seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.3), blendType='easeOut'), Wait(duration), self.hpText.colorScaleInterval(1.0, Vec4(1.0, 1.0, 1.0, 0)), Func(self.hideHpText))
                seq.start()

    def hideHpText(self):
        if self.hpText:
            taskMgr.remove(self.uniqueName('hpText'))
            self.hpText.removeNode()
            self.hpText = None
        if self.strText:
            self.strText.removeNode()
            self.strText = None
        if hasattr(self, 'auxText'):
            self.auxText.removeNode()
            del self.auxText
        if self.nametag3d:
            self.nametag3d.clearDepthTest()
            self.nametag3d.clearBin()
        self.sillySurgeText = False

    def died(self):
        self.reparentTo(render)
        base.cr.playGame.exitActiveZone()
        self.enable()
        self.disable()
        zoneId = self.getZoneId()
        hoodId = FunnyFarmGlobals.getHoodId(zoneId)
        base.cr.playGame.enterHood(hoodId)

    def sayLocation(self):
        locStr = "X: {0}\nY: {1}\nZ: {2}\nH: {3}\nZone: {4}\nVersion: {5}".format(round(self.getX(), 3), round(self.getY(), 3), round(self.getZ(), 3), round(self.getH(), 3),
                                                                                  self.zoneId, config.GetString('game-version', 'no_version_set'))
        self.setChatAbsolute(locStr, CFThought | CFTimeout)

    def disableBodyCollisions(self):
        pass

    # These functions are for reflections of the toon on the floor in places like Loony Labs.
    # This is currently just an alpha test; it looks pretty awkward for a variety of reasons,
    # so I'm unsure if we're going to keep it or not.
    def makeReflection(self):
        self.reflection = Toon.Toon()
        self.reflection.setDNA(self.getDNA())
        self.reflection.setHat(*base.avatarData.setHat)
        self.reflection.setGlasses(*base.avatarData.setGlasses)
        self.reflection.setBackpack(*base.avatarData.setBackpack)
        self.reflection.setShoes(*base.avatarData.setShoes)
        self.reflection.applyCheesyEffect(base.avatarData.setCheesyEffect)
        self.reflection.hideName()
        self.reflection.hideShadow()
        self.reflection.reparentTo(self)
        self.reflection.setR(180)
        self.reflection.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))
        self.reflection.setBin('default', 0)
        self.reflection.setSx(-1)
        self.reflection.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MNone))
        self.reflection.setZ(-0.15)
        self.reflection.setAnimState('neutral', 1.0)

    def deleteReflection(self):
        self.reflection.delete()
        del self.reflection

    def startUpdateReflection(self):
        self.reflectionAnim = None
        self.reflectionRate = 1.0
        taskMgr.add(self.updateReflection, 'ltUpdateReflection')

    def stopUpdateReflection(self):
        taskMgr.remove('ltUpdateReflection')
        del self.reflectionAnim
        del self.reflectionRate

    def updateReflection(self, task):
        reflectionAnim = self.reflectionAnim
        reflectionRate = self.reflectionRate
        playingAnim = self.getCurrentAnim()
        playingRate = self.getPlayRate()
        if playingAnim == None:
            playingAnim = self.playingAnim
        if reflectionAnim != playingAnim or reflectionRate != playingRate:
            self.reflectionAnim = playingAnim
            self.reflectionRate = playingRate
            if playingAnim == 'jump-idle' or playingAnim == 'running-jump-idle':
                if playingAnim == 'running-jump-idle':
                    self.reflection.playingAnim = None
                self.reflection.setAnimState('jumpAirborne', 1.0)
            elif playingAnim == 'jump-land' or playingAnim == 'running-jump-land':
                self.reflection.setAnimState('jumpLand', 1.0)
            elif playingAnim == 'openBook':
                self.reflection.enterOpenBook()
            elif playingAnim == 'readBook':
                self.reflection.enterReadBook()
            elif playingAnim == 'closeBook':
                self.reflection.enterCloseBook()
            else:
                if self.reflection.animFSM.getStateNamed(self.reflectionAnim):
                    self.reflection.setAnimState(self.reflectionAnim, self.reflectionRate)
                else:
                    self.reflection.loop(self.reflectionAnim)
        if playingAnim == 'jump-idle' or playingAnim == 'running-jump-idle':
            self.reflection.setZ((-self.getZ() * 2) - 0.15)
        else:
            self.reflection.setZ(-0.15)
        return Task.cont

@magicWord(argTypes=[int], aliases=['setHealth', 'hp', 'health'])
def setHp(hp):
    maxHp = base.localAvatar.maxHp
    hp = int(hp)
    if hp > maxHp or hp < -1:
        return 'Your health must be within -1-%d!' % maxHp
    base.localAvatar.setHealth(hp, maxHp)

@magicWord(argTypes=[int], aliases=['addQuest'])
def questAdd(id):
    av = base.localAvatar
    if not Quests.isQuest   (id):
        return 'Invalid quest ID!'
    if len(av.quests) >= av.questCarryLimit:
        return 'Cannot add quest %d; maximum quests reached!' % id

    av.quests.append([id, 0])
    messenger.send('questsChanged')

    if base.avatarData.setQuests != av.quests:
        base.avatarData.setQuests = av.quests[:]
        dataMgr.saveToonData(base.avatarData)

@magicWord(argTypes=[int, int])
def setQuest(taskId, slotId=0):
    av = base.localAvatar
    if not Quests.isQuest(taskId):
        return 'Invalid quest ID!'
    if len(av.quests) - 1 < slotId:
        return 'Cannot add quest %d, non-existent slot!' % taskId

    av.quests[slotId] = [taskId, 0]
    messenger.send('questsChanged')

    if base.avatarData.setQuests != av.quests:
        base.avatarData.setQuests = av.quests[:]
        dataMgr.saveToonData(base.avatarData)

@magicWord(argTypes=[int], aliases=['addQuestHistory'])
def appendQuestHistory(taskId):
    av = base.localAvatar
    if not Quests.isQuest(taskId):
        return 'Invalid quest ID!'
    av.addQuestHistory(taskId)

@magicWord(argTypes=[int])
def addMoney(money):
    av = base.localAvatar
    av.addMoney(money)

@magicWord(argTypes=[int])
def setMoney(money):
    av = base.localAvatar
    av.setMoney(money)

@magicWord()
def maxToon():
    av = base.localAvatar
    av.maxToon()

@magicWord()
def resetToon():
    av = base.localAvatar
    av.resetToon()

@magicWord()
def unlimited():
    av = base.localAvatar
    av.unlimitedGags = not av.unlimitedGags
