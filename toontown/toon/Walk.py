from panda3d.core import *
from direct.task.Task import Task
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
from direct.fsm import State

class Walk(StateData.StateData):
    notify = directNotify.newCategory('Walk')

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.fsm = ClassicFSM.ClassicFSM('Walk', [State.State('off', self.enterOff, self.exitOff, ['walking', 'swimming', 'slowWalking']),
         State.State('walking', self.enterWalking, self.exitWalking, ['swimming', 'slowWalking']),
         State.State('swimming', self.enterSwimming, self.exitSwimming, ['walking', 'slowWalking']),
         State.State('slowWalking', self.enterSlowWalking, self.exitSlowWalking, ['walking', 'swimming'])], 'off', 'off')
        self.fsm.enterInitialState()
        self.isSwimSoundAudible = 0
        self.swimSoundPlaying = 0

    def load(self):
        pass

    def unload(self):
        del self.fsm

    def enter(self, slowWalk = 0):
        base.localAvatar.startBlink()
        base.localAvatar.attachCamera()
        shouldPush = 1
        if len(base.localAvatar.cameraPositions) > 0:
            shouldPush = not base.localAvatar.cameraPositions[base.localAvatar.cameraIndex][4]
        base.localAvatar.startUpdateSmartCamera(shouldPush)
        base.localAvatar.showName()
        base.localAvatar.collisionsOn()
        base.localAvatar.enableAvatarControls()

    def exit(self):
        self.fsm.request('off')
        self.ignore('control')
        base.localAvatar.disableAvatarControls()
        base.localAvatar.stopUpdateSmartCamera()
        base.localAvatar.stopBlink()
        base.localAvatar.detachCamera()
        base.localAvatar.collisionsOff()
        base.localAvatar.controlManager.placeOnFloor()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterWalking(self):
        if base.localAvatar.hp > 0:
            base.localAvatar.startTrackAnimToSpeed()
            base.localAvatar.setWalkSpeedNormal()
        else:
            self.fsm.request('slowWalking')

    def exitWalking(self):
        base.localAvatar.stopTrackAnimToSpeed()

    def setSwimSoundAudible(self, isSwimSoundAudible):
        self.isSwimSoundAudible = isSwimSoundAudible
        if isSwimSoundAudible == 0 and self.swimSoundPlaying:
            self.swimSound.stop()
            self.swimSoundPlaying = 0

    def enterSwimming(self, swimSound):
        base.localAvatar.setWalkSpeedNormal()
        self.swimSound = swimSound
        self.swimSoundPlaying = 0
        base.localAvatar.setAnimState('swim', 1.0)
        taskMgr.add(self.__swim, 'localToonSwimming')

    def exitSwimming(self):
        taskMgr.remove('localToonSwimming')
        self.swimSound.stop()
        del self.swimSound
        self.swimSoundPlaying = 0

    def __swim(self, task):
        speed = base.mouseInterfaceNode.getSpeed()
        if speed == 0 and self.swimSoundPlaying:
            self.swimSoundPlaying = 0
            self.swimSound.stop()
        elif speed > 0 and self.swimSoundPlaying == 0 and self.isSwimSoundAudible:
            self.swimSoundPlaying = 1
            base.playSfx(self.swimSound, looping=1)
        return Task.cont

    def enterSlowWalking(self):
        self.accept(base.localAvatar.uniqueName('positiveHP'), self.__handlePositiveHP)
        base.localAvatar.startTrackAnimToSpeed()
        base.localAvatar.setWalkSpeedSlow()

    def __handlePositiveHP(self):
        self.fsm.request('walking')

    def exitSlowWalking(self):
        base.localAvatar.stopTrackAnimToSpeed()
        self.ignore(base.localAvatar.uniqueName('positiveHP'))
