from panda3d.core import *
from toontown.toonbase import ToontownGlobals

class GamepadManager:
    def __init__(self):
        self.l_down = False
        self.l_up = False
        self.l_left = False
        self.l_right = False
        self.r_down = False
        self.r_up = False
        self.r_left = False
        self.r_right = False

    def findInput(self, task):
        if base.gamepad:
            axis = base.gamepad.findAxis(InputDevice.Axis.left_x)
            if not axis.value < -ToontownGlobals.GP_DEADZONE and self.l_left:
                self.l_left = False
                messenger.send('lstick_left-up')
            elif not axis.value > ToontownGlobals.GP_DEADZONE and self.l_right:
                self.l_right = False
                messenger.send('lstick_right_up')
            if axis.value < -ToontownGlobals.GP_DEADZONE:
                messenger.send('lstick_left')
                self.l_left = True
            elif axis.value > ToontownGlobals.GP_DEADZONE:
                messenger.send('lstick_right')
                self.l_right = True
            axis = base.gamepad.findAxis(InputDevice.Axis.left_y)
            if not axis.value < -ToontownGlobals.GP_DEADZONE and self.l_down:
                self.l_down = False
                messenger.send('lstick_down-up')
            elif not axis.value > ToontownGlobals.GP_DEADZONE and self.l_up:
                self.l_up = False
                messenger.send('lstick_up-up')
            if axis.value < -ToontownGlobals.GP_DEADZONE:
                messenger.send('lstick_down')
                self.l_down = True
            elif axis.value > ToontownGlobals.GP_DEADZONE:
                messenger.send('lstick_up')
                self.l_up = True
            axis = base.gamepad.findAxis(InputDevice.Axis.right_x)
            print(axis.value)
            if not axis.value < -ToontownGlobals.GP_DEADZONE and self.r_left:
                self.r_left = False
                messenger.send('rstick_left-up')
            elif not axis.value > ToontownGlobals.GP_DEADZONE and self.r_right:
                self.r_right = False
                messenger.send('rstick_right-up')
            if axis.value < -ToontownGlobals.GP_DEADZONE:
                messenger.send('rstick_left')
                self.r_left = True
            elif axis.value > ToontownGlobals.GP_DEADZONE:
                messenger.send('rstick_right')
                self.r_right = True
            axis = base.gamepad.findAxis(InputDevice.Axis.right_y)
            if not axis.value < -ToontownGlobals.GP_DEADZONE and self.r_down:
                self.r_down = False
                messenger.send('rstick_down-up')
            elif not axis.value > ToontownGlobals.GP_DEADZONE and self.r_up:
                self.r_up = False
                messenger.send('rstick_up-up')
            if axis.value < -ToontownGlobals.GP_DEADZONE:
                messenger.send('rstick_down')
                self.r_down = True
            elif axis.value > ToontownGlobals.GP_DEADZONE:
                messenger.send('rstick_up')
                self.r_up = True
        return task.cont
