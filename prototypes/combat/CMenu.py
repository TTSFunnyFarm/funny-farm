from direct.gui.DirectGui import *
from panda3d.core import *
class CMenu(DirectFrame):
    def __init__(self):
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        DirectFrame.__init__(self, parent=hidden, relief=None, geom=DGG.getDefaultDialogGeom(), geom_scale=(1, 1, 0.5), pos=(0, 0, 0))
        self.initialiseoptions(CMenu)
        buttonImage = (guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
        buttonScale = (0.91, 1, 1.3)
        self.attackButton = DirectButton(parent=self, relief=None, image=buttonImage, image_scale=buttonScale, text="Attack", pos=(-0.26, 0, 0.12), text_scale=0.08, text_pos=(0, -0.02), command=print)
        self.passButton = DirectButton(parent=self, relief=None, image=buttonImage, image_scale=buttonScale, text="Pass", pos=(0.2, 0, 0.12), text_scale=0.08, text_pos=(0, -0.02), command=print)
        self.itemsButton = DirectButton(parent=self, relief=None, image=buttonImage, image_scale=buttonScale, text="Items", pos=(-0.26, 0, -0.12), text_scale=0.08, text_pos=(0, -0.02), command=print)
        self.runButton = DirectButton(parent=self, relief=None, image=buttonImage, image_scale=buttonScale, text="Run", pos=(0.2, 0, -0.12), text_scale=0.08, text_pos=(0, -0.02), command=print)
        guiButton.removeNode()
        #self.setBin('gui-popup', 0)
