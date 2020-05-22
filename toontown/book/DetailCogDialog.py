from direct.gui.DirectGui import *
from direct.gui.DirectGuiGlobals import *
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from toontown.toonbase import TTLocalizer as TTL
from toontown.toontowngui import TTDialog
from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitDNA
from toontown.suit import Suit
from toontown.battle import SuitBattleGlobals
from toontown.toon import NPCToons

class DetailCogDialog(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('DetailCogDialog')
    notify.setInfo(True)

    def __init__(self, suitIndex):
        DirectFrame.__init__(self, parent=aspect2dp, pos=(0, 0, 0.3), relief=None, image=DGG.getDefaultDialogGeom(), image_scale=(1.6, 1, 0.7), image_pos=(0, 0, 0.18), image_color=ToontownGlobals.GlobalDialogColor, text='Details', text_scale=0.12, text_pos=(0, 0.4), borderWidth=(0.01, 0.01), sortOrder=2000)
        self.initialiseoptions(DetailCogDialog)
        self.suitIndex = suitIndex
        self.popup = None
        self.isLoaded = 0
        self.isEntered = 0
        self.suitName = SuitDNA.suitHeadTypes[self.suitIndex]
        self.suitFullName = SuitBattleGlobals.SuitAttributes[self.suitName]['name']
        return

    def unload(self):
        if self.isLoaded == 0:
            return None
        self.isLoaded = 0
        self.exit()
        DirectFrame.destroy(self)
        return None

    def load(self):
        if self.isLoaded == 1:
            return None
        self.isLoaded = 1
        gui = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.head = Suit.attachSuitHead(self, self.suitName)
        z = self.head.getZ() + 0.2
        self.head.setPos(-0.5, -0.1, z)
        if settings['antialiasing']:
            self.head.setAntialias(AntialiasAttrib.MAuto)
        cogCounts = base.localAvatar.getCogCounts()
        skelecogCounts = base.localAvatar.getSkeleCounts()
        eliteCounts = base.localAvatar.getEliteCounts()
        self.suitLabel = DirectLabel(parent=self, relief=None, text=self.suitFullName, text_font=ToontownGlobals.getSuitFont(), pos=(-0.5, 0, -0.04), scale=0.07)
        self.cogsKilled = DirectLabel(parent=self, relief=None, text="Standard Destroyed: {}".format(cogCounts[self.suitIndex]), pos=(0.03, 0, 0.25), scale=0.06, text_align=TextNode.ACenter)
        self.skelecogsKilled = DirectLabel(parent=self, relief=None, text="Skelecogs Destroyed: {}".format(skelecogCounts[self.suitIndex]), pos=(0.03, 0, 0.15), scale=0.06, text_align=TextNode.ACenter)
        self.elitesKilled = DirectLabel(parent=self, relief=None, text="Elites Destroyed: {}".format(eliteCounts[self.suitIndex]), pos=(0.03, 0, 0.05), scale=0.06, text_align=TextNode.ACenter)
        closeButtonImage = (gui.find('**/CloseBtn_UP'), gui.find('**/CloseBtn_DN'), gui.find('**/CloseBtn_Rllvr'))
        buttonImage = (guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
        disabledColor = Vec4(0.5, 0.5, 0.5, 1)
        self.cancel = DirectButton(parent=self, relief=None, image=closeButtonImage, pos=(0.7, 0, -0.165), command=self.__cancel)
        gui.removeNode()
        guiButton.removeNode()
        self.hide()
        return

    def enter(self):
        if self.isEntered == 1:
            return None
        self.isEntered = 1
        if self.isLoaded == 0:
            self.load()
        self.popup = None
        base.transitions.fadeScreen(0.5)
        self.show()
        return

    def exit(self):
        if self.isEntered == 0:
            return None
        self.isEntered = 0
        self.cleanupDialogs()
        base.transitions.noTransitions()
        self.ignoreAll()
        self.hide()
        return None

    def cleanupDialogs(self):
        self.head = None
        if self.popup != None:
            self.popup.cleanup()
            self.popup = None
        return

    def __cancel(self):
        self.exit()
