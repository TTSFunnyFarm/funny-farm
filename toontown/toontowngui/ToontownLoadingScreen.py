from pandac.PandaModules import *
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import FFTime
import random

class ToontownLoadingScreen:

    def __init__(self):
        self.__expectedCount = 0
        self.__count = 0
        self.initGui = loader.loadModel('phase_3/models/gui/loading-background')
        self.initGui.reparentTo(aspect2d, 0)
        self.initGui.hide()
        self.initBg = self.initGui.find('**/bg')
        self.initBg.reparentTo(render2d)
        self.initBg.hide()
        self.initGui.find('**/fg').setScale(render2d, VBase3(1))
        self.initGui.find('**/bar_shadow').setScale(render2d, VBase3(1))
        self.initGui.find('**/fg').setBin('fixed', 20)
        
        if FFTime.isWinter():
            self.gui = loader.loadModel('phase_3/models/gui/progress-background_christmas')
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo_christmas')
            self.initGui.find('**/fg').setTexture(loader.loadTexture('phase_3/maps/toontown-logo_christmas.jpg', 'phase_3/maps/toontown-logo_a.rgb'), 1)
        elif FFTime.isHalloween():
            self.gui = loader.loadModel('phase_3/models/gui/progress-background_halloween')
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo_halloween')
            self.initGui.find('**/fg').setTexture(loader.loadTexture('phase_3/maps/toontown-logo_halloween.jpg', 'phase_3/maps/toontown-logo_a.rgb'), 1)
        else:
            self.gui = loader.loadModel('phase_3/models/gui/progress-background')
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo')
        
        self.logo.reparentTo(self.gui)
        self.banner = loader.loadModel('phase_3/models/gui/toon_council').find('**/scroll')
        self.banner.reparentTo(self.gui)
        self.banner.setScale(0.4, 0.4, 0.4)
        self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.banner, relief=None, text='', text_scale=TTLocalizer.TLStip, text_font=ToontownGlobals.getInterfaceFont(), textMayChange=1, pos=(-1.2, 0.0, 0.1), text_fg=(0.4, 0.3, 0.2, 1), text_wordwrap=13, text_align=TextNode.ALeft)
        self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(-1.1, 0, -0.77), text='', textMayChange=1, text_scale=0.08, text_fg=(0.93, 0.26, 0.28, 1.0), text_align=TextNode.ALeft, text_font=ToontownGlobals.getSignFont())
        self.waitBar = DirectWaitBar(guiId='ToontownLoadingScreenWaitBar', parent=self.gui, frameSize=(-1.06,
         1.06,
         -0.03,
         0.03), pos=(0, 0, -0.85), text='')

    def destroy(self):
        self.tip.destroy()
        self.title.destroy()
        self.waitBar.destroy()
        self.banner.removeNode()
        self.logo.removeNode()
        self.gui.removeNode()
    
    def getTip(self, tipCategory):
        return TTLocalizer.TipTitle + '\n' + random.choice(TTLocalizer.TipDict.get(tipCategory))
    
    def resetSettings(self):
        self.title.setPos(-1.1, 0, -0.77)
        self.title['text_align'] = TextNode.ALeft
        self.title['text_scale'] = 0.08

    def begin(self, range, label, tipCategory):
        self.waitBar['range'] = range
        self.title['text'] = label
        self.tip['text'] = self.getTip(tipCategory)
        self.__count = 0
        self.__expectedCount = range
        self.logo.setPos(0, 0, 0.6)
        self.logo.setSz(0.8)
        self.gui.reparentTo(aspect2dp, NO_FADE_SORT_INDEX)
        self.waitBar.update(self.__count)

    def beginInit(self):
        self.waitBar['range'] = 100
        self.title.setPos(0, 0, -0.77)
        self.title['text'] = 'Loading. . .'
        self.title['text_align'] = TextNode.ACenter
        self.title['text_scale'] = 0.13
        self.__count = 0
        self.__expectedCount = 100
        self.initGui.show()
        self.initBg.show()
        self.title.reparentTo(aspect2dp, NO_FADE_SORT_INDEX)
        self.waitBar.reparentTo(aspect2dp, NO_FADE_SORT_INDEX)
        self.waitBar.update(self.__count)

    def end(self):
        self.waitBar.finish(N=30)
        self.waitBar.reparentTo(self.gui)
        self.title.reparentTo(self.gui)
        self.logo.reparentTo(self.gui)
        self.gui.reparentTo(hidden)
        self.initGui.hide()
        self.initBg.hide()
        self.resetSettings()
        return (self.__expectedCount, self.__count)

    def abort(self):
        self.gui.reparentTo(hidden)

    def tick(self):
        self.__count = self.__count + 1
        self.waitBar.update(self.__count)


