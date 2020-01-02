from panda3d.core import *
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import FunnyFarmGlobals

class ExperienceBar(DirectFrame):

    def __init__(self, av):
        DirectFrame.__init__(self, relief=None, sortOrder=50)
        self.initialiseoptions(ExperienceBar)
        self.av = av
        self.container = DirectFrame(parent=self, relief=None)
        self.exp = 0
        self.maxExp = 0
        self.load()
        self.setExperience(self.av.getLevelExp(), self.av.getMaxLevelExp())

    def load(self):
        frameImage = loader.loadModel('phase_3/models/props/chatbox_input.bam')
        self.container['image'] = frameImage
        self.container['image_color'] = (0.5, 1, 0.6, 1)
        self.container.setPos(-0.37, 0, 0.04)
        self.container.setScale(0.08, 1, 0.02)
        self.bar = DirectWaitBar(parent=self.container, relief=DGG.SUNKEN, value=self.exp, range=self.maxExp, barColor=(0.5, 1, 0.6, 1), pos=(4.49, 0, 0.5), scale=(4.55, 1, 13.5), frameColor=(0.98, 1, 0.75, 1))
        self.barText = DirectLabel(parent=self.bar, relief=None, text="", text_font=ToontownGlobals.getMinnieFont(), pos=(0, 0, -0.05), scale=(0.08, 1, 0.12))
        frameImage.removeNode()

    def destroy(self):
        del self.bar
        del self.barText
        del self.av
        del self.exp
        del self.maxExp
        DirectFrame.destroy(self)

    def setExperience(self, exp, maxExp):
        self.exp = exp
        self.maxExp = maxExp
        self.bar['range'] = self.maxExp
        self.bar['value'] = self.exp
        maxed = FunnyFarmGlobals.LevelExperience[FunnyFarmGlobals.ToonLevelCap - 1]
        if self.exp == maxed and self.maxExp == maxed:
            self.barText['text'] = 'MAX'
        else:
            self.barText['text'] = TTLocalizer.ToonPageExperience % (self.exp, self.maxExp)
