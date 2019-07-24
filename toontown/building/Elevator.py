from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.task.Task import Task
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
from toontown.suit import Suit
from toontown.building.ElevatorConstants import *
from toontown.building.ElevatorUtils import *

class Elevator(DirectObject):
    notify = directNotify.newCategory('Elevator')

    def __init__(self, block, type=ELEVATOR_NORMAL):
        self.block = block
        self.type = type
        self.openSfx = base.loader.loadSfx('phase_5/audio/sfx/elevator_door_open.ogg')
        self.closeSfx = base.loader.loadSfx('phase_5/audio/sfx/elevator_door_close.ogg')
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.exitButton = None
        self.clock = None

    def setup(self, elevatorModel, parent, track, difficulty, numFloors, elite=False):
        self.np = elevatorModel
        self.parent = parent
        self.track = track
        self.difficulty = difficulty
        self.numFloors = numFloors
        self.elite = elite

        if not self.elite:
            npc = self.np.findAllMatches('**/floor_light_?;+s')
            for i in range(npc.getNumPaths()):
                light = npc.getPath(i)
                floor = int(light.getName()[-1:]) - 1
                if floor < self.numFloors:
                    light.setColor(LIGHT_OFF_COLOR)
                    if base.cr.playGame.street.place and hasattr(base.cr.playGame.street.place, 'currentFloor'):
                        currFloor = base.cr.playGame.street.place.currentFloor
                        if floor == (currFloor - 1):
                            light.setColor(LIGHT_ON_COLOR)
                else:
                    light.hide()

        self.np.reparentTo(self.parent)
        self.np.find('**/flashing').setDepthOffset(1)
        self.leftDoor = self.np.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.np.find('**/left_door')
        self.rightDoor = self.np.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.np.find('**/right_door')
        self.elevatorSphere = self.np.find('**/door_collisions')
        self.elevatorSphere.setName(self.uniqueName('elevatorSphere'))
        buttonGui = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        self.upButton = buttonGui.find('**//InventoryButtonUp')
        self.downButton = buttonGui.find('**/InventoryButtonDown')
        self.rolloverButton = buttonGui.find('**/InventoryButtonRollover')
        buttonGui.removeNode()

    def delete(self):
        self.removeActive()
        del self.np
        del self.parent
        del self.track
        del self.difficulty
        del self.numFloors
        del self.elite
        del self.leftDoor
        del self.rightDoor
        del self.elevatorSphere
        del self.upButton
        del self.downButton
        del self.rolloverButton
        if hasattr(self, 'cab'):
            del self.cab

    def showCorpIcon(self):
        self.cab = self.np.find('**/elevator')
        cogIcons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.track
        if dept == 'c':
            corpIcon = cogIcons.find('**/CorpIcon').copyTo(self.cab)
        elif dept == 's':
            corpIcon = cogIcons.find('**/SalesIcon').copyTo(self.cab)
        elif dept == 'l':
            corpIcon = cogIcons.find('**/LegalIcon').copyTo(self.cab)
        elif dept == 'm':
            corpIcon = cogIcons.find('**/MoneyIcon').copyTo(self.cab)
        corpIcon.setPos(0, 6.79, 6.8)
        corpIcon.setScale(3)
        corpIcon.setColor(Suit.Suit.medallionColors[dept])
        cogIcons.removeNode()

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, str(id(self))))

    def addActive(self):
        self.ignoreAll()
        self.accept('enter' + self.elevatorSphere.getName(), self.__handleEnterSphere)

    def removeActive(self):
        self.ignore('enter' + self.elevatorSphere.getName())

    def openDoors(self, callback=None, extraArgs=[]):
        track = getOpenInterval(self.leftDoor, self.rightDoor, self.openSfx, self.type)
        if callback:
            track.setDoneEvent(self.uniqueName('elevatorDoorsOpen'))
            self.acceptOnce(self.uniqueName('elevatorDoorsOpen'), callback, extraArgs)
        track.start()

    def forceOpenDoors(self):
        openDoors(self.leftDoor, self.rightDoor, self.type)

    def closeDoors(self, callback=None, extraArgs=[]):
        track = getCloseInterval(self.leftDoor, self.rightDoor, self.closeSfx, self.type)
        if callback:
            track.setDoneEvent(self.uniqueName('elevatorDoorsClose'))
            self.acceptOnce(self.uniqueName('elevatorDoorsClose'), callback, extraArgs)
        track.start()

    def forceCloseDoors(self):
        closeDoors(self.leftDoor, self.rightDoor, self.type)

    def board(self, index, callback=None, extraArgs=[]):
        base.localAvatar.disable()
        base.localAvatar.setZ(self.np, ElevatorPoints[index][2])
        base.localAvatar.setShadowHeight(0)
        camera.wrtReparentTo(self.np)
        cameraTrack = LerpPosHprInterval(camera, 1.5, Point3(0, -16, 5.5), Point3(0, 0, 0))
        animInFunc = Sequence(Func(base.localAvatar.setAnimState, 'run'))
        animFunc = Func(base.localAvatar.setAnimState, 'neutral')
        track = Sequence(animInFunc, LerpPosInterval(base.localAvatar, TOON_BOARD_ELEVATOR_TIME * 0.75, apply(Point3, ElevatorPoints[index]), other=self.np), LerpHprInterval(base.localAvatar, TOON_BOARD_ELEVATOR_TIME * 0.25, Point3(180, 0, 0), other=self.np), animFunc, name=base.localAvatar.uniqueName('fillElevator'), autoPause=1)
        track = Parallel(cameraTrack, track)
        if callback:
            track.setDoneEvent(track.getName())
            self.acceptOnce(track.getName(), self.closeDoors, [callback, extraArgs])
        else:
            self.enableExitButton()
            self.startCountdownClock(self.countdownTime, 0)
        track.start()

    def __handleEnterSphere(self, collEntry):
        base.localAvatar.disable()
        base.localAvatar.setAnimState('neutral')
        if base.cr.playGame.street and not base.cr.playGame.street.place:
            self.dialog = TTDialog.TTDialog(text=TTLocalizer.SuitBuildingDialog, text_align=TextNode.ACenter, style=TTDialog.YesNo, command=self.handleDialog)
            self.dialog.show()
            return
        elif base.cr.playGame.street.place:
            self.board(0, callback=base.cr.playGame.street.place.loadNextFloor)
        else:
            self.board(0)

    def handleDialog(self, choice):
        self.dialog.destroy()
        if choice == 1:
            if self.elite:
                callbackFunc = self.enterEliteBuilding
            else:
                callbackFunc = self.enterSuitBuilding
            self.board(0, callback=callbackFunc)
        else:
            base.localAvatar.enable()

    def hopOff(self, index, closeDoors=False):
        base.localAvatar.setAnimState('run')
        base.localAvatar.setHpr(self.np, 180, 0, 0)
        animFunc = Func(base.localAvatar.setAnimState, 'neutral')
        track = Sequence(LerpPosInterval(base.localAvatar, TOON_EXIT_ELEVATOR_TIME, Point3(*JumpOutOffsets[index]), startPos=Point3(*ElevatorPoints[index]), other=self.np), animFunc, name=base.localAvatar.uniqueName('emptyElevator'), autoPause=1)
        track.setDoneEvent(track.getName())
        self.acceptOnce(track.getName(), self.__handleExitSphere, [closeDoors])
        track.start()
        if self.exitButton:
            self.disableExitButton()
        if self.clock:
            self.exitWaitCountdown()

    def __handleExitSphere(self, closeDoors=False):
        base.localAvatar.enable()
        if closeDoors:
            self.closeDoors()

    def enableExitButton(self):
        self.exitButton = DirectButton(relief=None, text=TTLocalizer.ElevatorHopOff, text_fg=(0.9, 0.9, 0.9, 1), text_pos=(0, -0.23), text_scale=TTLocalizer.EexitButton, image=(self.upButton, self.downButton, self.rolloverButton), image_color=(0.5, 0.5, 0.5, 1), image_scale=(20, 1, 11), pos=(0, 0, 0.8), scale=0.15, command=self.hopOff, extraArgs=[0])

    def disableExitButton(self):
        self.exitButton.destroy()
        self.exitButton = None

    def timerTask(self, task):
        countdownTime = int(task.duration - task.time)
        timeStr = str(countdownTime)
        if self.clockNode.getText() != timeStr:
            self.clockNode.setText(timeStr)
        if task.time >= task.duration:
            self.disableExitButton()
            self.exitWaitCountdown()
            if self.elite:
                callbackFunc = self.enterEliteBuilding
            else:
                callbackFunc = self.enterSuitBuilding
            self.closeDoors(callback=callbackFunc)
            return Task.done
        else:
            return Task.cont

    def countdown(self, duration):
        countdownTask = Task(self.timerTask)
        countdownTask.duration = duration
        taskMgr.remove(self.uniqueName('elevatorTimerTask'))
        return taskMgr.add(countdownTask, self.uniqueName('elevatorTimerTask'))

    def startCountdownClock(self, countdownTime, ts):
        self.clockNode = TextNode('elevatorClock')
        self.clockNode.setFont(ToontownGlobals.getSignFont())
        self.clockNode.setAlign(TextNode.ACenter)
        self.clockNode.setTextColor(0.5, 0.5, 0.5, 1)
        self.clockNode.setText(str(int(countdownTime)))
        self.clock = self.np.attachNewNode(self.clockNode)
        self.clock.setPosHprScale(0, 2.0, 7.5, 0, 0, 0, 2.0, 2.0, 2.0)
        if ts < countdownTime:
            self.countdown(countdownTime - ts)

    def exitWaitCountdown(self):
        taskMgr.remove(self.uniqueName('elevatorTimerTask'))
        self.clock.removeNode()
        del self.clock
        del self.clockNode

    def enterSuitBuilding(self):
        base.cr.playGame.getActiveZone().enterSuitBuilding(self.block, self.track, self.difficulty, self.numFloors)

    def enterEliteBuilding(self):
        base.cr.playGame.getActiveZone().enterEliteBuilding(self.block, self.track, self.difficulty, self.numFloors)
