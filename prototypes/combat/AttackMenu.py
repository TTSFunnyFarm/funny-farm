from direct.gui.DirectGui import *
from panda3d.core import *
class AttackMenu(DirectFrame):
    def __init__(self):
        DirectFrame.__init__(self, relief=None, image=DGG.getDefaultDialogGeom(), image_scale=(1.0, 1, 0.5))
        #self.setBin('gui-popup', 0)
