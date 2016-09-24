from pandac.PandaModules import *
from direct.showbase import PythonUtil
from direct.showbase.PythonUtil import *
from direct.distributed.ClockDelta import *
from direct.actor.Actor import Actor
from direct.task import Task
from direct.interval.IntervalGlobal import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toon import Toon
from toontown.toon.LaffMeter import LaffMeter
from WalkControls import WalkControls
from toontown.chat.ChatManager import ChatManager
from toontown.chat.ChatGlobals import *
from otp.margins.WhisperPopup import *
from toontown.book import ShtikerBook
from toontown.book import OptionsPage
from toontown.book import MapPage
from toontown.book import ToonPage
from toontown.book import InventoryPage
from otp.otpbase import OTPGlobals
import InventoryNew
import Experience
import random

class LocalToon(Toon.Toon, WalkControls):
    notify = directNotify.newCategory('LocalToon')
    piePowerSpeed = base.config.GetDouble('pie-power-speed', 0.2)
    piePowerExponent = base.config.GetDouble('pie-power-exponent', 0.75)
    HpTextGenerator = TextNode('HpTextGenerator')
    HpTextEnabled = 1

    def __init__(self):
        Toon.Toon.__init__(self)
        WalkControls.__init__(self)
        self.chatMgr = ChatManager()
        self.soundWhisper = base.loadSfx('phase_3.5/audio/sfx/GUI_whisper_3.ogg')
        self.soundPhoneRing = base.loadSfx('phase_3.5/audio/sfx/telephone_ring.ogg')
        self.soundSystemMessage = base.loadSfx('phase_3/audio/sfx/clock03.ogg')
        self.zoneId = None
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
        self.maxNPCFriends = 16
        self.tossTrack = None
        self.pieTracks = {}
        self.splatTracks = {}
        self.lastTossedPie = 0
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
        self.tunnelTrack = None
        self.tunnelPivotPos = [-14, -6, 0]
        self.tunnelCenterOffset = 9.0
        self.tunnelCenterInfluence = 0.6
        self.pivotAngle = 90 + 45
        self.tunnelX = 0.0
        self.inventory = None
        self.hpText = None
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
        self.quests = []

    def delete(self):
        try:
            self.LocalToon_deleted
        except:
            self.LocalToon_deleted = 1
            self.ignoreAll()
            Toon.Toon.delete(self)
            WalkControls.delete(self)
            self.stopToonUp()
            self.endAllowPies()
            self.laffMeter.destroy()
            self.chatMgr.delete()
            if self.inventory:
                self.inventory.unload()
            self.book.unload()
            del self.laffMeter
            del self.optionsPage
            del self.mapPage
            del self.toonPage
            del self.invPage
            del self.chatMgr
            del self.inventory
            del self.book

    def isLocal(self):
        return True

    def setDoId(self, doId):
        self.doId = doId

    def getDoId(self):
        return self.doId

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, str(self.doId)))

    def enable(self):
        self.collisionsOn()
        self.enableAvatarControls()
        self.setupSmartCamera()
        self.book.showButton()
        self.beginAllowPies()
        self.invPage.acceptOnscreenHooks()
        self.setAnimState('neutral')

    def disable(self):
        self.stopUpdateSmartCamera()
        self.shutdownSmartCamera()
        self.disableAvatarControls()
        self.collisionsOff()
        self.book.hideButton()
        self.endAllowPies()
        self.invPage.ignoreOnscreenHooks()
        self.invPage.hideInventoryOnscreen()

    def setZoneId(self, zoneId):
        self.zoneId = zoneId
        # Check if we need to start the toonup task
        self.considerToonUp(zoneId)

    def getZoneId(self):
        return self.zoneId

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

    def stopChat(self):
        self.chatMgr.deleteGui()
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
        self.laffMeter = LaffMeter(self.style, self.hp, self.maxHp)
        self.laffMeter.setAvatar(self)
        self.laffMeter.setScale(0.075)
        self.laffMeter.reparentTo(base.a2dBottomLeft)
        if self.style.getAnimal() == 'monkey':
            self.laffMeter.setPos(0.153, 0.0, 0.13)
        else:
            self.laffMeter.setPos(0.133, 0.0, 0.13)
        self.laffMeter.stop()
        self.accept('time-insert', self.__beginTossPie)
        self.accept('time-insert-up', self.__endTossPie)
        self.accept('time-delete', self.__beginTossPie)
        self.accept('time-delete-up', self.__endTossPie)
        self.accept('pieHit', self.__pieHit)
        self.accept('interrupt-pie', self.interruptPie)

    def enableDebug(self):
        onScreenDebug.enabled = True

        def updateOnScreenDebug(task):
            onScreenDebug.add('Avatar Position', self.getPos())
            onScreenDebug.add('Avatar Angle', self.getHpr())
            return Task.cont

        taskMgr.add(updateOnScreenDebug, 'UpdateOSD')

    def setHealth(self, hp, maxHp, showText=0):
        oldHp = self.hp
        self.hp = hp
        self.maxHp = maxHp
        if self.hp >= self.maxHp:
            self.hp = self.maxHp
        if self.laffMeter:
            self.laffMeter.adjustFace(self.hp, self.maxHp)
        if showText:
            self.showHpText(self.hp - oldHp)
        if self.hp > 0 and self.animFSM.getCurrentState().getName() == 'Sad':
            self.setAnimState('Happy')
        self.setToonUpIncrement()
        base.avatarData.setHp = self.hp
        base.avatarData.setMaxHp = self.maxHp
        dataMgr.saveToonData(base.avatarData)

    def setToonUpIncrement(self):
        # At 0 hp, there are roughly 20 toonup intervals in 5 minutes, so if we divide the maxHp by 20 
        # and round to the nearest integer, we'll get an increment that will restore the player's health 
        # from 0 to max in roughly 5 minutes.
        self.toonUpIncrement = int(round(self.maxHp / 20))

    def setName(self, name):
        self.nametag.setName(name)
        base.avatarData.setName = name
        dataMgr.saveToonData(base.avatarData)

    def getName(self):
        return self.nametag.name

    def getMaxNPCFriends(self):
        return self.maxNPCFriends

    def setNametagFont(self, font):
        self.nametag.setFont(font)
        base.avatarData.setNametagStyle = FunnyFarmGlobals.nametagDict[font]
        dataMgr.saveToonData(base.avatarData)

    def setHat(self, hatIdx, textureIdx, colorIdx, fromRTM = False):
        Toon.Toon.setHat(self, hatIdx, textureIdx, colorIdx, fromRTM = False)
        base.avatarData.setHat = [hatIdx, textureIdx, colorIdx]
        dataMgr.saveToonData(base.avatarData)

    def setGlasses(self, glassesIdx, textureIdx, colorIdx, fromRTM = False):
        Toon.Toon.setGlasses(self, glassesIdx, textureIdx, colorIdx, fromRTM = False)
        base.avatarData.setGlasses = [glassesIdx, textureIdx, colorIdx]
        dataMgr.saveToonData(base.avatarData)

    def setBackpack(self, backpackIdx, textureIdx, colorIdx, fromRTM = False):
        Toon.Toon.setBackpack(self, backpackIdx, textureIdx, colorIdx, fromRTM = False)
        base.avatarData.setBackpack = [backpackIdx, textureIdx, colorIdx]
        dataMgr.saveToonData(base.avatarData)

    def setShoes(self, shoesIdx, textureIdx, colorIdx):
        Toon.Toon.setShoes(self, shoesIdx, textureIdx, colorIdx)
        base.avatarData.setShoes = [shoesIdx, textureIdx, colorIdx]
        dataMgr.saveToonData(base.avatarData)

    def setCheesyEffect(self, effect):
        Toon.Toon.applyCheesyEffect(self, effect, lerpTime=0.5)
        base.avatarData.setCheesyEffect = effect
        dataMgr.saveToonData(base.avatarData)

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
        base.avatarData.setMoney = self.money
        dataMgr.saveToonData(base.avatarData)

    def getMoney(self):
        return self.money

    def setMaxMoney(self, maxMoney):
        self.maxMoney = maxMoney
        base.avatarData.setMaxMoney = self.maxMoney
        dataMgr.saveToonData(base.avatarData)

    def getMaxMoney(self):
        return self.maxMoney

    def setBankMoney(self, bankMoney):
        self.bankMoney = bankMoney
        base.avatarData.setBankMoney = self.bankMoney
        dataMgr.saveToonData(base.avatarData)

    def getBankMoney(self):
        return self.bankMoney

    def setMaxBankMoney(self, maxBankMoney):
        self.maxBankMoney = maxBankMoney
        base.avatarData.setMaxBankMoney = self.maxBankMoney
        dataMgr.saveToonData(base.avatarData)

    def getMaxBankMoney(self):
        return self.maxBankMoney

    def setTrackAccess(self, trackArray):
        self.trackArray = trackArray
        if self.inventory:
            self.inventory.updateGUI()
        base.avatarData.setTrackAccess = self.trackArray
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
        base.avatarData.setMaxCarry = self.maxCarry
        dataMgr.saveToonData(base.avatarData)

    def getMaxCarry(self):
        return self.maxCarry

    def getPinkSlips(self):
        return 0

    def setInventory(self, inventory):
        self.inventory = InventoryNew.InventoryNew(self, invStr=inventory)
        self.inventory.updateGUI()
        self.inventory.saveInventory()

    def setExperience(self, experience):
        self.experience = Experience.Experience(experience, self)
        if self.inventory:
            self.inventory.updateGUI()
        self.experience.saveExp()

    def setLevel(self, level):
        self.level = level
        base.avatarData.setLevel = self.level
        dataMgr.saveToonData(base.avatarData)

    def getLevel(self):
        return self.level

    def setLevelExp(self, levelExp):
        self.levelExp = levelExp
        base.avatarData.setLevelExp = self.levelExp
        dataMgr.saveToonData(base.avatarData)

    def getLevelExp(self):
        return self.levelExp

    def getMaxLevelExp(self):
        return FunnyFarmGlobals.LevelExperience[self.level - 1]

    def setDamage(self, damageArray):
        self.damage = damageArray
        base.avatarData.setDamage = self.damage
        dataMgr.saveToonData(base.avatarData)

    def getDamage(self):
        return self.damage

    def setDefense(self, defenseArray):
        self.defense = defenseArray
        base.avatarData.setDefense = self.defense
        dataMgr.saveToonData(base.avatarData)

    def getDefense(self):
        return self.defense

    def setAccuracy(self, accuracyArray):
        self.accuracy = accuracyArray
        base.avatarData.setAccuracy = self.accuracy
        dataMgr.saveToonData(base.avatarData)

    def getAccuracy(self):
        return self.accuracy

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

    def resetToon(self):
        self.setHealth(20, 20, showText=1)
        self.setTrackAccess([0, 0, 0, 0, 1, 1, 0])
        self.setMaxCarry(20)
        self.experience.zeroOutExp()
        self.inventory.zeroInv()
        self.inventory.addItem(4, 0)
        self.inventory.addItem(5, 0)
        self.inventory.updateGUI()
        self.setDamage([0, 0, 0, 0, 0, 0])
        self.setDefense([0, 0, 0, 0])
        self.setAccuracy([0, 0, 0, 0, 0, 0])
        self.setMaxMoney(40)
        self.setMoney(0)
        self.setBankMoney(0)

    def setRandomSpawn(self, zoneId):
        if zoneId not in FunnyFarmGlobals.SpawnPoints.keys():
            return
        spawnPoints = FunnyFarmGlobals.SpawnPoints[zoneId]
        spawn = random.choice(spawnPoints)
        self.setPos(spawn[0])
        self.setHpr(spawn[1])

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
        import TTEmote
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
        taskMgr.remove('AnimationHandler')
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
            import TTEmote
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
        taskMgr.add(self.handleAnimation, 'AnimationHandler')

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

    def setSystemMessage(self, aboutId, chatString, whisperType = WTSystem):
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
        self.hp = max(self.hp - hpLost, 0)
        hpLost = oldHp - self.hp
        if hpLost > 0:
            self.showHpText(-hpLost, bonus)
            self.setHealth(self.hp, self.maxHp)
            if self.hp <= 0 and oldHp > 0:
                self.setupCamera()
                camera.wrtReparentTo(render)
                self.setAnimState('Died', callback=self.died)
        return

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
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
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
                elif number < 0:
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

    def showHpString(self, text, duration = 0.85, scale = 0.7):
        if self.HpTextEnabled and not self.ghostMode:
            if text != '':
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                self.HpTextGenerator.setText(text)
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                r = a = 1.0
                g = b = 0.0
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(duration), self.hpText.colorInterval(0.1, Vec4(r, g, b, 0)), Func(self.hideHpText))
                seq.start()

    def hideHpText(self):
        if self.hpText:
            taskMgr.remove(self.uniqueName('hpText'))
            self.hpText.removeNode()
            self.hpText = None
        if self.sillySurgeText:
            self.nametag3d.clearDepthTest()
            self.nametag3d.clearBin()
            self.sillySurgeText = False

    def died(self):
        base.cr.playGame.exitActiveZone()
        self.reparentTo(render)
        self.enable()
        zoneId = self.getZoneId()
        hoodId = FunnyFarmGlobals.getHoodId(zoneId)
        base.cr.playGame.enterHood(hoodId)
