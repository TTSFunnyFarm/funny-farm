from panda3d.core import * # TTOff code gets a TTFF treatment, nice
import math, random
from direct.actor import Actor
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import *
from direct.showbase.DirectObject import DirectObject
from direct.showutil import Rope
from direct.task.Task import Task
from toontown.effects import Ripples
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui import TTDialog
from toontown.fishing import FishingGlobals
from toontown.toonbase import ToontownTimer

class FishingSpot(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('FishingSpot')

    def __init__(self):
        self.lastFrame = 0
        self.placedAvatar = 0
        self.isOccupied = False
        self.nodePath = None
        self.collSphere = None
        self.collNode = None
        self.collNodePath = None
        self.protSphere = None
        self.protNode = None
        self.protNodePath = None
        self.track = None
        self.madeGui = False
        self.castGui = None
        self.reelGui = None
        self.crankGui = None
        self.crankHeld = False
        self.turnCrankTask = None
        self.itemGui = None
        self.failureGui = None
        self.brokeGui = None
        self.pole = None
        self.poleNode = []
        self.ptop = None
        self.bob = None
        self.bobBobTask = None
        self.splashSound = None
        self.ripples = None
        self.gotBobSpot = 0
        self.bobSpot = None
        self.nibbleStart = 0
        self.targetSpeed = None
        self.netTime = 0.0
        self.netDistance = 0.0
        self.line = None
        self.lineSphere = None
        #self.pendingFish = 0 unused
        self.crankTime = 0
        self.crankDelta = 0
        self.casted = False
        self.currentFish = None
        self.crankedBefore = False
        self.lineStrength = 0.0
        self.fishing = False
        self.parentNodePath = render
        self.lerp = None

    def disable(self):
        self.ignore(self.uniqueName('enterFishingSpotSphere'))
        self.setOccupied(False)
        self.__hideBob()
        self.nodePath.detachNode()
        self.__unmakeGui()

    def generate(self):
        self.nodePath = NodePath(self.uniqueName('FishingSpot'))
        self.line = Rope.Rope(self.uniqueName('FishingLine'))
        self.line.setColor(1, 1, 1, 0.4)
        self.line.setTransparency(1)
        self.lineSphere = BoundingSphere(Point3(-0.6, -2, -5), 5.5)
        self.collSphere = CollisionSphere(0, 0, 0, self.getSphereRadius())
        self.collSphere.setTangible(0)
        self.collNode = CollisionNode(self.uniqueName('FishingSpotSphere'))
        self.collNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.collNode.addSolid(self.collSphere)
        self.collNodePath = self.nodePath.attachNewNode(self.collNode)
        self.protSphere = CollisionSphere(0, 0, 0, 1.5)
        self.protNode = CollisionNode(self.uniqueName('ProtectionSphere'))
        self.protNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.protNode.addSolid(self.protSphere)
        self.protNodePath = NodePath(self.protNode)
        self.protNodePath.setScale(1, 1.5, 1.5)
        self.protNodePath.setPos(0, 7, 0)
        self.nodePath.reparentTo(self.getParentNodePath())
        self.accept(self.uniqueName('enterFishingSpotSphere'), self.__handleEnterSphere)

    def uniqueName(self, string):
        return '{0}-{1}'.format(string, id(self))

    def __handleEnterSphere(self, collEntry):
        if self.isOccupied and globalClock.getFrameCount() <= self.lastFrame + 1:
            self.notify.info('Ignoring duplicate entry for avatar.')
            return None

        if base.localAvatar.hp >= 0:
            self.notify.debug("Touched fishing dock")
            self.requestEnter()
            self.setOccupied(True)

    def requestEnter(self):
        self.notify.debug("Entering fishing dock")
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.posInTopRightCorner()
        self.setOccupied(True)
        self.setMovie(FishingGlobals.EnterMovie, 0, 0, 0)
        taskMgr.remove('cancelAnimation%d' % id(self))
        taskMgr.doMethodLater(2, self.cancelAnimation, 'cancelAnimation%d' % id(self))
        self.lastFish = [None, None, None]
        self.casted = False

    def requestExit(self):
        self.notify.debug("Exited fishing dock")
        self.removeFromPierWithAnim()

    def isFishing(self):
        return self.fishing

    def hideGui(self):
        if self.madeGui:
            if self.crankHeld:
                self.releaseCrank(None)

            if self.turnCrankTask:
                taskMgr.remove(self.turnCrankTask)
                self.turnCrankTask = None

            self.castGui.detachNode()
            self.reelGui.detachNode()
            self.crankHandle.unbind(DGG.B1PRESS)
            self.crankHandle.unbind(DGG.B1RELEASE)
            self.itemGui.detachNode()
            self.failureGui.detachNode()
            self.brokeGui.detachNode()

    def __makeGui(self):
        self.notify.debug("Making fishing gui")
        if self.madeGui:
            return None

        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**/InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        buttonModels.removeNode()
        crankModels = loader.loadModel('phase_4/models/gui/fishing_crank')
        crank = crankModels.find('**/fishing_crank')
        crankArrow = crankModels.find('**/fishing_crank_arrow')
        crankModels.removeNode()
        jarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')
        jarImage = jarGui.find('**/Jar')
        jarGui.removeNode()
        self.castGui = NodePath('castGui')
        self.exitButton = DirectButton(parent = self.castGui, relief = None, text = TTLocalizer.FishingExit, text_fg = (1, 1, 0.6, 1), text_pos = (0, -0.23), text_scale = 0.8, image = (upButton, downButton, rolloverButton), image_color = (1, 0, 0, 1), image_scale = (15, 1, 11), pos = (-0.2, 0, -0.8), scale = 0.12, command = self.__userExit)
        self.castButton = DirectButton(parent = self.castGui, relief = None, text = TTLocalizer.FishingCast, text_fg = (1, 1, 0.6, 1), text3_fg = (0.8, 0.8, 0.8, 1), text_pos = (0, -0.23), text_scale = 0.8, image = (upButton, downButton, rolloverButton), image_color = (1, 0, 0, 1), image3_color = (0.8, 0.5, 0.5, 1), image_scale = (15, 1, 11), pos = (-0.2, 0, -0.62), scale = 0.12, command = self.__userCast)
        self.jar = DirectLabel(parent = self.castGui, relief = None, text = str(base.localAvatar.getMoney()), text_scale = 0.2, text_fg = (0.95, 0.95, 0, 1), text_shadow = (0, 0, 0, 1), text_pos = (0, -0.1, 0), text_font = ToontownGlobals.getSignFont(), image = jarImage, pos = (-0.2, 0, -0.35), scale = 0.6)
        self.reelGui = NodePath('reelGui')
        self.reelButton = DirectButton(parent = self.reelGui, relief = None, text = TTLocalizer.FishingAutoReel, text_fg = (1, 1, 0.6, 1), text_pos = (0, -0.23), text_scale = 0.8, image = (upButton, downButton, rolloverButton), image_color = (0, 0.69, 0, 1), image_scale = (24, 1, 11), pos = (1.0, 0, -0.3), scale = 0.1, command = self.__userReel)
        self.crankGui = self.reelGui.attachNewNode('crankGui')
        arrow1 = crankArrow.copyTo(self.crankGui)
        arrow1.setColor(1, 0, 0, 1)
        arrow1.setPos(0.25, 0, -0.25)
        arrow2 = crankArrow.copyTo(self.crankGui)
        arrow2.setColor(1, 0, 0, 1)
        arrow2.setPos(-0.25, 0, 0.25)
        arrow2.setR(180)
        self.crankGui.setPos(-0.2, 0, -0.69)
        self.crankGui.setScale(0.5)
        self.crankHandle = DirectFrame(parent = self.crankGui, state = DGG.NORMAL, relief = None, image = crank)
        self.speedGauge = DirectWaitBar(parent = self.crankGui, relief = DGG.SUNKEN, frameSize = (-0.8, 0.8, -0.15, 0.15), borderWidth = (0.02, 0.02), scale = 0.42, pos = (0, 0, 0.75), barColor = (0, 0.69, 0, 1))
        self.speedGauge.hide()
        self.speedJudger = DirectLabel(parent = self.speedGauge, relief = None, text = '', scale = 0.3, pos = (0, 0, 0.5))
        self.itemGui = NodePath('itemGui')
        self.itemFrame = DirectFrame(parent = self.itemGui, relief = None, geom = DGG.getDefaultDialogGeom(), geom_color = ToontownGlobals.GlobalDialogColor, geom_scale = (1, 1, 0.5), text = TTLocalizer.FishingItemFound, text_pos = (0, 0.08), text_scale = 0.08, pos = (0, 0, 0.59))
        self.itemLabel = DirectLabel(parent = self.itemFrame, text = '', text_scale = 0.06, pos = (0, 0, -0.08))
        self.failureGui = NodePath('failureGui')
        self.failureFrame = DirectFrame(parent = self.failureGui, relief = None, geom = DGG.getDefaultDialogGeom(), geom_color = ToontownGlobals.GlobalDialogColor, geom_scale = (1.2, 1, 0.6), text = TTLocalizer.FishingFailure, text_pos = (0, 0.12), text_scale = 0.08, pos = (0, 0, 0.59))
        self.failureLabel = DirectLabel(parent = self.failureFrame, text = '', text_scale = 0.06, text_wordwrap = 16, pos = (0, 0, -0.04))
        self.brokeGui = NodePath('brokeGui')
        self.brokeFrame = DirectFrame(parent = self.brokeGui, relief = None, geom = DGG.getDefaultDialogGeom(), geom_color = ToontownGlobals.GlobalDialogColor, geom_scale = (1.2, 1, 0.6), text = TTLocalizer.FishingBrokeHeader, text_pos = (0, 0.12), text_scale = 0.08, pos = (0, 0, 0.59))
        self.brokeLabel = DirectLabel(parent = self.brokeFrame, relief = None, text = TTLocalizer.FishingBroke, text_scale = 0.06, text_wordwrap = 16, pos = (0, 0, -0.04))
        self.madeGui = True

    def __unmakeGui(self):
        if not (self.madeGui):
            return None

        self.exitButton.destroy()
        self.castButton.destroy()
        self.jar.destroy()
        self.reelButton.destroy()
        self.crankHandle.destroy()
        self.speedGauge.destroy()
        self.itemFrame.destroy()
        self.failureFrame.destroy()
        self.brokeFrame.destroy()
        self.madeGui = False

    def doCast(self):
        self.notify.debug("Cast line")
        self.timer.countdown(45, self.removeFromPierWithAnim)
        base.localAvatar.takeMoney(1, False)
        self.crankedBefore = False
        self.casted = True
        self.currentFish = None
        self.targetSpeed = None
        self.setMovie(FishingGlobals.CastMovie, 0, 0, 0)
        taskMgr.doMethodLater(random.randrange(FishingGlobals.NibbleMinWait, FishingGlobals.NibbleMaxWait), self.startNibble, 'nibble-%d' % id(self))

    def doAutoReel(self):
        return # todo?

    def doReel(self, speed, netTime, netDistance):
        self.notify.debug("Reeling")
        self.timer.countdown(45, self.removeFromPierWithAnim)
        if not self.crankedBefore:
            self.crankedBefore = True
            self.setMovie(FishingGlobals.BeginReelMovie, 0, 0, speed)
            #taskMgr.remove('nibbleDone-%d' % id(self))
            #taskMgr.doMethodLater(FishingGlobals.PostNibbleWait, self.nibbleDone, 'nibbleDone%d' % id(self))
        else:
            self.setMovie(FishingGlobals.ContinueReelMovie, 0, 0, speed)

    def getSphereRadius(self):
        return FishingGlobals.SphereRadius

    def setParentNodePath(self, np):
        self.parentNodePath = np

    def getParentNodePath(self):
        return self.parentNodePath

    def setPosHpr(self, x, y, z, h, p, r):
        self.nodePath.setPosHpr(x, y, z, h, p, r)

    def setOccupied(self, isOccupied):
        self.notify.debug("Setting occupied to {0}".format(isOccupied))
        if self.isOccupied == isOccupied:
            return # already occupied/deoccupied!
        if self.track:
            if self.track.isPlaying():
                self.track.finish()
            self.track = None
        self.isOccupied = isOccupied
        self.__hideLine()
        self.lastFrame = globalClock.getFrameCount()
        if not self.isOccupied:
            base.localAvatar.setBlend(animBlend = False)
            base.localAvatar.setPlayRate(1.0, 'cast')
            self.__dropPole()
            base.localAvatar.loop('neutral')
            base.localAvatar.wrtReparentTo(render)
            self.__hideBob()
            base.localAvatar.fishingSpot = None
            self.placedAvatar = 0
            self.collSphere.setTangible(0)
            self.protNodePath.detachNode()
            base.localAvatar.enable()
        else:
            self.collSphere.setTangible(1)
            self.protNodePath.reparentTo(self.nodePath)
            self.__loadStuff()
            base.setCellsAvailable([
                base.bottomCells[1],
                base.bottomCells[2]], 0)
            self.placedAvatar = 0
            base.localAvatar.wrtReparentTo(self.nodePath)
            base.localAvatar.fishingSpot = self
            base.localAvatar.setAnimState('neutral', 1.0)
            self.__setupNeutralBlend()
            self.hideGui()
            base.setCellsAvailable([
                base.bottomCells[1],
                base.bottomCells[2]], 1
            )
            base.localAvatar.disable()
        return

    def __avatarGone(self):
        self.setOccupied(False)

    def __setupNeutralBlend(self):
        base.localAvatar.stop()
        base.localAvatar.loop('neutral')
        base.localAvatar.setBlend(animBlend = True)
        base.localAvatar.pose('cast', 0)
        base.localAvatar.setControlEffect('neutral', 0.2)
        base.localAvatar.setControlEffect('cast', 0.8)

    def setTargetSpeed(self, speed):
        self.notify.debug("Got target speed: {0}".format(speed))
        self.targetSpeed = speed
        if self.isOccupied:
            self.__updateSpeedGauge()

    def getTargetSpeed(self):
        return self.targetSpeed

    def setGaugeVal(self, val):
        self.speedGauge['value'] = val

    def setMovie(self, mode, code, item, speed):
        self.notify.debug("setMovie {0} {1} {2} {3}".format(mode, code, item, speed))
        if self.track:
            if self.track.isPlaying():
                self.track.finish()
            self.track = None

        self.__hideLine()
        if mode == FishingGlobals.NoMovie:
            return
        if mode == FishingGlobals.EnterMovie:
            self.track = Parallel()
            base.localAvatar.stopLookAround()
            if self.isOccupied:
                self.track.append(LerpPosHprInterval(nodePath = camera, other = base.localAvatar, duration = 1.5, pos = Point3(14, -7.4, 7.3), hpr = VBase3(45, -12, 0), blendType = 'easeInOut'))
            base.localAvatar.setBlend(animBlend = False)
            base.localAvatar.setPlayRate(1.0, 'walk')
            base.localAvatar.loop('walk')
            toonTrack = Sequence(LerpPosHprInterval(base.localAvatar, 1.5, Point3(0, 0, 0), Point3(0, 0, 0)),
                Func(self.__setupNeutralBlend),
                Func(self.__holdPole),
                Parallel(ActorInterval(base.localAvatar, 'cast', playRate = 0.5, duration = 27.0 / 12.0), ActorInterval(self.pole, 'cast', playRate = 0.5, duration = 27.0 / 12.0), LerpScaleInterval(self.pole, 1.0, 1.0, startScale = 0.01)),
                Func(base.localAvatar.pose, 'cast', 88), Func(self.pole.pose, 'cast', 88))
            if self.isOccupied:
                toonTrack.append(Func(self.showCastGui))
            self.track.append(toonTrack)
            self.track.start()
            self.timer.countdown(45, self.removeFromPierWithAnim)
        elif mode == FishingGlobals.ExitMovie:
            if self.isOccupied:
                self.hideGui()
            base.localAvatar.stopLookAround()
            base.localAvatar.startLookAround()
            self.__placeAvatar()
            self.__hideLine()
            self.__hideBob()
            self.track = Sequence(Parallel(ActorInterval(base.localAvatar, 'cast', duration = 1.0, startTime = 1.0, endTime = 0.0), ActorInterval(self.pole, 'cast', duration = 1.0, startTime = 1.0, endTime = 0.0), LerpScaleInterval(self.pole, duration = 0.5, scale = 0.01, startScale = 1.0)), Func(self.__dropPole))
            self.track.start()
        elif mode == FishingGlobals.CastMovie:
            base.localAvatar.stopLookAround()
            base.localAvatar.startLookAround()
            self.__placeAvatar()
            self.__getBobSpot()
            self.track = Sequence(Parallel(ActorInterval(base.localAvatar, 'cast', duration = 2.0, startTime = 1.0), ActorInterval(self.pole, 'cast', duration = 2.0, startTime = 1.0), Sequence(Wait(1.3), Func(self.__showBobCast), Func(self.__showLineWaiting), LerpPosInterval(self.bob, 0.2, self.bobSpot), Func(self.__showBob), SoundInterval(self.splashSound))))
            if self.isOccupied:
                self.track.append(Func(self.__showReelGui))

            self.track.start()
        elif mode == FishingGlobals.NibbleMovie:
            self.__placeAvatar()
            base.localAvatar.pose('cast', 71)
            self.pole.pose('cast', 71)
            self.__showLineWaiting()
            self.__nibbleBob()
        elif mode == FishingGlobals.BeginReelMovie:
            base.localAvatar.stopLookAround()
            self.__placeAvatar()
            self.__hideBob()
            self.__showLineReelTaught()
            base.localAvatar.setPlayRate(speed, 'cast')
            self.pole.setPlayRate(speed, 'cast')
            self.track = Sequence(Parallel(ActorInterval(base.localAvatar, 'cast', duration = 1.0 / speed, startTime = 3.0 / speed, playRate = speed), ActorInterval(self.pole, 'cast', duration = 1.0 / speed, startTime = 3.0 / speed, playRate = speed)), Func(base.localAvatar.loop, 'cast', 1, None, 57, 65), Func(self.pole.loop, 'cast', 1, None, 96, 126))
            self.track.start()
        elif mode == FishingGlobals.ContinueReelMovie:
            base.localAvatar.stopLookAround()
            self.__showLineReelTaught()
            if not (self.placedAvatar):
                self.__placeAvatar()
                base.localAvatar.pose('cast', 88)
                self.pole.pose('cast', 88)

            if speed < 0:
                base.localAvatar.loop('cast', restart = 0, fromFrame = 65, toFrame = 57)
                self.pole.loop('cast', restart = 0, fromFrame = 126, toFrame = 88)
            else:
                base.localAvatar.loop('cast', restart = 0, fromFrame = 57, toFrame = 65)
                self.pole.loop('cast', restart = 0, fromFrame = 88, toFrame = 126)
            base.localAvatar.setPlayRate(speed/2, 'cast')
            self.pole.setPlayRate(speed/2, 'cast')
        elif mode == FishingGlobals.PullInMovie:
            base.localAvatar.startLookAround()
            self.__placeAvatar()
            self.__hideBob()
            base.localAvatar.setPlayRate(1, 'cast')
            self.pole.setPlayRate(1, 'cast')
            base.localAvatar.pose('cast', 94)
            self.pole.pose('cast', 94)
            if self.isOccupied:
                self.showCastGui()
                if code == FishingGlobals.QuestItem:
                    self.__showQuestItem(item)
                elif code == FishingGlobals.FishItem:
                    self.__showFishItem(item)
                elif code == FishingGlobals.OverLimitFishItem:
                    self.hideGui()
                    self.b_fishReleaseQuery(item)
                else:
                    self.showFailureReason(code)

        return None

    def getStareAtNodeAndOffset(self):
        return (self.nodePath, Point3())

    def __loadStuff(self):
        if not self.pole:
            self.pole = Actor.Actor()
            self.pole.loadModel('phase_4/models/props/fishing-pole-mod')
            self.pole.setBlend(frameBlend = config.GetBool('interpolate-animations', True))
            self.pole.loadAnims({'cast': 'phase_4/models/props/fishing-pole-chan'})
            self.pole.pose('cast', 0)
            self.ptop = self.pole.find('**/joint_attachBill')

        if not self.bob:
            self.bob = loader.loadModel('phase_4/models/props/fishing_bob')
            self.ripples = Ripples.Ripples(self.nodePath)
            self.ripples.hide()

        if not self.splashSound:
            self.splashSound = base.loader.loadSfx('phase_4/audio/sfx/TT_splash1.ogg')

    def __placeAvatar(self):
        if not (self.placedAvatar):
            self.placedAvatar = 1
            self.__holdPole()
            self.__setupNeutralBlend()
            base.localAvatar.setPosHpr(0, 0, 0, 0, 0, 0)

    def __holdPole(self):
        if self.poleNode != []:
            self.__dropPole()

        np = NodePath('pole-holder')
        hands = base.localAvatar.getRightHands()
        for h in hands:
            self.poleNode.append(np.instanceTo(h))

        self.pole.reparentTo(self.poleNode[0])

    def __dropPole(self):
        self.__hideBob()
        self.__hideLine()
        if self.pole:
            self.pole.clearMat()
            self.pole.detachNode()

        for pn in self.poleNode:
            pn.removeNode()

        self.poleNode = []

    def __showLineWaiting(self):
        self.line.setup(4, ((None, (0, 0, 0)), (None, (0, -2, -4)), (self.bob, (0, -1, 0)), (self.bob, (0, 0, 0))))
        self.line.ropeNode.setBounds(self.lineSphere)
        self.line.reparentTo(self.ptop)

    def __showLineReelTaught(self):
        self.__getBobSpot()
        self.line.setup(2, ((None, (0, 0, 0)), (self.nodePath, self.bobSpot)))
        self.line.ropeNode.setBounds(self.lineSphere)
        self.line.reparentTo(self.ptop)

    def __showLineReelSlack(self):
        self.__getBobSpot()
        self.line.setup(3, ((None, (0, 0, 0)), (None, (0, -2, -4)), (self.nodePath, self.bobSpot)))
        self.line.ropeNode.setBounds(self.lineSphere)
        self.line.reparentTo(self.ptop)

    def __hideLine(self):
        self.line.detachNode()

    def __showBobCast(self):
        self.__hideBob()
        self.bob.reparentTo(self.nodePath)
        base.localAvatar.update(0)
        self.bob.setPos(self.ptop, 0, 0, 0)

    def __showBob(self):
        self.__hideBob()
        self.__getBobSpot()
        self.bob.reparentTo(self.nodePath)
        self.bob.setPos(self.bobSpot)
        self.ripples.stop()
        self.ripples.setPos(self.bobSpot)
        self.ripples.play(0.75)
        self.bobBobTask = taskMgr.add(self.__doBobBob, self.uniqueName('bob'))

    def __nibbleBob(self):
        self.__hideBob()
        self.__getBobSpot()
        self.bob.reparentTo(self.nodePath)
        self.bob.setPos(self.bobSpot)
        self.ripples.stop()
        self.ripples.setPos(self.bobSpot)
        self.ripples.play()
        self.nibbleStart = globalClock.getFrameTime()
        self.bobBobTask = taskMgr.add(self.__doNibbleBob, self.uniqueName('bob'))

    def __hideBob(self):
        if self.bob:
            self.bob.detachNode()
        if self.bobBobTask:
            taskMgr.remove(self.bobBobTask)
            self.bobBobTask = None
        if self.ripples:
            self.ripples.stop()

    def __doBobBob(self, task):
        now = globalClock.getFrameTime()
        z = math.sin(now) * 0.5
        self.bob.setZ(self.bobSpot[2] + z)
        return Task.cont

    def __doNibbleBob(self, task):
        now = globalClock.getFrameTime()
        elapsed = now - self.nibbleStart
        if elapsed > FishingGlobals.NibbleTime:
            self.__showBob()
            return Task.done

        x = (elapsed / FishingGlobals.NibbleTime + 1.0) * 0.5
        y = math.sin(x * math.pi)
        amplitude = y * y * y * 0.2
        nibbleEffect = math.sin(now * 12) * amplitude
        z = math.sin(now) * 0.5 + nibbleEffect
        self.bob.setZ(self.bobSpot[2] + z)
        return Task.cont

    def __userExit(self):
        self.hideGui()
        self.requestExit()

    def __userReel(self):
        self.hideGui()
        self.doAutoReel()

    def __userCast(self):
        self.itemGui.detachNode()
        self.failureGui.detachNode()
        if base.localAvatar.getMoney() > 0:
            self.__hideCastButtons()
            self.doCast()
            self.jar['text'] = str(base.localAvatar.getMoney())
        else:
            self.__showBroke()

    def showCastGui(self):
        self.notify.debug("Showing cast buttons")
        self.hideGui()
        self.__makeGui()
        self.castButton.show()
        self.exitButton.show()
        self.castGui.reparentTo(aspect2d)
        self.castButton['state'] = DGG.NORMAL
        self.jar['text'] = str(base.localAvatar.getMoney())

    def __hideCastButtons(self):
        self.castButton.hide()
        self.exitButton.hide()

    def __showReelGui(self):
        self.notify.debug("Showing reel")
        self.hideGui()
        self.__makeGui()
        self.reelGui.reparentTo(aspect2d)
        self.crankGui.show()
        self.speedGauge.hide()
        self.crankHandle.bind(DGG.B1PRESS, self.clickCrank)
        self.crankHandle.bind(DGG.B1RELEASE, self.releaseCrank)
        self.reelButton.hide()
        self.netTime = 0.0
        self.netDistance = 0.0
        self.targetSpeed = None

    def clickCrank(self, param):
        if self.crankHeld:
            self.__releaseCrank(param)

        self.reelButton.hide()
        self.crankHeld = True
        self.doReel(1.0, self.netTime, self.netDistance)
        mw = base.mouseWatcherNode
        mpos = (mw.getMouseX(), mw.getMouseY())
        angle = self.__getMouseAngleToCrank(mpos[0], mpos[1])
        self.crankHandle.setR(angle)
        self.crankAngle = angle
        self.crankDelta = 0
        if not self.turnCrankTask:
            self.turnCrankTask = taskMgr.add(self.__turnCrank, self.uniqueName('turnCrank'))

    def releaseCrank(self, unused):
        if not self.crankHeld:
            return

        self.crankHeld = False
        if self.isFishing():
            #self.__updateCrankSpeed(1)
            pass

    def __turnCrank(self, task):
        if self.crankHeld and base.mouseWatcherNode.hasMouse():
            mx = base.mouseWatcherNode.getMouseX()
            my = base.mouseWatcherNode.getMouseY()
            angle = self.__getMouseAngleToCrank(mx, my)
            #if self.crankHandle.getR() >= 360:
                #self.crankHandle.setR(0)
            old = self.crankHandle.getR()
            self.crankHandle.setR(angle)
            if self.isFishing():
                if not self.crankTime:
                    self.crankTime = globalClock.getFrameTime()
                delta = self.crankHandle.getR() - old
                delta = abs(delta)
                print(delta)
                print(globalClock.getFrameTime() -self.crankTime)
                old = self.lineStrength
                self.lineStrength += delta / (globalClock.getFrameTime() - self.crankTime)
                if self.lineStrength > 100:
                    self.lineStrength = 100


        return Task.cont

    def startFishing(self):
        self.fishing = True
        self.speedGauge.show()
        self.speedJudger.show()
        taskMgr.doMethodLater(0.05, self.updateThings, 'update-%d' % id(self))

    def stopFishing(self):
        #self.lineStrength = 0.0
        self.crankTime = 0
        self.fishing = False

    def updateThings(self, task):
        if not self.isFishing():
            return task.done
        old = self.lineStrength
        self.lineStrength -= self.getTargetSpeed()
        if self.lineStrength < 0:
            self.lineStrength = 0
        self.__updateSpeedGauge()
        if self.isFishing():
            return task.again

    def __updateSpeedGauge(self):
        now = globalClock.getFrameTime()
        #if self.crankTime < 0:
            #self.crankTime = now
        elapsed = now - self.crankTime
        degreesPerSecond = 0
        speed = 0
        avgSpeed = 0
        #if self.crankDelta != 0:
            #print(self.lineStrength)
        if self.isFishing():
            #print(avgSpeed, self.targetSpeed)
            #print(pctDiff)
            self.speedGauge['value'] = self.lineStrength
            if self.lineStrength >= 65:
                self.speedJudger.setText(TTLocalizer.FishingCrankTooFast)
            elif self.lineStrength <= 35:
                self.speedJudger.setText(TTLocalizer.FishingCrankTooSlow)
            else:
                self.speedJudger.setText("Just right!")

    def __getMouseAngleToCrank(self, x, y):
        p = self.crankGui.getRelativePoint(NodePath(), Point3(x, 0, y))
        angle = math.atan2(p[2], p[0]) * 180.0 / math.pi
        return angle

    def __showFishItem(self, itemId):
        self.__makeGui()
        itemName = FishingGlobals.getFishName(itemId)
        itemValue = int(FishingGlobals.FishValues[itemId] * self.targetSpeed)
        self.itemLabel['text'] = '{0}\nValue: {1} jellybean{2}'.format(itemName, itemValue, '' if itemValue == 1 else 's')
        #self.jar['text'] = str(min(base.localAvatar.getMoney() + itemValue, base.localAvatar.getMaxMoney()))
        self.itemGui.reparentTo(aspect2d)

    def showFailureReason(self, code):
        self.__makeGui()
        reason = ''
        if code == FishingGlobals.TooSoon:
            reason = TTLocalizer.FishingFailureTooSoon
        elif code == FishingGlobals.TooLate:
            reason = TTLocalizer.FishingFailureTooLate
        elif code == FishingGlobals.AutoReel:
            reason = TTLocalizer.FishingFailureAutoReel
        elif code == FishingGlobals.TooSlow:
            reason = TTLocalizer.FishingFailureTooSlow
        elif code == FishingGlobals.TooFast:
            reason = TTLocalizer.FishingFailureTooFast

        self.failureLabel['text'] = reason
        self.failureGui.reparentTo(aspect2d)

    def showBroke(self):
        self.__makeGui()
        self.brokeGui.reparentTo(aspect2d)
        self.castButton['state'] = DGG.DISABLED

    def __getBobSpot(self):
        if self.gotBobSpot:
            return None

        startSpot = (0, 8, 5)
        ray = CollisionRay(startSpot[0], startSpot[1], startSpot[2], 0, 0, -1)
        rayNode = CollisionNode('BobRay')
        rayNode.setCollideMask(BitMask32.allOff())
        rayNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        rayNode.addSolid(ray)
        rayNodePath = self.nodePath.attachNewNode(rayNode)
        cqueue = CollisionHandlerQueue()

        try:
            world = base.cr.playGame.hood.place.loader.geom
        except:
            world = None

        if world:
            trav = CollisionTraverser()
            trav.addCollider(rayNodePath, cqueue)
            trav.traverse(world)

        rayNodePath.removeNode()
        cqueue.sortEntries()
        if cqueue.getNumEntries() == 0:
            self.notify.debug("Couldn't find bob spot for %d" % id(self))
            self.bobSpot = Point3(startSpot[0], startSpot[1], 0)
        else:
            entry = cqueue.getEntry(0)
            self.bobSpot = Point3(entry.getInteriorPoint(self.nodePath))
        self.gotBobSpot = 1

    def b_fishReleaseQuery(self, fish):
        pass

    def fishReleaseQuery(self, fish):
        pass # todo?

    def fishReleased(self, fish):
        # todo?
        self.showCastGui()

    def cancelAnimation(self, task = None):
        self.notify.debug("Cancelling animation")
        self.setMovie(FishingGlobals.NoMovie, 0, 0, 0)

    def removeFromPierWithAnim(self, task = None):
        taskMgr.remove('cancelAnimation%d' % id(self))
        self.setMovie(FishingGlobals.ExitMovie, 0, 0, 0)
        taskMgr.doMethodLater(1, self.removeFromPier, 'remove%d' % id(self))

    def removeFromPier(self, task = None):
        self.uncast()
        self.timer.destroy()
        self.cancelAnimation()
        self.setOccupied(False)

    def startNibble(self, task):
        numFish = len(TTLocalizer.ClassicFishNames)
        self.setTargetSpeed(round(random.uniform(1.0, 3.0), 3))
        self.currentFish = random.randrange(0, numFish)
        self.notify.debug('A {0} with speed {1} bit our line.'.format(TTLocalizer.ClassicFishNames[self.currentFish][0], self.targetSpeed))
        self.setMovie(FishingGlobals.NibbleMovie, 0, 0, 0)
        taskMgr.doMethodLater(FishingGlobals.NibbleTime, self.finishNibble, 'nibbleDone-%d' % id(self))
        self.startFishing()
        return Task.done

    def finishNibble(self, task):
        print("HIII??")
        self.stopFishing()
        self.uncast()
        #if avgSpeed == 0:
            #self.setMovie(FishingGlobals.PullInMovie, FishingGlobals.TooLate, 0, 0)
            #return Task.done
        pctDiff = self.lineStrength
        self.lineStrength = 0.0
        self.notify.debug('pctDiff: {0}, avgSpeed: {1}'.format(pctDiff, avgSpeed))
        print("LOLLL",  pctDiff)
        if pctDiff >= 65:
            self.setMovie(FishingGlobals.PullInMovie, FishingGlobals.TooFast, 0, 0)
        elif pctDiff <= 35:
            self.setMovie(FishingGlobals.PullInMovie, FishingGlobals.TooSlow, 0, 0)
        else:
            self.setMovie(FishingGlobals.PullInMovie, FishingGlobals.FishItem, self.currentFish, 0)
            base.localAvatar.addMoney(int(FishingGlobals.FishValues[self.currentFish] * self.targetSpeed))
            self.jar['text'] = str(base.localAvatar.getMoney())
        self.currentFish = None
        return Task.done

    def uncast(self):
        self.casted = False
        taskMgr.remove('nibble-%d' % id(self))
        taskMgr.remove('nibbleDone-%d' % id(self))
