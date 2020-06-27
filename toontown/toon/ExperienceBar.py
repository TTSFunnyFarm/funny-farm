from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
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
        frameImage = base.loader.loadModel('phase_14/models/gui/experience_bar')
        fillImage = base.loader.loadTexture('phase_14/maps/exp_bar_fill.jpg', 'phase_14/maps/exp_bar_fill_a.rgb')
        self.container['image'] = frameImage
        self.container.setPos(-0.5, 0, -0.44)
        self.bar = DirectWaitBar(parent=self.container, relief=None, value=self.exp, range=self.maxExp, pos=(0.5, 0, 0.502), scale=(0.5, 1, 6.85), barTexture=fillImage, barColor=(1.0, 1.0, 1.0, 1.0), sortOrder=1)
        self.bar.setTransparency(TransparencyAttrib.MAlpha)
        self.barText = DirectLabel(parent=self.container, relief=None, text="", text_font=ToontownGlobals.getSignFont(), pos=(0.5, 0, 0.485), scale=(0.037, 1, 0.037), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), sortOrder=2)
        frameImage.removeNode()

    def destroy(self):
        del self.bar
        del self.barText
        del self.av
        del self.exp
        del self.maxExp
        DirectFrame.destroy(self)

    def setExperience(self, exp, maxExp):
        oldExp = self.exp
        oldMaxExp = self.maxExp
        self.exp = exp
        if self.maxExp == 0:
            self.setNewMax(maxExp)
        animTrack = Sequence()
        expGained = exp - oldExp
        if expGained <= 0:
            if maxExp != oldMaxExp:
                animTrack.append(LerpFunctionInterval(self.moveBar, fromData=oldExp, toData=oldMaxExp, duration=1, blendType='easeIn'))
                animTrack.append(Func(self.setNewMax, maxExp))
                animTrack.append(LerpFunctionInterval(self.moveBar, fromData=0, toData=exp, duration=1, blendType='easeOut'))
            else:
                animTrack.append(LerpFunctionInterval(self.moveBar, fromData=oldExp, toData=exp, duration=2, blendType='easeInOut'))
        else:
            animTrack.append(LerpFunctionInterval(self.moveBar, fromData=oldExp, toData=exp, duration=2, blendType='easeInOut'))
        animTrack.start()

    def moveBar(self, data):
        self.bar['value'] = data
        ratio = self.bar['value'] / self.bar['range']
        self.bar.setTexScale(TextureStage.getDefault(), ratio, 1)
        self.barText['text'] = TTLocalizer.ToonPageExperience % (data, self.maxExp)

    def setNewMax(self, maxExp):
        self.maxExp = maxExp
        self.bar['range'] = maxExp
