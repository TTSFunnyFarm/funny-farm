from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

class Interior(DirectObject):
    notify = directNotify.newCategory('Interior')

    def __init__(self):
        self.interiorFile = None

    def load(self):
        self.interior = loader.loadModel(self.interiorFile)
        self.interior.reparentTo(render)
        musicMgr.playCurrentZoneMusic()

    def unload(self):
        musicMgr.stopMusic()
        self.ignoreAll()
        self.interior.removeNode()
        del self.interior

    def setupDoor(self, name, node):
        door = loader.loadModel('phase_3.5/models/modules/doors_practical').find('**/' + name)
        door.reparentTo(self.interior.find('**/' + node))
        return door

    def fixDoor(self, door):
        door.find('**/door_*_hole_left').setColor(0, 0, 0, 1)
        door.find('**/door_*_hole_right').setColor(0, 0, 0, 1)
        door.find('**/door_*_flat').setDepthOffset(1)
        door.find('**/door_*_hole_left').setDepthOffset(2)
        door.find('**/door_*_hole_right').setDepthOffset(2)
        door.find('**/door_*_left').setDepthOffset(3)
        door.find('**/door_*_right').setDepthOffset(3)
        door.find('**/door_*_trigger').setY(-0.24)
        door.setDepthOffset(1)
