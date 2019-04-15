from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownGlobals
from ElevatorConstants import *
from ElevatorUtils import *

class SuitInteriorBase(DirectObject):
    notify = directNotify.newCategory('SuitInterior')

    def __init__(self, block, track):
        self.block = block
        self.track = track
        self.floorModelA = None
        self.floorModelB = None
        self.floorModelC = None
        self.floor = None
        self.elevatorFilename = None
        self.elevatorModel = None
        self.entranceElevator = None
        self.exitElevator = None
        self.numFloors = 0
        self.currentFloor = 0
        self.elevatorMusic = base.loader.loadMusic('phase_7/audio/bgm/tt_elevator.ogg')

    def enter(self):
        self.entranceElevator.openDoors(callback=self.enterFloor)

    def enterFloor(self):
        self.elevatorMusic.stop()
        base.localAvatar.wrtReparentTo(render)

    def loadFloor(self, floorModel):
        self.floor = loader.loadModel(floorModel)
        self.floor.reparentTo(render)
        self.elevatorModel = loader.loadModel(self.elevatorFilename)

    def unloadFloor(self):
        self.floor.removeNode()
        self.floor = None
        self.entranceElevator.delete()
        self.exitElevator.delete()

    def unload(self):
        self.unloadFloor()
        del self.floorModelA
        del self.floorModelB
        del self.floorModelC
        del self.floor
        del self.elevatorFilename
        del self.elevatorModel
        del self.entranceElevator
        del self.exitElevator
        del self.elevatorMusic

    def playElevator(self):
        base.camLens.setMinFov(ToontownGlobals.CBElevatorFov/(4./3.))
        base.localAvatar.reparentTo(self.entranceElevator.np)
        base.localAvatar.setPos(*ElevatorPoints[0])
        base.localAvatar.setHpr(180, 0, 0)
        base.localAvatar.setAnimState('neutral')
        camera.reparentTo(self.entranceElevator.np)
        camera.setH(180)
        camera.setPos(0, 14, 4)
        base.playMusic(self.elevatorMusic, looping=1, volume=0.8)
        track = Sequence(getRideElevatorInterval(ELEVATOR_NORMAL), Func(self.enter))
        track.start()
