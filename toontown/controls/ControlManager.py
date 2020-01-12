from toontown.controls.InputStateGlobal import inputState
#from DirectGui import *
#from PythonUtil import *
#from IntervalGlobal import *

#from otp.avatar import Avatar
from direct.directnotify import DirectNotifyGlobal
#import GhostWalker
#import GravityWalker
#import NonPhysicsWalker
#import PhysicsWalker
#if __debug__:
#    import DevWalker
from direct.task import Task
from panda3d.core import ConfigVariableBool
from toontown.toonbase.ToontownGlobals import GP_CONTROLS

# This is a hack, it may be better to use a line instead of a ray.
CollisionHandlerRayStart = 4000.0


class ControlManager:
    notify = DirectNotifyGlobal.directNotify.newCategory("ControlManager")

    def __init__(self, enable=True, passMessagesThrough = False):
        self.notify.debug("init control manager %s" % (passMessagesThrough))
        self.passMessagesThrough = passMessagesThrough
        self.inputStateTokens = []
        # Used to switch between strafe and turn. We will reset to whatever was last set.
        self.controls = {}
        self.currentControls = None
        self.currentControlsName = None
        self.isEnabled = 0
        self.ignoreUse = 0
        if enable:
            self.enable()
        #self.monitorTask = taskMgr.add(self.monitor, "ControlManager-%s"%(id(self)), priority=-1)
        self.forceAvJumpToken = None


    if __debug__:
        def lockControls(self):
            self.ignoreUse = True

        def unlockControls(self):
            self.ignoreUse = False

    def __str__(self):
        return 'ControlManager: using \'%s\'' % self.currentControlsName

    def add(self, controls, name="basic"):
        """Add a control instance to the list of available control systems.
        args:
            controls: an avatar control system.
            name (str): any key that you want to use to refer to the controls later (e.g. using the use(<name>) call).
        """
        if not controls:
            return
        oldControls = self.controls.get(name)
        if oldControls:
            self.notify.debug("Replacing controls: %s" % name)
            oldControls.disableAvatarControls()
            oldControls.setCollisionsActive(0)
            oldControls.delete()
        controls.disableAvatarControls()
        controls.setCollisionsActive(0)
        self.controls[name] = controls

    def get(self, name):
        return self.controls.get(name)

    def remove(self, name):
        """Remove a control instance from the list of available control
        systems.
        args:
            name: any key that was used to refer to the controls when they were added (e.g. using the add(<controls>, <name>) call).
        """
        oldControls = self.controls.pop(name,None)
        if oldControls:
            self.notify.debug("Removing controls: %s" % name)
            oldControls.disableAvatarControls()
            oldControls.setCollisionsActive(0)

    def use(self, name, avatar):
        """
        name is a key (string) that was previously passed to add().
        Use a previously added control system.
        """
        if __debug__ and self.ignoreUse:
            return
        controls = self.controls.get(name)

        if controls:
            if controls != self.currentControls:
                if self.currentControls:
                    self.currentControls.disableAvatarControls()
                    self.currentControls.setCollisionsActive(0)
                    self.currentControls.setAvatar(None)
                self.currentControls = controls
                self.currentControlsName = name
                self.currentControls.setAvatar(avatar)
                self.currentControls.setCollisionsActive(1)
                if self.isEnabled:
                    self.currentControls.enableAvatarControls()
                messenger.send('use-%s-controls'%(name,), [avatar])
        else:
            self.notify.debug("Unknown controls: %s" % name)

    def setSpeeds(self, forwardSpeed, jumpForce,
            reverseSpeed, rotateSpeed, strafeLeft=0, strafeRight=0):
        for controls in self.controls.values():
            controls.setWalkSpeed(forwardSpeed, jumpForce, reverseSpeed, rotateSpeed)

    def delete(self):
        self.disable()
        del self.controls
        del self.currentControls

        for token in self.inputStateTokens:
            token.release()

        #self.monitorTask.remove()

    def getSpeeds(self):
        if self.currentControls:
            return self.currentControls.getSpeeds()
        return None

    def getIsAirborne(self):
        if self.currentControls:
            return self.currentControls.getIsAirborne()
        return False

    def setTag(self, key, value):
        for controls in self.controls.values():
            controls.setTag(key, value)

    def deleteCollisions(self):
        for controls in self.controls.values():
            controls.deleteCollisions()

    def collisionsOn(self):
        if self.currentControls:
            self.currentControls.setCollisionsActive(1)

    def collisionsOff(self):
        if self.currentControls:
            self.currentControls.setCollisionsActive(0)

    def placeOnFloor(self):
        if self.currentControls:
            self.currentControls.placeOnFloor()

    def enable(self):
        if self.isEnabled:
            return

        self.isEnabled = 1

        # keep track of what we do on the inputState so we can undo it later on
        #self.inputStateTokens = []
        source = inputState.Keyboard
        if base.gamepad:
            source = inputState.Gamepad
        self.refreshInputStates(source)
        self.accept('refresh-controls', self.refreshInputStates)
        if self.currentControls:
            self.currentControls.enableAvatarControls()

    def refreshInputStates(self, source=None):
        self.inputStateTokens = []
        if self.passMessagesThrough:
            ist = self.inputStateTokens
            source = inputState.Keyboard
            if base.gamepad:
                source = inputState.Gamepad
            ist.append(inputState.watchWithModifiers("forward", settings[base.getCurrentDevice()]['forward'], inputSource=source))
            ist.append(inputState.watchWithModifiers("reverse", settings[base.getCurrentDevice()]['reverse'], inputSource=source))
            ist.append(inputState.watchWithModifiers("turnLeft", settings[base.getCurrentDevice()]['turn_left'], inputSource=source))
            ist.append(inputState.watchWithModifiers("turnRight", settings[base.getCurrentDevice()]['turn_right'], inputSource=source))
        ist = self.inputStateTokens
        keybinds = settings['keybinds']
        keybinds = keybinds.get(base.getCurrentDevice())
        if not keybinds:
            settings['keybinds'][base.getCurrentDevice()] = GP_CONTROLS
            keybinds = GP_CONTROLS
        ist.append(inputState.watch("run", 'runningEvent', "running-on", "running-off"))

        ist.append(inputState.watchWithModifiers("forward", keybinds['forward'], inputSource=source))
        ist.append(inputState.watch("forward", "force-forward", "force-forward-stop"))

        ist.append(inputState.watchWithModifiers("reverse", keybinds['reverse'], inputSource=source))

        ist.append(inputState.watchWithModifiers("turnLeft", keybinds['turn_left'], inputSource=source))
        ist.append(inputState.watch("turnleft", "force-turn_left", "force-turn_left-stop"))
        ist.append(inputState.watch("turnLeft", "force-turnLeft", "force-turnLeft-stop"))

        ist.append(inputState.watchWithModifiers("turnRight", keybinds['turn_right'], inputSource=source))
        ist.append(inputState.watch("turnRight", "force-turn_right", "force-turn_right-stop"))
        ist.append(inputState.watch("jump", keybinds['jump'], keybinds['jump'] + '-up', inputSource=source))

    def disable(self):
        self.isEnabled = 0

        for token in self.inputStateTokens:
            token.release()
        self.inputStateTokens = []
        self.ignore('refresh-controls')

        if self.currentControls:
            self.currentControls.disableAvatarControls()

        if self.passMessagesThrough: # for not breaking toontown
            ist = self.inputStateTokens
            source = inputState.Keyboard
            if base.gamepad:
                source = inputState.Gamepad
            ist.append(inputState.watchWithModifiers("forward", settings[base.getCurrentDevice()]['forward'], inputSource=source))
            ist.append(inputState.watchWithModifiers("reverse", settings[base.getCurrentDevice()]['reverse'], inputSource=source))
            ist.append(inputState.watchWithModifiers("turnLeft", settings[base.getCurrentDevice()]['turn_left'], inputSource=source))
            ist.append(inputState.watchWithModifiers("turnRight", settings[base.getCurrentDevice()]['turn_right'], inputSource=source))

    def stop(self):
        self.disable()
        if self.currentControls:
            self.currentControls.setCollisionsActive(0)
            self.currentControls.setAvatar(None)
        self.currentControls = None

    def disableAvatarJump(self):
        if not self.forceAvJumpToken:
            return
        self.forceAvJumpToken = inputState.force('jump', 0, 'ControlManager.disableAvatarJump')

    def enableAvatarJump(self):
        """
        Stop forcing the ctrl key to return 0's
        """
        if self.forceAvJumpToken:
            self.forceAvJumpToken.release()
            del self.forceAvJumpToken

    def monitor(self, foo):
        #if 1:
        #    airborneHeight=self.avatar.getAirborneHeight()
        #    onScreenDebug.add("airborneHeight", "% 10.4f"%(airborneHeight,))
        onScreenDebug.add("InputState forward", "%d"%(inputState.isSet("forward")))
        onScreenDebug.add("InputState reverse", "%d"%(inputState.isSet("reverse")))
        onScreenDebug.add("InputState turnLeft", "%d"%(inputState.isSet("turnLeft")))
        onScreenDebug.add("InputState turnRight", "%d"%(inputState.isSet("turnRight")))
        #onScreenDebug.add("InputState slideLeft", "%d"%(inputState.isSet("slideLeft")))
        #onScreenDebug.add("InputState slideRight", "%d"%(inputState.isSet("slideRight")))
        return Task.cont
