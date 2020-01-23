from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from toontown.toonbase import TTLocalizer as TTL
from toontown.toontowngui import TTDialog
from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitDNA
from toontown.suit import Suit
from toontown.battle import SuitBattleGlobals
from toontown.toon import NPCToons

class DetailCogDialog(DirectFrame, StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('SummonCogDialog')
    notify.setInfo(True)

    def __init__(self, suitIndex):
        DirectFrame.__init__(self, parent=aspect2dp, pos=(0, 0, 0.3), relief=None, image=DGG.getDefaultDialogGeom(), image_scale=(1.6, 1, 0.7), image_pos=(0, 0, 0.18), image_color=ToontownGlobals.GlobalDialogColor, text=TTL.SummonDlgTitle, text_scale=0.12, text_pos=(0, 0.4), borderWidth=(0.01, 0.01), sortOrder=NO_FADE_SORT_INDEX)
        StateData.StateData.__init__(self, 'summon-cog-done')
        self.initialiseoptions(SummonCogDialog)
        self.suitIndex = suitIndex
        base.summonDialog = self
        self.popup = None
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
        z = self.head.getZ()
        self.head.setPos(-0.4, -0.1, z + 0.2)
        self.suitLabel = DirectLabel(parent=self, relief=None, text=self.suitFullName, text_font=ToontownGlobals.getSuitFont(), pos=(-0.4, 0, 0), scale=0.07)
        closeButtonImage = (gui.find('**/CloseBtn_UP'), gui.find('**/CloseBtn_DN'), gui.find('**/CloseBtn_Rllvr'))
        buttonImage = (guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
        disabledColor = Vec4(0.5, 0.5, 0.5, 1)
        self.summonSingleButton = DirectButton(parent=self, relief=None, text=TTL.SummonDlgButton1, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.06, text_pos=(0, -0.01), pos=(0.3, 0, 0.25), command=self.issueSummons, extraArgs=['single'])
        self.summonBuildingButton = DirectButton(parent=self, relief=None, text=TTL.SummonDlgButton2, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.06, text_pos=(0, -0.01), pos=(0.3, 0, 0.125), command=self.issueSummons, extraArgs=['building'])
        self.summonInvasionButton = DirectButton(parent=self, relief=None, text=TTL.SummonDlgButton3, image=buttonImage, image_scale=(1.7, 1, 1), image3_color=disabledColor, text_scale=0.06, text_pos=(0, -0.01), pos=(0.3, 0, 0.0), command=self.issueSummons, extraArgs=['invasion'])
        self.cancel = DirectButton(parent=self, relief=None, image=closeButtonImage, pos=(0.7, 0, -0.1), command=self.__cancel)
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
        self.disableButtons()
        self.enableButtons()
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
        messenger.send(self.doneEvent, [])
        return None

    def cleanupDialogs(self):
        self.head = None
        if self.popup != None:
            self.popup.cleanup()
            self.popup = None
        return

    def hideSummonButtons(self):
        self.summonSingleButton.hide()
        self.summonBuildingButton.hide()
        self.summonInvasionButton.hide()

    def __cancel(self):
        self.exit()
