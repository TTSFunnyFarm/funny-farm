from panda3d.core import *
from toontown.building.ElevatorConstants import *
from toontown.building.ElevatorUtils import *
from toontown.building.Elevator import Elevator
from toontown.building.SuitInteriorBase import SuitInteriorBase

class SuitInterior(SuitInteriorBase):

    def __init__(self, track, difficulty, numFloors):
        SuitInteriorBase.__init__(self, track)
        self.floorModelA = 'phase_7/models/modules/suit_interior'
        self.floorModelB = 'phase_7/models/modules/cubicle_room'
        self.floorModelC = 'phase_7/models/modules/boss_suit_office'
        self.elevatorFilename = 'phase_4/models/modules/elevator'
        self.entranceElevator = Elevator(ELEVATOR_NORMAL)
        self.exitElevator = Elevator(ELEVATOR_NORMAL)
        self.difficulty = difficulty
        self.numFloors = numFloors
        self.intermissionMusic = base.loader.loadMusic('phase_14/audio/bgm/elite_intermission.ogg')

    def enter(self):
        SuitInteriorBase.enter(self)

    def loadNextFloor(self):
        if self.floor:
            self.unloadFloor()
        if self.currentFloor == 1:
            self.loadFloorA()
        elif self.currentFloor < self.numFloors:
            self.loadFloorB()
        elif self.currentFloor == self.numFloors:
            self.loadFloorC()
        self.entranceElevator.forceCloseDoors()
        self.exitElevator.forceCloseDoors()
        self.playElevator()
        self.currentFloor += 1

    def loadFloorA(self):
        SuitInteriorBase.loadFloorA(self)
        self.entranceElevator.setup(self.elevatorModel.copyTo(hidden), self.floor.find('**/elevator-in'), self.track, self.difficulty, self.numFloors)
        self.exitElevator.setup(self.elevatorModel.copyTo(hidden), self.floor.find('**/elevator-out'), self.track, self.difficulty, self.numFloors)

    def loadFloorB(self):
        SuitInteriorBase.loadFloorB(self)
        self.entranceElevator.setup(self.elevatorModel.copyTo(hidden), self.floor.find('**/elevator-in'), self.track, self.difficulty, self.numFloors)
        self.exitElevator.setup(self.elevatorModel.copyTo(hidden), self.floor.find('**/elevator-out'), self.track, self.difficulty, self.numFloors)

    def loadFloorC(self):
        SuitInteriorBase.loadFloorC(self)
        self.entranceElevator.setup(self.elevatorModel.copyTo(hidden), self.floor.find('**/elevator-in'), self.track, self.difficulty, self.numFloors)
        self.exitElevator.setup(self.elevatorModel.copyTo(hidden), self.floor.find('**/elevator-out'), self.track, self.difficulty, self.numFloors)
