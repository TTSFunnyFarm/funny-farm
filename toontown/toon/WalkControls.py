from panda3d.core import *
from direct.showbase.PythonUtil import *
from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.showbase.InputStateGlobal import inputState
from direct.controls.GhostWalker import GhostWalker
from direct.controls.GravityWalker import GravityWalker
from direct.controls.ObserverWalker import ObserverWalker
from direct.controls.PhysicsWalker import PhysicsWalker
from direct.controls.SwimWalker import SwimWalker
from direct.controls.TwoDWalker import TwoDWalker
from direct.controls import ControlManager
from otp.otpbase import OTPGlobals
import math

class WalkControls(DirectObject):
    notify = directNotify.newCategory('WalkControls')
    wantDevCameraPositions = 0
    movingNeutral, movingForward = (False, False)
    movingRotation, movingBackward = (False, False)
    movingJumping = False

    def __init__(self):
        self.isPageUp = 0
        self.isPageDown = 0
        self.fov = OTPGlobals.DefaultCameraFov
        self.cTrav = CollisionTraverser('base.cTrav')
        base.pushCTrav(self.cTrav)
        self.cTrav.setRespectPrevTransform(1)
        self.avatarControlsEnabled = 0
        self.controlManager = ControlManager.ControlManager(True, False)
        self.soundWalk = base.loader.loadSfx('phase_3.5/audio/sfx/AV_footstep_walkloop.ogg')
        self.soundRun = base.loader.loadSfx('phase_3.5/audio/sfx/AV_footstep_runloop.ogg')

    def delete(self):
        self.ignoreAll()
        base.popCTrav()
        self.stopUpdateSmartCamera()
        self.shutdownSmartCamera()
        self.disableAvatarControls()
        self.controlManager.delete()
        self.physControls = None
        del self.controlManager
        del self.soundRun
        del self.soundWalk

    def useSwimControls(self):
        self.controlManager.use('swim', self)
        self.soundRun.stop()
        self.soundWalk.stop()

    def useGhostControls(self):
        self.controlManager.use('ghost', self)

    def useWalkControls(self):
        self.controlManager.use('walk', self)

    def useTwoDControls(self):
        self.controlManager.use('twoD', self)

    def wantLegacyLifter(self):
        return False

    def setupCamera(self):
        base.disableMouse()
        camera.reparentTo(self)
        camera.setPos(0, -6.5 - max(self.height, 3.0), (self.height * (1.0/3.0)) + 2.2)
        camera.setHpr(0, 0, 0)
        base.camLens.setMinFov(OTPGlobals.DefaultCameraFov/(4./3.))

    def setupSmartCamera(self):
        self.initializeSmartCamera()
        self.startUpdateSmartCamera()

    def setupControls(self, avatarRadius = 1.4, floorOffset = OTPGlobals.FloorOffset, reach = 4.0, wallBitmask = OTPGlobals.WallBitmask, floorBitmask = OTPGlobals.FloorBitmask, ghostBitmask = OTPGlobals.GhostBitmask):
        walkControls = GravityWalker(legacyLifter=self.wantLegacyLifter())
        walkControls.setWallBitMask(wallBitmask)
        walkControls.setFloorBitMask(floorBitmask)
        walkControls.initializeCollisions(self.cTrav, self, avatarRadius, floorOffset, reach)
        walkControls.setAirborneHeightFunc(self.getAirborneHeight)
        self.controlManager.add(walkControls, 'walk')
        self.physControls = walkControls
        twoDControls = TwoDWalker()
        twoDControls.setWallBitMask(wallBitmask)
        twoDControls.setFloorBitMask(floorBitmask)
        twoDControls.initializeCollisions(self.cTrav, self, avatarRadius, floorOffset, reach)
        twoDControls.setAirborneHeightFunc(self.getAirborneHeight)
        self.controlManager.add(twoDControls, 'twoD')
        swimControls = SwimWalker()
        swimControls.setWallBitMask(wallBitmask)
        swimControls.setFloorBitMask(floorBitmask)
        swimControls.initializeCollisions(self.cTrav, self, avatarRadius, floorOffset, reach)
        swimControls.setAirborneHeightFunc(self.getAirborneHeight)
        self.controlManager.add(swimControls, 'swim')
        ghostControls = GhostWalker()
        ghostControls.setWallBitMask(ghostBitmask)
        ghostControls.setFloorBitMask(floorBitmask)
        ghostControls.initializeCollisions(self.cTrav, self, avatarRadius, floorOffset, reach)
        ghostControls.setAirborneHeightFunc(self.getAirborneHeight)
        self.controlManager.add(ghostControls, 'ghost')
        observerControls = ObserverWalker()
        observerControls.setWallBitMask(ghostBitmask)
        observerControls.setFloorBitMask(floorBitmask)
        observerControls.initializeCollisions(self.cTrav, self, avatarRadius, floorOffset, reach)
        observerControls.setAirborneHeightFunc(self.getAirborneHeight)
        self.controlManager.add(observerControls, 'observer')
        self.controlManager.use('walk', self)
        self.setWalkSpeedNormal()
        self.enableAvatarControls()
        # We're not initializing the smart camera right away anymore because it creates bugs with the tutorial.

    def enableAvatarControls(self):
        if self.avatarControlsEnabled:
            return
        self.avatarControlsEnabled = 1
        self.controlManager.enable()
        base.taskMgr.add(self.handleAnimation, 'AnimationHandler')
        self.setupCamera()

    def disableAvatarControls(self):
        if not self.avatarControlsEnabled:
            return
        self.avatarControlsEnabled = 0
        self.controlManager.disable()
        base.taskMgr.remove('AnimationHandler')
        self.stopSound()

    def initializeSmartCameraCollisions(self):
        self.ccTrav = CollisionTraverser('LocalToon.ccTrav')
        self.ccLine = CollisionSegment(0.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        self.ccLineNode = CollisionNode('ccLineNode')
        self.ccLineNode.addSolid(self.ccLine)
        self.ccLineNodePath = self.attachNewNode(self.ccLineNode)
        self.ccLineBitMask = OTPGlobals.CameraBitmask
        self.ccLineNode.setFromCollideMask(self.ccLineBitMask)
        self.ccLineNode.setIntoCollideMask(BitMask32.allOff())
        self.camCollisionQueue = CollisionHandlerQueue()
        self.ccTrav.addCollider(self.ccLineNodePath, self.camCollisionQueue)
        self.ccSphere = CollisionSphere(0, 0, 0, 1)
        self.ccSphereNode = CollisionNode('ccSphereNode')
        self.ccSphereNode.addSolid(self.ccSphere)
        self.ccSphereNodePath = camera.attachNewNode(self.ccSphereNode)
        self.ccSphereNode.setFromCollideMask(OTPGlobals.CameraBitmask)
        self.ccSphereNode.setIntoCollideMask(BitMask32.allOff())
        self.camPusher = CollisionHandlerPusher()
        self.camPusher.addCollider(self.ccSphereNodePath, camera)
        self.camPusher.setCenter(self)
        self.ccPusherTrav = CollisionTraverser('LocalToon.ccPusherTrav')
        self.ccSphere2 = self.ccSphere
        self.ccSphereNode2 = CollisionNode('ccSphereNode2')
        self.ccSphereNode2.addSolid(self.ccSphere2)
        self.ccSphereNodePath2 = camera.attachNewNode(self.ccSphereNode2)
        self.ccSphereNode2.setFromCollideMask(OTPGlobals.CameraBitmask)
        self.ccSphereNode2.setIntoCollideMask(BitMask32.allOff())
        self.camPusher2 = CollisionHandlerPusher()
        self.ccPusherTrav.addCollider(self.ccSphereNodePath2, self.camPusher2)
        self.camPusher2.addCollider(self.ccSphereNodePath2, camera)
        self.camPusher2.setCenter(self)
        self.camFloorRayNode = self.attachNewNode('camFloorRayNode')
        self.ccRay = CollisionRay(0.0, 0.0, 0.0, 0.0, 0.0, -1.0)
        self.ccRayNode = CollisionNode('ccRayNode')
        self.ccRayNode.addSolid(self.ccRay)
        self.ccRayNodePath = self.camFloorRayNode.attachNewNode(self.ccRayNode)
        self.ccRayBitMask = OTPGlobals.FloorBitmask
        self.ccRayNode.setFromCollideMask(self.ccRayBitMask)
        self.ccRayNode.setIntoCollideMask(BitMask32.allOff())
        self.ccTravFloor = CollisionTraverser('LocalToon.ccTravFloor')
        self.camFloorCollisionQueue = CollisionHandlerQueue()
        self.ccTravFloor.addCollider(self.ccRayNodePath, self.camFloorCollisionQueue)
        self.ccTravOnFloor = CollisionTraverser('LocalToon.ccTravOnFloor')
        self.ccRay2 = CollisionRay(0.0, 0.0, 0.0, 0.0, 0.0, -1.0)
        self.ccRay2Node = CollisionNode('ccRay2Node')
        self.ccRay2Node.addSolid(self.ccRay2)
        self.ccRay2NodePath = self.camFloorRayNode.attachNewNode(self.ccRay2Node)
        self.ccRay2BitMask = OTPGlobals.FloorBitmask
        self.ccRay2Node.setFromCollideMask(self.ccRay2BitMask)
        self.ccRay2Node.setIntoCollideMask(BitMask32.allOff())
        self.ccRay2MoveNodePath = hidden.attachNewNode('ccRay2MoveNode')
        self.camFloorCollisionBroadcaster = CollisionHandlerFloor()
        self.camFloorCollisionBroadcaster.setInPattern('on-floor')
        self.camFloorCollisionBroadcaster.setOutPattern('off-floor')
        self.camFloorCollisionBroadcaster.addCollider(self.ccRay2NodePath, self.ccRay2MoveNodePath)

    def deleteSmartCameraCollisions(self):
        del self.ccTrav
        del self.ccLine
        del self.ccLineNode
        self.ccLineNodePath.removeNode()
        del self.ccLineNodePath
        del self.camCollisionQueue
        del self.ccRay
        del self.ccRayNode
        self.ccRayNodePath.removeNode()
        del self.ccRayNodePath
        del self.ccRay2
        del self.ccRay2Node
        self.ccRay2NodePath.removeNode()
        del self.ccRay2NodePath
        self.ccRay2MoveNodePath.removeNode()
        del self.ccRay2MoveNodePath
        del self.ccTravOnFloor
        del self.ccTravFloor
        del self.camFloorCollisionQueue
        del self.camFloorCollisionBroadcaster
        del self.ccSphere
        del self.ccSphereNode
        self.ccSphereNodePath.removeNode()
        del self.ccSphereNodePath
        del self.camPusher
        del self.ccPusherTrav
        del self.ccSphere2
        del self.ccSphereNode2
        self.ccSphereNodePath2.removeNode()
        del self.ccSphereNodePath2
        del self.camPusher2

    def setWalkSpeedNormal(self):
        self.controlManager.setSpeeds(OTPGlobals.ToonForwardSpeed, OTPGlobals.ToonJumpForce, OTPGlobals.ToonReverseSpeed, OTPGlobals.ToonRotateSpeed)

    def setWalkSpeedSlow(self):
        self.controlManager.setSpeeds(OTPGlobals.ToonForwardSlowSpeed, OTPGlobals.ToonJumpSlowForce, OTPGlobals.ToonReverseSlowSpeed, OTPGlobals.ToonRotateSlowSpeed)

    def collisionsOff(self):
        self.controlManager.collisionsOff()

    def collisionsOn(self):
        self.controlManager.collisionsOn()

    def runSound(self):
        self.soundWalk.stop()
        base.playSfx(self.soundRun, looping=1)

    def walkSound(self):
        self.soundRun.stop()
        base.playSfx(self.soundWalk, looping=1)

    def stopSound(self):
        self.soundRun.stop()
        self.soundWalk.stop()

    def setMovementAnimation(self, loopName, playRate=1.0):
        if 'jump' in loopName:
            self.movingJumping = True
            self.movingForward = False
            self.movingNeutral = False
            self.movingRotation = False
            self.movingBackward = False
            self.stopSound()
            self.stopLookAround()
        elif loopName == 'run':
            self.movingJumping = False
            self.movingForward = True
            self.movingNeutral = False
            self.movingRotation = False
            self.movingBackward = False
            self.runSound()
            self.stopLookAround()
        elif loopName == 'walk':
            self.movingJumping = False
            self.movingForward = False
            self.movingNeutral = False
            if playRate == -1.0:
                self.movingBackward = True
                self.movingRotation = False
            else:
                self.movingBackward = False
                self.movingRotation = True
            self.walkSound()
            self.stopLookAround()
        elif loopName == 'neutral':
            self.movingJumping = False
            self.movingForward = False
            self.movingNeutral = True
            self.movingRotation = False
            self.movingBackward = False
            self.stopSound()
            self.startLookAround()
        else:
            self.movingJumping = False
            self.movingForward = False
            self.movingNeutral = False
            self.movingRotation = False
            self.movingBackward = False
            self.stopSound()
            self.stopLookAround()
        if self.animFSM.hasStateNamed(loopName):
            self.setAnimState(loopName, playRate)
        else:
            if self.getCurrentAnim() == loopName and self.getPlayRate(loopName) == playRate:
                return
            self.setPlayRate(playRate, loopName)
            self.loop(loopName)

    def handleAnimation(self, task):
        forward = KeyboardButton.up()
        backward = KeyboardButton.down()
        left = KeyboardButton.left()
        right = KeyboardButton.right()
        control = KeyboardButton.control()
        keyPressed = base.mouseWatcherNode.is_button_down
        if not self.standWalkRunReverse:
            self.standWalkRunReverse = (('neutral', 1.0),
             ('walk', 1.0),
             ('run', 1.0),
             ('walk', -1.0))

        if keyPressed(control):
            if self.isPageUp or self.isPageDown:
                self.clearPageUpDown()
            if keyPressed(forward) or keyPressed(backward) or keyPressed(left) or keyPressed(right):
                if self.movingJumping == False:
                    if self.physControls.isAirborne:
                        if not self.controlManager.forceAvJumpToken:
                            self.playingAnim = None
                            self.setMovementAnimation('jumpAirborne')
                    else:
                        if keyPressed(forward):
                            if self.movingForward == False:
                                self.setMovementAnimation(self.standWalkRunReverse[2][0], playRate=self.standWalkRunReverse[2][1])
                        elif keyPressed(backward):
                            if self.movingBackward == False:
                                self.setMovementAnimation(self.standWalkRunReverse[3][0], playRate=self.standWalkRunReverse[3][1])
                        elif keyPressed(left) or keyPressed(right):
                            if self.movingRotation == False:
                                self.setMovementAnimation(self.standWalkRunReverse[1][0], playRate=self.standWalkRunReverse[1][1])
                else:
                    if not self.physControls.isAirborne:
                        if keyPressed(forward):
                            if self.movingForward == False:
                                self.setMovementAnimation(self.standWalkRunReverse[2][0], playRate=self.standWalkRunReverse[2][1])
                        elif keyPressed(backward):
                            if self.movingBackward == False:
                                self.setMovementAnimation(self.standWalkRunReverse[3][0], playRate=self.standWalkRunReverse[3][1])
                        elif keyPressed(left) or keyPressed(right):
                            if self.movingRotation == False:
                                self.setMovementAnimation(self.standWalkRunReverse[1][0], playRate=self.standWalkRunReverse[1][1])
            else:
                if self.movingJumping == False:
                    if self.physControls.isAirborne:
                        if not self.controlManager.forceAvJumpToken:
                            self.playingAnim = 'neutral'
                            self.setMovementAnimation('jumpAirborne')
                    else:
                        if self.movingNeutral == False:
                            self.setMovementAnimation(self.standWalkRunReverse[0][0], playRate=self.standWalkRunReverse[0][1])
                else:
                    if not self.physControls.isAirborne:
                        if self.movingNeutral == False:
                            self.setMovementAnimation(self.standWalkRunReverse[0][0], playRate=self.standWalkRunReverse[0][1])
        elif keyPressed(forward) == 1:
            if self.isPageUp or self.isPageDown:
                self.clearPageUpDown()
            if self.movingForward == False:
                if not self.physControls.isAirborne:
                    self.setMovementAnimation(self.standWalkRunReverse[2][0], playRate=self.standWalkRunReverse[2][1])
        elif keyPressed(backward) == 1:
            if self.isPageUp or self.isPageDown:
                self.clearPageUpDown()
            if self.movingBackward == False:
                if not self.physControls.isAirborne:
                    self.setMovementAnimation(self.standWalkRunReverse[3][0], playRate=self.standWalkRunReverse[3][1])
        elif keyPressed(left) or keyPressed(right):
            if self.isPageUp or self.isPageDown:
                self.clearPageUpDown()
            if self.movingRotation == False:
                if not self.physControls.isAirborne:
                    self.setMovementAnimation(self.standWalkRunReverse[1][0], playRate=self.standWalkRunReverse[1][1])
        else:
            if not self.physControls.isAirborne:
                if self.movingNeutral == False:
                    self.setMovementAnimation(self.standWalkRunReverse[0][0], playRate=self.standWalkRunReverse[0][1])
        return Task.cont

    def enableSmartCameraViews(self):
        self.accept('tab', self.nextCameraPos, [1])
        self.accept('shift-tab', self.nextCameraPos, [0])
        self.accept('page_up', self.pageUp)
        self.accept('page_down', self.pageDown)

    def disableSmartCameraViews(self):
        self.ignore('tab')
        self.ignore('shift-tab')
        self.ignore('page_up')
        self.ignore('page_down')
        self.ignore('page_down-up')

    def pageUp(self):
        if not self.avatarControlsEnabled:
            return
        # self.wakeUp()
        if not self.isPageUp:
            self.isPageDown = 0
            self.isPageUp = 1
            self.lerpCameraFov(70, 0.6)
            self.setCameraPositionByIndex(self.cameraIndex)
        else:
            self.clearPageUpDown()

    def pageDown(self):
        if not self.avatarControlsEnabled:
            return
        # self.wakeUp()
        if not self.isPageDown:
            self.isPageUp = 0
            self.isPageDown = 1
            self.lerpCameraFov(70, 0.6)
            self.setCameraPositionByIndex(self.cameraIndex)
        else:
            self.clearPageUpDown()

    def clearPageUpDown(self):
        if self.isPageDown or self.isPageUp:
            self.lerpCameraFov(self.fov, 0.6)
            self.isPageDown = 0
            self.isPageUp = 0
            self.setCameraPositionByIndex(self.cameraIndex)

    def nextCameraPos(self, forward):
        if not self.avatarControlsEnabled:
            return
        # self.wakeUp()
        self.__cameraHasBeenMoved = 1
        if forward:
            self.cameraIndex += 1
            if self.cameraIndex > len(self.cameraPositions) - 1:
                self.cameraIndex = 0
        else:
            self.cameraIndex -= 1
            if self.cameraIndex < 0:
                self.cameraIndex = len(self.cameraPositions) - 1
        self.setCameraPositionByIndex(self.cameraIndex)

    def initCameraPositions(self):
        camHeight = self.getClampedAvatarHeight()
        heightScaleFactor = camHeight * 0.3333333333
        defLookAt = Point3(0.0, 1.5, camHeight)
        scXoffset = 3.0
        scPosition = (Point3(scXoffset - 1, -10.0, camHeight + 5.0), Point3(scXoffset, 2.0, camHeight))
        self.cameraPositions = [(Point3(0.0, -9.0 * heightScaleFactor, camHeight),
          defLookAt,
          Point3(0.0, camHeight, camHeight * 4.0),
          Point3(0.0, camHeight, camHeight * -1.0),
          0),
         (Point3(0.0, 0.7, camHeight),
          defLookAt,
          Point3(0.0, camHeight, camHeight * 1.33),
          Point3(0.0, camHeight, camHeight * 0.66),
          1),
         (Point3(5.7 * heightScaleFactor, 7.65 * heightScaleFactor, camHeight + 2.0),
          Point3(0.0, 1.0, camHeight),
          Point3(0.0, 1.0, camHeight * 4.0),
          Point3(0.0, 1.0, camHeight * -1.0),
          0),
         (Point3(0.0, 8.65 * heightScaleFactor, camHeight),
          Point3(0.0, 1.0, camHeight),
          Point3(0.0, 1.0, camHeight * 4.0),
          Point3(0.0, 1.0, camHeight * -1.0),
          0),
         (Point3(-camHeight * 3, 0.0, camHeight),
          Point3(0.0, 0.0, camHeight),
          Point3(0.0, camHeight, camHeight * 1.1),
          Point3(0.0, camHeight, camHeight * 0.9),
          1),
         (Point3(camHeight * 3, 0.0, camHeight),
          Point3(0.0, 0.0, camHeight),
          Point3(0.0, camHeight, camHeight * 1.1),
          Point3(0.0, camHeight, camHeight * 0.9),
          1),
         (Point3(0.0, -24.0 * heightScaleFactor, camHeight + 4.0),
          defLookAt,
          Point3(0.0, 1.5, camHeight * 4.0),
          Point3(0.0, 1.5, camHeight * -1.0),
          0),
         (Point3(0.0, -12.0 * heightScaleFactor, camHeight + 4.0),
          defLookAt,
          Point3(0.0, 1.5, camHeight * 4.0),
          Point3(0.0, 1.5, camHeight * -1.0),
          0)] + self.auxCameraPositions
        if self.wantDevCameraPositions:
            self.cameraPositions += [(Point3(0.0, 0.0, camHeight * 3),
              Point3(0.0, 0.0, 0.0),
              Point3(0.0, camHeight * 2, 0.0),
              Point3(0.0, -camHeight * 2, 0.0),
              1),
             (Point3(camHeight * 3, 0.0, camHeight),
              Point3(0.0, 0.0, camHeight),
              Point3(0.0, camHeight, camHeight * 1.1),
              Point3(0.0, camHeight, camHeight * 0.9),
              1),
             (Point3(camHeight * 3, 0.0, 0.0),
              Point3(0.0, 0.0, camHeight),
              Point3(0.0, camHeight, camHeight * 1.1),
              Point3(0.0, camHeight, camHeight * 0.9),
              1),
             (Point3(-camHeight * 3, 0.0, camHeight),
              Point3(0.0, 0.0, camHeight),
              Point3(0.0, camHeight, camHeight * 1.1),
              Point3(0.0, camHeight, camHeight * 0.9),
              1),
             (Point3(0.0, -60, 60),
              defLookAt + Point3(0, 15, 0),
              defLookAt + Point3(0, 15, 0),
              defLookAt + Point3(0, 15, 0),
              1),
             (Point3(0.0, -20, 20),
              defLookAt + Point3(0, 5, 0),
              defLookAt + Point3(0, 5, 0),
              defLookAt + Point3(0, 5, 0),
              1)]

    def lerpCameraFov(self, fov, time):
        taskMgr.remove('cam-fov-lerp-play')
        oldFov = base.camLens.getHfov()
        if abs(fov - oldFov) > 0.1:

            def setCamFov(fov):
                base.camLens.setMinFov(fov/(4./3.))

            self.camLerpInterval = LerpFunctionInterval(setCamFov, fromData=oldFov, toData=fov, duration=time, name='cam-fov-lerp')
            self.camLerpInterval.start()

    def recalcCameraSphere(self):
        nearPlaneDist = base.camLens.getNear()
        hFov = base.camLens.getHfov()
        vFov = base.camLens.getVfov()
        hOff = nearPlaneDist * math.tan(deg2Rad(hFov / 2.0))
        vOff = nearPlaneDist * math.tan(deg2Rad(vFov / 2.0))
        camPnts = [Point3(hOff, nearPlaneDist, vOff),
         Point3(-hOff, nearPlaneDist, vOff),
         Point3(hOff, nearPlaneDist, -vOff),
         Point3(-hOff, nearPlaneDist, -vOff),
         Point3(0.0, 0.0, 0.0)]
        avgPnt = Point3(0.0, 0.0, 0.0)
        for camPnt in camPnts:
            avgPnt = avgPnt + camPnt

        avgPnt = avgPnt / len(camPnts)
        sphereRadius = 0.0
        for camPnt in camPnts:
            dist = Vec3(camPnt - avgPnt).length()
            if dist > sphereRadius:
                sphereRadius = dist

        avgPnt = Point3(avgPnt)
        self.ccSphereNodePath.setPos(avgPnt)
        self.ccSphereNodePath2.setPos(avgPnt)
        self.ccSphere.setRadius(sphereRadius)

    def putCameraFloorRayOnAvatar(self):
        self.camFloorRayNode.setPos(self, 0, 0, 5)

    def putCameraFloorRayOnCamera(self):
        self.camFloorRayNode.setPos(self.ccSphereNodePath, 0, 0, 0)

    def setLookAtPoint(self, la):
        self.__curLookAt = Point3(la)

    def getLookAtPoint(self):
        return Point3(self.__curLookAt)

    def getClampedAvatarHeight(self):
        return max(self.getHeight(), 3.0)

    def getVisibilityPoint(self):
        return Point3(0.0, 0.0, self.getHeight())

    def posCamera(self, lerp, time):
        if not lerp:
            self.positionCameraWithPusher(self.getCompromiseCameraPos(), self.getLookAtPoint())
        else:
            camPos = self.getCompromiseCameraPos()
            savePos = camera.getPos()
            saveHpr = camera.getHpr()
            self.positionCameraWithPusher(camPos, self.getLookAtPoint())
            x = camPos[0]
            y = camPos[1]
            z = camPos[2]
            destHpr = camera.getHpr()
            h = destHpr[0]
            p = destHpr[1]
            r = destHpr[2]
            camera.setPos(savePos)
            camera.setHpr(saveHpr)
            taskMgr.remove('posCamera')
            camera.lerpPosHpr(x, y, z, h, p, r, time, task='posCamera')

    def positionCameraWithPusher(self, pos, lookAt):
        camera.setPos(pos)
        self.ccPusherTrav.traverse(self.__geom)
        camera.lookAt(lookAt)

    def setCameraPositionByIndex(self, index):
        self.notify.debug('switching to camera position %s' % index)
        self.setCameraSettings(self.cameraPositions[index])

    def setIdealCameraPos(self, pos):
        self.__idealCameraPos = Point3(pos)
        self.updateSmartCameraCollisionLineSegment()

    def getIdealCameraPos(self):
        return Point3(self.__idealCameraPos)

    def setCameraSettings(self, camSettings):
        self.setIdealCameraPos(camSettings[0])
        if self.isPageUp and self.isPageDown or not self.isPageUp and not self.isPageDown:
            self.__cameraHasBeenMoved = 1
            self.setLookAtPoint(camSettings[1])
        elif self.isPageUp:
            self.__cameraHasBeenMoved = 1
            self.setLookAtPoint(camSettings[2])
        elif self.isPageDown:
            self.__cameraHasBeenMoved = 1
            self.setLookAtPoint(camSettings[3])
        else:
            self.notify.error('This case should be impossible.')
        self.__disableSmartCam = camSettings[4]
        if self.__disableSmartCam:
            self.putCameraFloorRayOnAvatar()
            self.cameraZOffset = 0.0

    def getCompromiseCameraPos(self):
        if self.__idealCameraObstructed == 0:
            compromisePos = self.getIdealCameraPos()
        else:
            visPnt = self.getVisibilityPoint()
            idealPos = self.getIdealCameraPos()
            distance = Vec3(idealPos - visPnt).length()
            ratio = self.closestObstructionDistance / distance
            compromisePos = idealPos * ratio + visPnt * (1 - ratio)
            liftMult = 1.0 - ratio * ratio
            compromisePos = Point3(compromisePos[0], compromisePos[1], compromisePos[2] + self.getHeight() * 0.4 * liftMult)
        compromisePos.setZ(compromisePos[2] + self.cameraZOffset)
        return compromisePos

    def updateSmartCameraCollisionLineSegment(self):
        pointB = self.getIdealCameraPos()
        pointA = self.getVisibilityPoint()
        vectorAB = Vec3(pointB - pointA)
        lengthAB = vectorAB.length()
        if lengthAB > 0.001:
            self.ccLine.setPointA(pointA)
            self.ccLine.setPointB(pointB)

    def initializeSmartCamera(self):
        self.__idealCameraObstructed = 0
        self.closestObstructionDistance = 0.0
        self.cameraIndex = 0
        self.auxCameraPositions = []
        self.cameraZOffset = 0.0
        self.__onLevelGround = 0
        self.__camCollCanMove = 0
        self.__geom = render
        self.__disableSmartCam = 0
        self.initializeSmartCameraCollisions()
        self._smartCamEnabled = False

    def shutdownSmartCamera(self):
        self.deleteSmartCameraCollisions()

    def setOnLevelGround(self, flag):
        self.__onLevelGround = flag

    def setCameraCollisionsCanMove(self, flag):
        self.__camCollCanMove = flag

    def setGeom(self, geom):
        self.__geom = geom

    def startUpdateSmartCamera(self, push = 1):
        if self._smartCamEnabled:
            self.notify.warning('redundant call to startUpdateSmartCamera')
            return
        self._smartCamEnabled = True
        self.__floorDetected = 0
        self.__cameraHasBeenMoved = 0
        self.recalcCameraSphere()
        self.initCameraPositions()
        self.setCameraPositionByIndex(self.cameraIndex)
        self.posCamera(0, 0.0)
        self.__instantaneousCamPos = camera.getPos()
        if push:
            self.cTrav.addCollider(self.ccSphereNodePath, self.camPusher)
            self.ccTravOnFloor.addCollider(self.ccRay2NodePath, self.camFloorCollisionBroadcaster)
            self.__disableSmartCam = 0
        else:
            self.__disableSmartCam = 1
        self.__lastPosWrtRender = camera.getPos(render)
        self.__lastHprWrtRender = camera.getHpr(render)
        taskName = 'updateSmartCamera'
        taskMgr.remove(taskName)
        taskMgr.add(self.updateSmartCamera, taskName, priority=47)
        self.enableSmartCameraViews()

    def stopUpdateSmartCamera(self):
        if not self._smartCamEnabled:
            self.notify.warning('redundant call to stopUpdateSmartCamera')
            return
        self.disableSmartCameraViews()
        self.cTrav.removeCollider(self.ccSphereNodePath)
        self.ccTravOnFloor.removeCollider(self.ccRay2NodePath)
        if not base.localAvatar.isEmpty():
            self.putCameraFloorRayOnAvatar()
        taskMgr.remove('updateSmartCamera')
        self._smartCamEnabled = False

    def updateSmartCamera(self, task):
        if not self.__camCollCanMove and not self.__cameraHasBeenMoved:
            if self.__lastPosWrtRender == camera.getPos(render):
                if self.__lastHprWrtRender == camera.getHpr(render):
                    return Task.cont
        self.__cameraHasBeenMoved = 0
        self.__lastPosWrtRender = camera.getPos(render)
        self.__lastHprWrtRender = camera.getHpr(render)
        self.__idealCameraObstructed = 0
        if not self.__disableSmartCam:
            self.ccTrav.traverse(self.__geom)
            if self.camCollisionQueue.getNumEntries() > 0:
                self.camCollisionQueue.sortEntries()
                self.handleCameraObstruction(self.camCollisionQueue.getEntry(0))
            if not self.__onLevelGround:
                self.handleCameraFloorInteraction()
        if not self.__idealCameraObstructed:
            self.nudgeCamera()
        if not self.__disableSmartCam:
            self.ccPusherTrav.traverse(self.__geom)
            self.putCameraFloorRayOnCamera()
        self.ccTravOnFloor.traverse(self.__geom)
        return Task.cont

    def nudgeCamera(self):
        CLOSE_ENOUGH = 0.1
        curCamPos = self.__instantaneousCamPos
        curCamHpr = camera.getHpr()
        targetCamPos = self.getCompromiseCameraPos()
        targetCamLookAt = self.getLookAtPoint()
        posDone = 0
        if Vec3(curCamPos - targetCamPos).length() <= CLOSE_ENOUGH:
            camera.setPos(targetCamPos)
            posDone = 1
        camera.setPos(targetCamPos)
        camera.lookAt(targetCamLookAt)
        targetCamHpr = camera.getHpr()
        for x in xrange(3):
            # This function is from PythonUtil:
            targetCamHpr[x] = fitDestAngle2Src(curCamHpr[x], targetCamHpr[x])
        hprDone = 0
        if Vec3(curCamHpr - targetCamHpr).length() <= CLOSE_ENOUGH:
            hprDone = 1
        if posDone and hprDone:
            return
        lerpRatio = 0.15
        lerpRatio = 1 - pow(1 - lerpRatio, globalClock.getDt() * 30.0)
        self.__instantaneousCamPos = targetCamPos * lerpRatio + curCamPos * (1 - lerpRatio)
        if self.__disableSmartCam or not self.__idealCameraObstructed:
            newHpr = targetCamHpr * lerpRatio + curCamHpr * (1 - lerpRatio)
        else:
            newHpr = targetCamHpr
        camera.setPos(self.__instantaneousCamPos)
        camera.setHpr(newHpr)

    def popCameraToDest(self):
        newCamPos = self.getCompromiseCameraPos()
        newCamLookAt = self.getLookAtPoint()
        self.positionCameraWithPusher(newCamPos, newCamLookAt)
        self.__instantaneousCamPos = camera.getPos()

    def handleCameraObstruction(self, camObstrCollisionEntry):
        collisionPoint = camObstrCollisionEntry.getSurfacePoint(self.ccLineNodePath)
        collisionVec = Vec3(collisionPoint - self.ccLine.getPointA())
        distance = collisionVec.length()
        self.__idealCameraObstructed = 1
        self.closestObstructionDistance = distance
        self.popCameraToDest()

    def handleCameraFloorInteraction(self):
        self.putCameraFloorRayOnCamera()
        self.ccTravFloor.traverse(self.__geom)
        if self.__onLevelGround:
            return
        if self.camFloorCollisionQueue.getNumEntries() == 0:
            return
        self.camFloorCollisionQueue.sortEntries()
        camObstrCollisionEntry = self.camFloorCollisionQueue.getEntry(0)
        camHeightFromFloor = camObstrCollisionEntry.getSurfacePoint(self.ccRayNodePath)[2]
        self.cameraZOffset = camera.getPos()[2] + camHeightFromFloor
        if self.cameraZOffset < 0:
            self.cameraZOffset = 0
        if self.__floorDetected == 0:
            self.__floorDetected = 1
            self.popCameraToDest()
