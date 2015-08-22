from pandac.PandaModules import *
from ElevatorConstants import *
from ElevatorUtils import *
import Elevator
import SuitInteriorBase

class EliteInterior(SuitInteriorBase.SuitInteriorBase):

    def __init__(self, zoneId):
        SuitInteriorBase.SuitInteriorBase.__init__(self, zoneId)
        self.floorModelA = 'phase_11/models/lawbotHQ/LB_Zone04a'
        self.floorModelB = 'phase_5/models/cogdominium/tt_m_ara_cbr_barrelRoom'
        self.floorModelC = 'phase_5/models/cogdominium/tt_m_ara_crg_penthouse_law'
        self.entranceElevator = Elevator.Elevator(ELEVATOR_NORMAL)
        self.exitElevator = Elevator.Elevator(ELEVATOR_NORMAL)
        self.numFloors = 7
        self.intermissionMusic = base.loadMusic('phase_14/audio/bgm/elite_intermission.ogg')

    def enter(self):
        SuitInteriorBase.SuitInteriorBase.enter(self)

    def loadNextFloor(self):
        if self.floor:
            self.unloadFloor()
        if self.currentFloor in [0, 1, 3, 4]:
            self.loadFloorA()
        elif self.currentFloor in [2, 5]:
            self.loadFloorB()
        elif self.currentFloor == 6:
            self.loadFloorC()
        self.entranceElevator.forceCloseDoors()
        self.exitElevator.forceCloseDoors()
        self.playElevator()
        self.currentFloor += 1

    def loadFloorA(self):
        SuitInteriorBase.SuitInteriorBase.loadFloorA(self)
        self.entranceElevator.setup(self.floor.find('**/ENTRANCE'))
        self.entranceElevator.np.setH(180)
        self.exitElevator.setup(self.floor.find('**/EXIT'))

    def loadFloorB(self):
        SuitInteriorBase.SuitInteriorBase.loadFloorB(self)
        origin = self.floor.find('**/pasted__floor_light_1').getPos()
        self.entranceElevator.setup(render)
        self.entranceElevator.np.setPosHpr(origin, Vec3(180, 0, 0))
        self.floor.find('**/entranceElevator_GRP').removeNode()
        self.exitElevator.setup(self.floor.find('**/elevatorOut_locator'))
        self.floor.find('**/collision_GRP').setBin('ground', 18)

    def loadFloorC(self):
        SuitInteriorBase.SuitInteriorBase.loadFloorC(self)
        self.entranceElevator.setup(self.floor.find('**/elevatorIN_node'))
        self.exitElevator.setup(self.floor.find('**/elevatorOUT_node'))
