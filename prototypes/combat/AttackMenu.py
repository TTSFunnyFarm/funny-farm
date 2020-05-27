from direct.gui.DirectGui import *
from panda3d.core import *
class AttackMenu(DirectFrame):
    def __init__(self):
        DirectFrame.__init__(self, relief=None, geom=DGG.getDefaultDialogGeom(), geom_scale=(1, 1, 0.5), pos=(0, 0, 0))
        self.initialiseoptions(AttackMenu)
        #self.setBin('gui-popup', 0)
