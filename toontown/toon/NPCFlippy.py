from panda3d.core import *
import NPCToon

class NPCFlippy(NPCToon.NPCToon):

    def __init__(self):
        NPCToon.NPCToon.__init__(self)
        self.setScale(1.25)

    def getCollSphereRadius(self):
        return 4
