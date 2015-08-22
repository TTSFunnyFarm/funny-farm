from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.task.Task import Task
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from ElevatorConstants import *
from ElevatorUtils import *

class Elevator(DirectObject):
	notify = directNotify.newCategory('Elevator')

	def __init__(self, type=ELEVATOR_NORMAL):
		self.type = type
		if self.type == ELEVATOR_NORMAL:
			self.modelPath = 'phase_5/models/cogdominium/tt_m_ara_csa_elevatorB'
		else:
			self.notify.error('Invalid elevator type: ' + self.type)
		self.openSfx = base.loadSfx('phase_5/audio/sfx/elevator_door_open.ogg')
		self.closeSfx = base.loadSfx('phase_5/audio/sfx/elevator_door_close.ogg')
		self.countdownTime = ElevatorData[self.type]['countdown']
		self.exitButton = None
		self.clock = None

	def setup(self, parent):
		self.parent = parent
		self.np = loader.loadModel(self.modelPath)
		self.np.reparentTo(self.parent)
		self.np.find('**/flashing').setDepthOffset(1)
		self.leftDoor = self.np.find('**/left_door')
		self.rightDoor = self.np.find('**/right_door')
		self.elevatorSphere = self.np.find('**/door_collisions')
		self.elevatorSphere.setName(self.uniqueName('elevatorSphere'))
		self.buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
		self.upButton = self.buttonModels.find('**//InventoryButtonUp')
		self.downButton = self.buttonModels.find('**/InventoryButtonDown')
		self.rolloverButton = self.buttonModels.find('**/InventoryButtonRollover')

	def delete(self):
		self.removeActive()
		self.np.removeNode()
		del self.np
		del self.leftDoor
		del self.rightDoor
		del self.elevatorSphere
		self.buttonModels.removeNode()
		del self.buttonModels
		del self.upButton
		del self.downButton
		del self.rolloverButton

	def uniqueName(self, idString):
		return ('%s-%s' % (idString, str(id(self))))

	def addActive(self):
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
		if base.cr.playGame.place:
			self.board(0, callback=base.cr.playGame.place.loadNextFloor)
		else:
			self.board(0)

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
		base.localAvatar.collisionsOn()
		base.localAvatar.enableAvatarControls()
		base.localAvatar.setupSmartCamera()
		base.localAvatar.book.showButton()
		base.localAvatar.beginAllowPies()
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
			self.closeDoors(callback=self.enterEliteBuilding)
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

	def enterEliteBuilding(self):
		zoneId = base.cr.playGame.street.zoneId
		base.cr.playGame.exitStreet()
		base.cr.playGame.enterEliteInterior(zoneId)



