from panda3d.core import *
from direct.gui.DirectGui import *
from direct.gui import OnscreenText
from direct.interval.IntervalGlobal import *
from MakeAToonGlobals import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import *
from toontown.toon.LocalToon import LocalToon
from toontown.toontowngui import TTDialog
from direct.fsm import StateData
import os
import re

class NameShop(StateData.StateData):

    def __init__(self, doneEvent, index):
        StateData.StateData.__init__(self, doneEvent)
        self.index = index
        self.pickANameGUIElements = []
        self.typeANameGUIElements = []

    def enter(self, toon):
        self.notify.debug('enter')
        self.toon = toon
        self.ubershow(self.typeANameGUIElements)
        self.accept('next', self.__handleSubmit)
        self.acceptOnce('last', self.__handleBackward)

    def exit(self):
        self.notify.debug('exit')
        self.ignore('next')
        self.ignore('last')
        self.hideAll()
        self.nameEntry.enterText('')

    def load(self):
        nameBalloon = loader.loadModel('phase_3/models/props/chatbox_input')
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        self.arrowUp = gui.find('**/tt_t_gui_mat_namePanelArrowUp')
        self.arrowDown = gui.find('**/tt_t_gui_mat_namePanelArrowDown')
        self.arrowHover = gui.find('**/tt_t_gui_mat_namePanelArrowHover')
        self.squareUp = gui.find('**/tt_t_gui_mat_namePanelSquareUp')
        self.squareDown = gui.find('**/tt_t_gui_mat_namePanelSquareDown')
        self.squareHover = gui.find('**/tt_t_gui_mat_namePanelSquareHover')
        typePanel = gui.find('**/tt_t_gui_mat_typeNamePanel')
        self.typeNamePanel = DirectFrame(parent=aspect2d, image=None, relief='flat', scale=(0.75, 0.7, 0.7), state='disabled', pos=(-0.0163333, 0, 0.075), image_pos=(0, 0, 0.025), frameColor=(1, 1, 1, 0))
        self.typePanelFrame = DirectFrame(image=typePanel, relief='flat', frameColor=(1, 1, 1, 0), pos=(-0.008, 0, 0.019))
        self.typePanelFrame.reparentTo(self.typeNamePanel, sort=1)
        self.typeANameGUIElements.append(self.typeNamePanel)
        self.typeANameGUIElements.append(self.typePanelFrame)
        self.nameLabel = OnscreenText.OnscreenText(TTLocalizer.PleaseTypeName, parent=aspect2d, style=OnscreenText.ScreenPrompt, scale=TTLocalizer.NSnameLabel, pos=(-0.0163333, 0.53))
        self.nameLabel.wrtReparentTo(self.typeNamePanel, sort=2)
        self.typeANameGUIElements.append(self.nameLabel)
        self.typeNotification = OnscreenText.OnscreenText(TTLocalizer.AllNewNames, parent=aspect2d, style=OnscreenText.ScreenPrompt, scale=TTLocalizer.NStypeNotification, pos=(-0.0163333, 0.15))
        self.typeNotification.wrtReparentTo(self.typeNamePanel, sort=2)
        self.typeANameGUIElements.append(self.typeNotification)
        self.nameMessages = OnscreenText.OnscreenText(TTLocalizer.NameMessages, parent=aspect2d, style=OnscreenText.ScreenPrompt, scale=0.06, pos=(-0.0163333, -0.05))
        self.nameMessages.wrtReparentTo(self.typeNamePanel, sort=2)
        self.typeANameGUIElements.append(self.nameMessages)
        self.nameEntry = DirectEntry(parent=aspect2d, relief=None, scale=TTLocalizer.NSnameEntry, entryFont=getToonFont(), width=TTLocalizer.NSmaxNameWidth, numLines=2, focus=1, cursorKeys=1, pos=(0.0, 0.0, 0.39), text_align=TextNode.ACenter, autoCapitalize=1, command=self.__handleSubmit)
        self.nameEntry.wrtReparentTo(self.typeNamePanel, sort=2)
        self.typeANameGUIElements.append(self.nameEntry)
        self.submitButton = DirectButton(parent=aspect2d, relief=None, image=(self.squareUp,
         self.squareDown,
         self.squareHover,
         self.squareUp), image_scale=(1.2, 0, 1.1), pos=(-0.01, 0, -0.25), text=TTLocalizer.NameShopSubmitButton, text_scale=0.06, text_pos=(0, -0.02), command=self.__handleSubmit)
        self.submitButton.wrtReparentTo(self.typeNamePanel, sort=2)
        self.typeNamePanel.setPos(-0.42, 0, -0.078)
        self.typeANameGUIElements.append(self.submitButton)
        guiButton.removeNode()
        self.uberhide(self.typeANameGUIElements)

    def ubershow(self, guiObjectsToShow):
        for x in guiObjectsToShow:
            try:
                x.show()
            except:
                print 'NameShop: Tried to show already removed object'

    def hideAll(self):
        self.uberhide(self.pickANameGUIElements)
        self.uberhide(self.typeANameGUIElements)

    def uberhide(self, guiObjectsToHide):
        for x in guiObjectsToHide:
            try:
                x.hide()
            except:
                print 'NameShop: Tried to hide already removed object'

    def uberdestroy(self, guiObjectsToDestroy):
        for x in guiObjectsToDestroy:
            try:
                x.destroy()
                del x
            except:
                print 'NameShop: Tried to destroy already removed object'

    def reviewName(self, name):
        blacklistFile = 'resources/phase_4/etc/tblacklist.dat'
        with open(blacklistFile) as blacklist:
            badWords = blacklist.read().title().split()
            nameWords = re.sub('[^\w]', ' ',  name).split()
            for word in nameWords:
                if word in badWords:
                    self.rejectName()
                    return
            if len(name) < 3 or len(nameWords) > 4:
                self.rejectName()
                return
            if name == 'Rocky Reborn':
                self.rockyDialog()
                return
            self.createAvatar()
            self.promptTutorial()

    def rejectName(self):
        self.rejectDialog = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.RejectNameText, style=TTDialog.Acknowledge, command=self.cleanupRejectDialog)
        self.rejectDialog.show()

    def cleanupRejectDialog(self, *args):
        self.rejectDialog.destroy()
        self.rejectDialog = None

    def rockyDialog(self):
        self.rockyDialog = TTDialog.TTDialog(parent=aspect2dp, text='Rocky Reborn is playing my game? What a\nstrong soldier!', text_align=TextNode.ACenter, style=TTDialog.Acknowledge, command=self.cleanupRockyDialog)
        self.rockyDialog.show()

    def cleanupRockyDialog(self, *args):
        self.rockyDialog.destroy()
        del self.rockyDialog
        self.createAvatar()
        self.promptTutorial()

    def createAvatar(self):
        self.dna = self.toon.getRawDNA()
        self.toonData = dataMgr.createToonData(self.index, self.dna, self.name)
        dataMgr.saveToonData(self.toonData)
        dataMgr.createLocalAvatar(self.toonData)

    def __handleSubmit(self, *args):
        self.name = self.nameEntry.get()
        Sequence(Func(self.waitForServer), Wait(1), Func(self.cleanupWaitForServer), Func(self.reviewName, self.name)).start()

    def __handleDone(self, tutorial = 0):
        if tutorial == 1:
            self.doneStatus = 'done-tutorial'
        else:
            self.doneStatus = 'done'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def waitForServer(self):
        self.waitForServerDialog = TTDialog.TTDialog(text=TTLocalizer.WaitingForNameSubmission, style=TTDialog.NoButtons)
        self.waitForServerDialog.show()

    def cleanupWaitForServer(self):
        if self.waitForServerDialog != None:
            self.waitForServerDialog.cleanup()
            self.waitForServerDialog = None
        return

    def promptTutorial(self):
        self.promptTutorialDialog = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.PromptTutorial, text_scale=0.06, text_align=TextNode.ACenter, text_wordwrap=22, command=self.__openTutorialDialog, fadeScreen=0.5, style=TTDialog.TwoChoice, buttonTextList=[TTLocalizer.MakeAToonEnterTutorial, TTLocalizer.MakeAToonSkipTutorial], button_text_scale=0.06, buttonPadSF=5.5, sortOrder=DGG.NO_FADE_SORT_INDEX)
        self.promptTutorialDialog.show()

    def __openTutorialDialog(self, choice = 0):
        self.promptTutorialDialog.destroy()
        self.__handleDone(choice)
