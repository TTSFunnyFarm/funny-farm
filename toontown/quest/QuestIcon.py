from panda3d.core import *
from direct.interval.IntervalGlobal import *

OFFER = 0
MAIN = 1
BONUS = 2

class QuestIcon(NodePath):

    def __init__(self, typeId = OFFER):
        NodePath.__init__(self, 'QuestIcon_%d_%d' % (typeId, id(self)))
        self.type = typeId
        self.track = None
        self.load()

    def load(self):
        gui = loader.loadModel('phase_14/models/props/quest_icons')
        iconPath = {
         OFFER: '**/quest_icon_offer',
         MAIN: '**/quest_icon_main',
         BONUS: '**/quest_icon_bonus'
        }
        geom = gui.find(iconPath[self.type])
        geom.reparentTo(self)
        gui.removeNode()

    def unload(self):
        if self.track:
            self.stop()
        self.removeNode()

    def start(self):
        self.track = Sequence()
        self.track.append(LerpPosInterval(self, duration=1.0, pos=Point3(self.getX(self.getParent()), self.getY(self.getParent()), self.getZ(self.getParent()) + 0.5), blendType='easeInOut'))
        self.track.append(LerpPosInterval(self, duration=1.0, pos=Point3(self.getX(self.getParent()), self.getY(self.getParent()), self.getZ(self.getParent())), blendType='easeInOut'))
        self.track.loop()

    def stop(self):
        self.track.finish()
        del self.track
