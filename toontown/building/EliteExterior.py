from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from ElevatorConstants import *
import Elevator

class EliteExterior(DirectObject):

    def __init__(self):
        self.modelPath = 'phase_5/models/cogdominium/tt_m_ara_cbe_fieldOfficeLegalEagle'
        self.elevator = Elevator.Elevator(ELEVATOR_NORMAL)

    def load(self):
        self.geom = loader.loadModel(self.modelPath)
        self.geom.reparentTo(render)
        self.elevator.setup(self.geom.find('**/lbfo_door_origin'))
        self.elevator.addActive()

    def unload(self):
        self.elevator.delete()
        self.geom.removeNode()
        del self.elevator
        del self.geom

    def setPos(self, x, y, z):
        self.geom.setPos(x, y, z)

    def setHpr(self, h, p, r):
        self.geom.setHpr(h, p, r)

    def setPosHpr(self, x, y, z, h, p, r):
        self.geom.setPosHpr(x, y, z, h, p, r)
