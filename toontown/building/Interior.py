from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject

class Interior(DirectObject):
    notify = directNotify.newCategory('Interior')

    def __init__(self):
        self.interiorFile = None

    def load(self):
        self.interior = loader.loadModel(self.interiorFile)
        self.interior.reparentTo(render)

    def unload(self):
        self.ignoreAll()
        self.interior.removeNode()
        del self.interior

    def setupDoor(self, name, node):
        door = loader.loadModel('phase_3.5/models/modules/doors_practical').find('**/' + name)
        door.reparentTo(self.interior.find('**/' + node))
        return door

    def fixDoor(self, door):
        name = door.getName()
        door.find('**/' + name + '_hole_left').setColor(0, 0, 0, 1)
        door.find('**/' + name + '_hole_right').setColor(0, 0, 0, 1)
        door.find('**/' + name + '_right').setDepthOffset(1)
        door.find('**/' + name + '_left').setDepthOffset(1)
        door.setDepthOffset(1)
        door.find('**/' + name + '_trigger').setY(-0.24)
