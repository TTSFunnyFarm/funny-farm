from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownGlobals
from ElevatorConstants import *
from ElevatorUtils import *

class SuitInteriorBase(DirectObject):
    notify = directNotify.newCategory('SuitInterior')

    def __init__(self, zoneId):
        self.zoneId = zoneId
        self.floorModelA = None
        self.floorModelB = None
        self.floorModelC = None
        self.floor = None
        self.entranceElevator = None
        self.exitElevator = None
        self.numFloors = 0
        self.currentFloor = 0
        self.waitMusic = base.loader.loadMusic('phase_7/audio/bgm/encntr_toon_winning_indoor.ogg')
        self.elevatorMusic = base.loader.loadMusic('phase_7/audio/bgm/tt_elevator.ogg')

    def enter(self):
        self.entranceElevator.openDoors(callback=self.exitTheElevator)

    def exitTheElevator(self):
        # This is where we would normally start the cog battle.
        base.localAvatar.wrtReparentTo(render)
        self.entranceElevator.hopOff(0, True)
        self.elevatorMusic.stop()
        self.exitElevator.openDoors()
        self.exitElevator.addActive()

    def loadFloorA(self):
        self.floor = loader.loadModel(self.floorModelA)
        self.floor.reparentTo(render)

    def loadFloorB(self):
        self.floor = loader.loadModel(self.floorModelB)
        self.floor.reparentTo(render)

    def loadFloorC(self):
        self.floor = loader.loadModel(self.floorModelC)
        self.floor.reparentTo(render)

    def unloadFloor(self):
        self.floor.removeNode()
        del self.floor
        self.entranceElevator.delete()
        self.exitElevator.delete()

    def unload(self):
        self.unloadFloor()
        del self.entranceElevator
        del self.exitElevator

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
