from pandac.PandaModules import *
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
import random

class ToontownLoadingScreen:

    def __init__(self):
        self.__expectedCount = 0
        self.__count = 0

    # We can't access the holiday manager before initializing the loader, so we have to load the assets after the AI has started.

    def load(self):
        if base.air.holidayMgr.isWinter():
            self.gui = loader.loadModel('phase_3/models/gui/progress-background_christmas')
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo_christmas')
        elif base.air.holidayMgr.isHalloween():
            self.gui = loader.loadModel('phase_3/models/gui/progress-background_halloween')
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo_halloween')
        else:
            self.gui = loader.loadModel('phase_3/models/gui/progress-background')
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo')

        self.logo.reparentTo(self.gui)
        self.banner = loader.loadModel('phase_3/models/gui/toon_council').find('**/scroll')
        self.banner.reparentTo(self.gui)
        self.banner.setScale(0.4, 0.4, 0.4)
        self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.banner, relief=None, text='', text_scale=TTLocalizer.TLStip, text_font=ToontownGlobals.getInterfaceFont(), textMayChange=1, pos=(-1.2, 0.0, 0.1), text_fg=(0.4, 0.3, 0.2, 1), text_wordwrap=13, text_align=TextNode.ALeft)
        self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(-1.075, 0, -0.77), text='', textMayChange=1, text_scale=0.08, text_fg=(0.93, 0.26, 0.28, 1.0), text_align=TextNode.ALeft, text_font=ToontownGlobals.getSignFont())
        self.waitBar = DirectWaitBar(guiId='ToontownLoadingScreenWaitBar', parent=self.gui, frameSize=(-1.06,
         1.06,
         -0.03,
         0.03), pos=(0, 0, -0.85), text='')

    def unload(self):
        self.tip.destroy()
        self.title.destroy()
        self.waitBar.destroy()
        self.banner.removeNode()
        self.logo.removeNode()
        self.gui.removeNode()

    def getTip(self, tipCategory):
        return TTLocalizer.TipTitle + '\n' + random.choice(TTLocalizer.TipDict.get(tipCategory))

    def begin(self, range, label, tipCategory):
        base.adjustWindowAspectRatio(base.getAspectRatio())
        self.waitBar['range'] = range
        self.title['text'] = label
        self.tip['text'] = self.getTip(tipCategory)
        self.__count = 0
        self.__expectedCount = range
        self.logo.setPos(0, 0, 0.6)
        self.logo.setSz(0.8)
        self.gui.reparentTo(aspect2d, DGG.NO_FADE_SORT_INDEX)
        self.waitBar.update(self.__count)

    def end(self):
        base.adjustWindowAspectRatio(base.getAspectRatio())
        self.waitBar.finish(N=globalClock.getAverageFrameRate())
        self.waitBar.reparentTo(self.gui)
        self.title.reparentTo(self.gui)
        self.logo.reparentTo(self.gui)
        self.gui.reparentTo(hidden)
        return (self.__expectedCount, self.__count)

    def abort(self):
        self.gui.reparentTo(hidden)

    def tick(self):
        base.adjustWindowAspectRatio(base.getAspectRatio())
        self.__count = self.__count + 1
        self.waitBar.update(self.__count)
