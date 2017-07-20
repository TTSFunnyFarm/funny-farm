from toontown.building import Building

class House(Building.Building):
    def __init__(self, zoneId, idx):
        Building.Building.__init__(self, zoneId)
        self.houseModel = 'phase_5.5/models/estate/houseB'
        self.model = None
        self.index = idx
        self.door = None

    def load(self):
        self.model = loader.loadModel(self.houseModel)
        self.model.setName('tb0{0}:toon_landmark_house'.format(self.index))
        self.model.flattenMedium()
        self.setupDoor()
        Building.Building.load(self)

    def unload(self):
        Building.Building.unload(self)
        self.door.removeNode()
        self.door = None
        self.model.removeNode()
        self.model = None

    def getBuildingNodePath(self):
        return self.model

    def setupDoor(self):
        self.notify.debug('setupDoor')
        doorModelName = 'door_double_round_ur'
        door = loader.loadModel('phase_3.5/models/modules/doors_practical').find('**/' + doorModelName)
        door_origin = self.model.find('**/door_origin')
        door_origin.setHpr(90, 0, 0)
        door_origin.setScale(0.6, 0.6, 0.8)
        door_origin.setPos(door_origin, 0.5, 0, 0.0)
        door.reparentTo(door_origin)
        self.door_origin = door_origin
        doorTrigger = door.find('**/' + doorModelName + '_trigger')
        doorTrigger.setName('door_trigger_{0}'.format(self.index))
        houseColor = (0.651, 0.376, 0.31)
        door.setColor(houseColor[0], houseColor[1], houseColor[2], 1)
        door.find('**/door_*_hole_left').setColor(0, 0, 0, 1)
        door.find('**/door_*_hole_right').setColor(0, 0, 0, 1)
        door.find('**/door_*_hole_left').setDepthOffset(1)
        door.find('**/door_*_hole_right').setDepthOffset(1)
        self.door = door
        # self.__setupNamePlate()
        # self.__setupFloorMat()
        # self.__setupNametag()
