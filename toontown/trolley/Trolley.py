from panda3d.core import *
from direct.task.Task import Task
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from toontown.trolley.TrolleyConstants import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
import math

class Trolley(DirectObject):
    notify = directNotify.newCategory('Trolley')

    def __init__(self):
        self.trolleyCountdownTime = TROLLEY_COUNTDOWN_TIME
        self.trolleyAwaySfx = base.loader.loadSfx('phase_4/audio/sfx/SZ_trolley_away.ogg')
        self.trolleyBellSfx = base.loader.loadSfx('phase_4/audio/sfx/SZ_trolley_bell.ogg')
        self.trolleySong = base.loader.loadMusic('phase_4/audio/bgm/trolley_song.ogg')

    def setup(self):
        self.trolleyStation = base.cr.playGame.hood.geom.find('**/*trolley_station*')
        self.trolleyCar = self.trolleyStation.find('**/trolley_car')
        self.trolleySphereNode = self.trolleyStation.find('**/trolley_sphere').node()
        exitFog = Fog('TrolleyExitFog')
        exitFog.setColor(0.0, 0.0, 0.0)
        exitFog.setLinearOnsetPoint(30.0, 14.0, 0.0)
        exitFog.setLinearOpaquePoint(37.0, 14.0, 0.0)
        exitFog.setLinearFallback(70.0, 999.0, 1000.0)
        self.trolleyExitFog = self.trolleyStation.attachNewNode(exitFog)
        self.trolleyExitFogNode = exitFog
        enterFog = Fog('TrolleyEnterFog')
        enterFog.setColor(0.0, 0.0, 0.0)
        enterFog.setLinearOnsetPoint(0.0, 14.0, 0.0)
        enterFog.setLinearOpaquePoint(-7.0, 14.0, 0.0)
        enterFog.setLinearFallback(70.0, 999.0, 1000.0)
        self.trolleyEnterFog = self.trolleyStation.attachNewNode(enterFog)
        self.trolleyEnterFogNode = enterFog
        self.trolleyCar.setFogOff()
        self.keys = self.trolleyCar.findAllMatches('**/key')
        self.numKeys = self.keys.getNumPaths()
        self.keyInit = []
        self.keyRef = []
        for i in range(self.numKeys):
            key = self.keys[i]
            key.setTwoSided(1)
            ref = self.trolleyCar.attachNewNode('key' + repr(i) + 'ref')
            ref.setPosHpr(key, 0, 0, 0, 0, 0, 0)
            self.keyRef.append(ref)
            self.keyInit.append(key.getTransform())

        self.frontWheels = self.trolleyCar.findAllMatches('**/front_wheels')
        self.numFrontWheels = self.frontWheels.getNumPaths()
        self.frontWheelInit = []
        self.frontWheelRef = []
        for i in range(self.numFrontWheels):
            wheel = self.frontWheels[i]
            ref = self.trolleyCar.attachNewNode('frontWheel' + repr(i) + 'ref')
            ref.setPosHpr(wheel, 0, 0, 0, 0, 0, 0)
            self.frontWheelRef.append(ref)
            self.frontWheelInit.append(wheel.getTransform())

        self.backWheels = self.trolleyCar.findAllMatches('**/back_wheels')
        self.numBackWheels = self.backWheels.getNumPaths()
        self.backWheelInit = []
        self.backWheelRef = []
        for i in range(self.numBackWheels):
            wheel = self.backWheels[i]
            ref = self.trolleyCar.attachNewNode('backWheel' + repr(i) + 'ref')
            ref.setPosHpr(wheel, 0, 0, 0, 0, 0, 0)
            self.backWheelRef.append(ref)
            self.backWheelInit.append(wheel.getTransform())

        trolleyAnimationReset = Func(self.resetAnimation)
        trolleyEnterStartPos = Point3(-20, 14, -1)
        trolleyEnterEndPos = Point3(15, 14, -1)
        trolleyEnterPos = Sequence(name='TrolleyEnterPos')
        trolleyEnterPos.append(Func(self.trolleyCar.setFog, self.trolleyEnterFogNode))
        trolleyEnterPos.append(self.trolleyCar.posInterval(TROLLEY_ENTER_TIME, trolleyEnterEndPos, startPos=trolleyEnterStartPos, blendType='easeOut'))
        trolleyEnterPos.append(Func(self.trolleyCar.setFogOff))
        trolleyEnterTrack = Sequence(trolleyAnimationReset, trolleyEnterPos, name='trolleyEnter')
        keyAngle = round(TROLLEY_ENTER_TIME) * 360
        dist = Vec3(trolleyEnterEndPos - trolleyEnterStartPos).length()
        wheelAngle = dist / (2.0 * math.pi * 0.95) * 360
        trolleyEnterAnimateInterval = LerpFunctionInterval(self.animateTrolley, duration=TROLLEY_ENTER_TIME, blendType='easeOut', extraArgs=[keyAngle, wheelAngle], name='TrolleyAnimate')
        trolleyEnterSoundTrack = SoundInterval(self.trolleyAwaySfx, node=self.trolleyCar)
        self.trolleyEnterTrack = Parallel(trolleyEnterTrack, trolleyEnterAnimateInterval, trolleyEnterSoundTrack)
        trolleyExitStartPos = Point3(15, 14, -1)
        trolleyExitEndPos = Point3(50, 14, -1)
        trolleyExitPos = Sequence(name='TrolleyExitPos')
        trolleyExitPos.append(Func(self.trolleyCar.setFog, self.trolleyExitFogNode))
        trolleyExitPos.append(self.trolleyCar.posInterval(TROLLEY_EXIT_TIME, trolleyExitEndPos, startPos=trolleyExitStartPos, blendType='easeIn'))
        trolleyExitPos.append(Func(self.trolleyCar.setFogOff))
        trolleyExitPos.append(Func(messenger.send, 'playMinigame'))
        trolleyExitBellInterval = SoundInterval(self.trolleyBellSfx, node=self.trolleyCar)
        trolleyExitAwayInterval = SoundInterval(self.trolleyAwaySfx, node=self.trolleyCar)
        keyAngle = round(TROLLEY_EXIT_TIME) * 360
        dist = Vec3(trolleyExitEndPos - trolleyExitStartPos).length()
        wheelAngle = dist / (2.0 * math.pi * 0.95) * 360
        trolleyExitAnimateInterval = LerpFunctionInterval(self.animateTrolley, duration=TROLLEY_EXIT_TIME, blendType='easeIn', extraArgs=[keyAngle, wheelAngle], name='TrolleyAnimate')
        self.trolleyExitTrack = Parallel(trolleyExitPos, trolleyExitBellInterval, trolleyExitAwayInterval, trolleyExitAnimateInterval, name=self.uniqueName('trolleyExit'))
        self.buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        self.upButton = self.buttonModels.find('**//InventoryButtonUp')
        self.downButton = self.buttonModels.find('**/InventoryButtonDown')
        self.rolloverButton = self.buttonModels.find('**/InventoryButtonRollover')

    def delete(self):
        self.trolleyExitFog.removeNode()
        del self.trolleyExitFog
        del self.trolleyExitFogNode
        self.trolleyEnterFog.removeNode()
        del self.trolleyEnterFog
        del self.trolleyEnterFogNode
        self.trolleyEnterTrack.pause()
        self.trolleyEnterTrack = None
        del self.trolleyEnterTrack
        self.trolleyExitTrack.pause()
        self.trolleyExitTrack = None
        del self.trolleyExitTrack
        del self.trolleyStation
        del self.trolleyCar
        del self.keys
        del self.numKeys
        del self.keyInit
        del self.keyRef
        del self.frontWheels
        del self.numFrontWheels
        del self.frontWheelInit
        del self.frontWheelRef
        del self.backWheels
        del self.numBackWheels
        del self.backWheelInit
        del self.backWheelRef
        del self.trolleyAwaySfx
        del self.trolleyBellSfx
        del self.trolleySong
        self.buttonModels.removeNode()
        del self.buttonModels
        del self.upButton
        del self.downButton
        del self.rolloverButton

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, str(id(self))))

    def addActive(self):
        self.accept('entertrolley_sphere', self.handleEnterTrolleySphere)
        self.trolleySphereNode.setCollideMask(ToontownGlobals.WallBitmask)

    def removeActive(self):
        self.ignore('entertrolley_sphere')
        self.trolleySphereNode.setCollideMask(BitMask32(0))

    def handleEnterTrolleySphere(self, collEntry):
        self.notify.debug('Entering Trolley Sphere...')
        if base.localAvatar.getPos(render).getZ() < self.trolleyCar.getPos(render).getZ():
            return
        base.localAvatar.disable()
        base.localAvatar.experienceBar.hide()
        base.localAvatar.setAnimState('neutral')
        self.dialog = TTDialog.TTDialog(text=TTLocalizer.TrolleyDialog, text_align=TextNode.ACenter, style=TTDialog.YesNo, command=self.handleEnterTrolley)
        self.dialog.show()

    def handleEnterTrolley(self, choice):
        self.dialog.destroy()
        if choice == 1:
            self.fillSlot(0)
            # musicMgr.stopMusic()
            # musicMgr.playMusic(self.trolleySong)
        else:
            base.localAvatar.enable()
            base.localAvatar.experienceBar.show()

    def fillSlot(self, index):
        camera.wrtReparentTo(self.trolleyCar)
        self.cameraBoardTrack = LerpPosHprInterval(camera, 1.5, Point3(-35, 0, 8), Point3(-90, 0, 0))
        toon = base.localAvatar
        toon.wrtReparentTo(self.trolleyCar)
        toon.setAnimState('run')
        toon.headsUp(-5, -4.5 + index * 3, 1.4)
        sitStartDuration = toon.getDuration('sit-start')
        track = Sequence(LerpPosInterval(toon, TOON_BOARD_TIME * 0.75, Point3(-5, -4.5 + index * 3, 1.4)), LerpHprInterval(toon, TOON_BOARD_TIME * 0.25, Point3(90, 0, 0)), Parallel(Sequence(Wait(sitStartDuration * 0.25), LerpPosInterval(toon, sitStartDuration * 0.25, Point3(-3.9, -4.5 + index * 3, 3.0))), ActorInterval(toon, 'sit-start')), Func(toon.setAnimState, 'Sit'), Func(self.enterLeaving), name=toon.uniqueName('fillTrolley'), autoPause=1)
        self.cameraBoardTrack.start()
        track.start()
        # self.enableExitButton()
        # self.enterWaitCountdown(0)

    def emptySlot(self, index):
        toon = base.localAvatar
        toon.setHpr(self.trolleyCar, 90, 0, 0)
        toon.wrtReparentTo(render)
        sitStartDuration = toon.getDuration('sit-start')
        track = Sequence(Parallel(ActorInterval(toon, 'sit-start', startTime=sitStartDuration, endTime=0.0), Sequence(Wait(sitStartDuration * 0.5), LerpPosInterval(toon, sitStartDuration * 0.25, Point3(-5, -4.5 + index * 3, 1.4), other=self.trolleyCar))), Func(toon.setAnimState, 'run'), LerpPosInterval(toon, TOON_EXIT_TIME, Point3(21 - index * 3, -5, 0.02), other=self.trolleyStation), name=toon.uniqueName('emptyTrolley'), autoPause=1)
        track.setDoneEvent(track.getName())
        self.acceptOnce(track.getName(), self.handleTrolleyDone)
        track.start()
        # self.disableExitButton()
        # self.exitWaitCountdown()

    def handleTrolleyDone(self):
        # self.trolleySong.stop()
        # musicMgr.playCurrentZoneMusic()
        base.localAvatar.enable()
        base.localAvatar.experienceBar.show()

    def enterWaitCountdown(self, ts):
        self.clockNode = TextNode('trolleyClock')
        self.clockNode.setFont(ToontownGlobals.getSignFont())
        self.clockNode.setAlign(TextNode.ACenter)
        self.clockNode.setTextColor(0.9, 0.1, 0.1, 1)
        self.clockNode.setText('10')
        self.clock = self.trolleyStation.attachNewNode(self.clockNode)
        self.clock.setBillboardAxis()
        self.clock.setPosHprScale(15.86, 13.82, 11.68, -0.0, 0.0, 0.0, 3.02, 3.02, 3.02)
        if ts < self.trolleyCountdownTime:
            self.countdown(self.trolleyCountdownTime - ts)

    def timerTask(self, task):
        countdownTime = int(task.duration - task.time)
        timeStr = str(countdownTime)
        if self.clockNode.getText() != timeStr:
            self.clockNode.setText(timeStr)
        if task.time >= task.duration:
            self.disableExitButton()
            self.exitWaitCountdown()
            self.enterLeaving()
            return Task.done
        else:
            return Task.cont

    def countdown(self, duration):
        countdownTask = Task(self.timerTask)
        countdownTask.duration = duration
        taskMgr.remove('trolleyTimerTask')
        return taskMgr.add(countdownTask, 'trolleyTimerTask')

    def exitWaitCountdown(self):
        taskMgr.remove('trolleyTimerTask')
        self.clock.removeNode()
        del self.clock
        del self.clockNode

    def enableExitButton(self):
        self.exitButton = DirectButton(relief=None, text=TTLocalizer.TrolleyHopOff, text_fg=(1, 1, 0.65, 1), text_pos=(0, -0.23), text_scale=TTLocalizer.TexitButton, image=(self.upButton, self.downButton, self.rolloverButton), image_color=(1, 0, 0, 1), image_scale=(20, 1, 11), pos=(0, 0, 0.8), scale=0.15, command=self.emptySlot, extraArgs=[0])
        return

    def disableExitButton(self):
        self.exitButton.destroy()

    def enterLeaving(self):
        self.trolleyExitTrack.start()
        camera.posHprInterval(3, (0, 18.55, 3.75), (-180, 0, 0), blendType='easeInOut').start()
        self.acceptOnce('playMinigame', self.handleEnterMinigame)

    def exitLeaving(self):
        self.trolleyExitTrack.finish()

    def handleEnterMinigame(self):
        base.localAvatar.setAnimState('neutral')
        base.cr.playGame.enterRandomMinigame()

    def animateTrolley(self, t, keyAngle, wheelAngle):
        for i in range(self.numKeys):
            key = self.keys[i]
            ref = self.keyRef[i]
            key.setH(ref, t * keyAngle)

        for i in range(self.numFrontWheels):
            frontWheel = self.frontWheels[i]
            ref = self.frontWheelRef[i]
            frontWheel.setH(ref, t * wheelAngle)

        for i in range(self.numBackWheels):
            backWheel = self.backWheels[i]
            ref = self.backWheelRef[i]
            backWheel.setH(ref, t * wheelAngle)

    def resetAnimation(self):
        for i in range(self.numKeys):
            self.keys[i].setTransform(self.keyInit[i])

        for i in range(self.numFrontWheels):
            self.frontWheels[i].setTransform(self.frontWheelInit[i])

        for i in range(self.numBackWheels):
            self.backWheels[i].setTransform(self.backWheelInit[i])
