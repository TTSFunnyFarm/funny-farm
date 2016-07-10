from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
from toontown.toon import ToonHead
from toontown.toon import ToonDNA
import sys

MAX_AVATARS = 6
POSITIONS = (Vec3(-0.840167, 0, 0.359333),
 Vec3(0.00933349, 0, 0.306533),
 Vec3(0.862, 0, 0.3293),
 Vec3(-0.863554, 0, -0.445659),
 Vec3(0.00999999, 0, -0.5181),
 Vec3(0.864907, 0, -0.445659))
NAME_ROTATIONS = (7, -11, 1, -5, 3.5, -5)
NAME_POSITIONS = ((0, 0, 0.26),
 (-0.03, 0, 0.25),
 (0, 0, 0.27),
 (-0.03, 0, 0.25),
 (0.03, 0, 0.26),
 (0, 0, 0.26))
DELETE_POSITIONS = ((0.187, 0, -0.26),
 (0.31, 0, -0.167),
 (0.231, 0, -0.241),
 (0.314, 0, -0.186),
 (0.243, 0, -0.233),
 (0.28, 0, -0.207))

class AvatarChooser:

    def __init__(self):
        self.isLoaded = 0

    def enter(self):
        if not self.isLoaded:
            self.load()
        self.bg.show()
        self.quitButton.show()
        base.transitions.fadeScreen(1.0)
        base.transitions.fadeIn(1.0)
        if base.air.holidayMgr.isWinter():
            base.setBackgroundColor(Vec4(0.682, 0.847, 0.99, 1))
        elif base.air.holidayMgr.isHalloween():
            base.setBackgroundColor(Vec4(0.118, 0.118, 0.118, 1))
        else:
            base.setBackgroundColor(Vec4(0.145, 0.368, 0.78, 1))

    def exit(self):
        if not self.isLoaded:
            return
        self.unload()
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        musicMgr.stopMusic()

    def load(self):
        if self.isLoaded:
            return
        self.buttons = []
        if base.air.holidayMgr.isWinter():
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_christmas')
        elif base.air.holidayMgr.isHalloween():
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_halloween')
        else:
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui')
        gui.flattenMedium()
        bgImage = gui.find('**/tt_t_gui_pat_background')
        btnImages = [
            gui.find('**/tt_t_gui_pat_squareRed'),
            gui.find('**/tt_t_gui_pat_squareGreen'),
            gui.find('**/tt_t_gui_pat_squarePurple'),
            gui.find('**/tt_t_gui_pat_squareBlue'),
            gui.find('**/tt_t_gui_pat_squarePink'),
            gui.find('**/tt_t_gui_pat_squareYellow')
        ]
        quitGui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui')
        quitHover = quitGui.find('**/QuitBtn_RLVR')
        trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui')
        trashClsd = trashcanGui.find('**/TrashCan_CLSD')
        trashOpen = trashcanGui.find('**/TrashCan_OPEN')
        trashRlvr = trashcanGui.find('**/TrashCan_RLVR')
        self.bg = DirectFrame(image=bgImage, relief=None)
        self.bg.hide()
        self.title = OnscreenText(TTLocalizer.AvatarChooserPickAToon, scale=TTLocalizer.ACtitle, parent=self.bg, font=ToontownGlobals.getSignFont(), fg=(1, 0.9, 0.1, 1), pos=(0.0, 0.82))
        
        for i in xrange(0, MAX_AVATARS):
            button = DirectButton(parent=self.bg, image=btnImages[i], relief=None, pos=POSITIONS[i], scale=1.01, text=(TTLocalizer.AvatarChoiceMakeAToon,), text_scale=0.1, text_font=ToontownGlobals.getSignFont(), text_fg=(0, 1, 0.8, 0.5), text1_scale=TTLocalizer.ACmakeAToon, text1_font=ToontownGlobals.getSignFont(), text1_fg=(0, 1, 0.8, 1), text2_scale=TTLocalizer.ACmakeAToon, text2_font=ToontownGlobals.getSignFont(), text2_fg=(0.3, 1, 0.9, 1), command=self.__handleCreate, extraArgs=[i + 1])
            button.delete = DirectButton(parent=button, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[i], scale=0.45, command=self.__handleDelete, extraArgs=[i + 1])
            button.delete.hide()
            self.buttons.append(button)

        self.quitButton = DirectButton(parent=self.bg, image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserQuit, text_font=ToontownGlobals.getSignFont(), text_fg=(0.977, 0.816, 0.133, 1), text_pos=TTLocalizer.ACquitButtonPos, text_scale=TTLocalizer.ACquitButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(1.08, 0, -0.907), command=base.userExit)
        self.loadAvatars()
        gui.removeNode()
        quitGui.removeNode()
        trashcanGui.removeNode()
        self.isLoaded = 1
        return

    def unload(self):
        if not self.isLoaded:
            return
        for button in self.buttons:
            self.buttons.remove(button)
            button.destroy()
            button.delete.destroy()
        del self.buttons
        self.bg.destroy()
        del self.bg
        self.title.removeNode()
        del self.title
        self.quitButton.destroy()
        del self.quitButton
        self.isLoaded = 0

    def loadAvatars(self):
        if dataMgr.checkToonFiles():
            for i in xrange(0, MAX_AVATARS):
                data = dataMgr.loadToonData(i + 1)
                if data != None:
                    self.displayHead(data, self.buttons[i])

    def displayHead(self, data, button):
        head = hidden.attachNewNode('head')
        head.setPosHprScale(0, 5, -0.1, 180, 0, 0, 0.24, 0.24, 0.24)
        head.reparentTo(button.stateNodePath[0], 20)
        head.instanceTo(button.stateNodePath[1], 20)
        head.instanceTo(button.stateNodePath[2], 20)
        headModel = ToonHead.ToonHead()
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(*data.setDNA)
        headModel.setupHead(dna, forGui=1)
        headModel.reparentTo(head)
        animalStyle = dna.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
        headModel.setScale(bodyScale / 0.75)
        headModel.startBlink()
        headModel.startLookAround()

        nameText = DirectLabel(parent=button, text=data.setName, relief=None, scale=0.08, pos=NAME_POSITIONS[data.index - 1], hpr=(0, 0, NAME_ROTATIONS[data.index - 1]), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_wordwrap=8, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
        button.name = data.setName
        button['command'] = self.__handleChoice
        button['extraArgs'] = [data]
        button['text'] = ('', TTLocalizer.AvatarChoicePlayThisToon, TTLocalizer.AvatarChoicePlayThisToon)
        button['text_scale'] = TTLocalizer.ACplayThisToon
        button['text_fg'] = (1, 0.9, 0.1, 1)
        button.delete.show()

    def __handleCreate(self, index):
        base.transitions.fadeOut()
        Sequence(Wait(1), Func(base.cr.enterCreateAvatar, index)).start()

    def __handleChoice(self, data):
        base.transitions.fadeOut()
        Sequence(Wait(1), Func(self.__handleDone, data)).start()

    def __handleDelete(self, index):
        name = self.buttons[index - 1].name
        self.verify = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.AvatarChoiceDeleteConfirm % name, style=TTDialog.TwoChoice, command=self.__handleVerifyDelete, extraArgs=[index])
        self.verify.show()

    # Let's just spam the user with dialogs and piss them off

    def __handleVerifyDelete(self, choice, index):
        self.verify.destroy()
        del self.verify
        if choice == 1:
            self.confirm = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.AvatarChoiceVerifyDelete, style=TTDialog.TwoChoice, command=self.__handleConfirmDelete, extraArgs=[index])
            self.confirm.show()

    def __handleConfirmDelete(self, choice, index):
        self.confirm.destroy()
        del self.confirm
        if choice == 1:
            self.seriously = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.AvatarChoiceSeriously, style=TTDialog.TwoChoice, command=self.__handleSeriously, extraArgs=[index])
            self.seriously.show()

    def __handleSeriously(self, choice, index):
        self.seriously.destroy()
        del self.seriously
        if choice == 1:
            self.stop = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.AvatarChoiceStop, style=TTDialog.TwoChoice, command=self.__handleStop, extraArgs=[index])
            self.stop.show()

    def __handleStop(self, choice, index):
        self.stop.destroy()
        del self.stop
        if choice == 1:
            self.positive = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.AvatarChoicePositive, style=TTDialog.TwoChoice, command=self.__handlePositive, extraArgs=[index])
            self.positive.show()

    def __handlePositive(self, choice, index):
        self.positive.destroy()
        del self.positive
        if choice == 1:
            self.lastChance = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.AvatarChoiceLastChance, style=TTDialog.TwoChoice, command=self.__handleLastChance, extraArgs=[index])
            self.lastChance.show()

    def __handleLastChance(self, choice, index):
        self.lastChance.destroy()
        del self.lastChance
        if choice == 1:
            dataMgr.deleteToonData(index)
            # Hacky way of updating the gui
            self.unload()
            self.load()
            self.enter()

    def __handleDone(self, data):
        loader.beginBulkLoad('main', TTLocalizer.EnteringLabel, 1000, TTLocalizer.TIP_GENERAL)
        dataMgr.createLocalAvatar(data)
        base.cr.exitChooseAvatar()
        loader.endBulkLoad('main')
        base.cr.enterTheTooniverse(data.setLastHood)
