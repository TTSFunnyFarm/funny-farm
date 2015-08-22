from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import FFTime
from toontown.toontowngui import TTDialog
from toontown.toon import ToonHead
from toontown.toon import ToonDNA
from toontown.makeatoon.MakeAToon import MakeAToon
import sys

NAME_ROTATIONS = (-11, 7, 1, 3.5, -5, -5)
NAME_POSITIONS = ((-0.03, 0, 0.25),
 (0, 0, 0.26),
 (0, 0, 0.27),
 (0.03, 0, 0.26),
 (-0.03, 0, 0.25),
 (0, 0, 0.26))
DELETE_POSITIONS = ((0.31, 0, -0.167),
 (0.187, 0, -0.26),
 (0.231, 0, -0.241),
 (0.243, 0, -0.233),
 (0.314, 0, -0.186),
 (0.28, 0, -0.207))

class PickAToon:

    def __init__(self):
        self.choice = None
        self.isLoaded = False
        self.avList = []
        self.mat = None
        self.posList = [
                (0.008, 0, 0.305),
                (-0.84, 0, 0.36),
                (0.86, 0, 0.33),
                (0.01, 0, -0.52),
                (-0.863, 0, -0.445),
                (0.863, 0, -0.445),
        ]
        self.panelText = ('Make a\nToon', 'Make a\nToon')
        self.textColor = VBase4(0.933594, 0.265625, 0.28125, 0.6)
        self.textColorRlvr = VBase4(0.933594, 0.265625, 0.28125, 1.0)
        self.textScale = 0.1
        self.textScaleRlvr = 0.12

    def enter(self):
        if not self.isLoaded:
            self.load()
        base.disableMouse()
        self.bg.show()
        self.quitButton.show()
        self.logoutButton.show()
        if FFTime.isWinter():
            base.setBackgroundColor(Vec4(0.682, 0.847, 0.99, 1))
        elif FFTime.isHalloween():
            base.setBackgroundColor(Vec4(0.118, 0.118, 0.118, 1))
        else:
            base.setBackgroundColor(Vec4(0.145, 0.368, 0.78, 1))

    def exit(self):
        if not self.isLoaded:
            return
        self.unload()
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        soundMgr.stopPAT()

    def load(self):
        self.isLoaded = 1
        if FFTime.isWinter():
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_christmas')
        elif FFTime.isHalloween():
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_halloween')
        else:
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui')

        bgImage = gui.find('**/tt_t_gui_pat_background')
        avBtn1 = gui.find('**/tt_t_gui_pat_squareGreen')
        avBtn2 = gui.find('**/tt_t_gui_pat_squareRed')
        avBtn3 = gui.find('**/tt_t_gui_pat_squarePurple')
        avBtn4 = gui.find('**/tt_t_gui_pat_squarePink')
        avBtn5 = gui.find('**/tt_t_gui_pat_squareBlue')
        avBtn6 = gui.find('**/tt_t_gui_pat_squareYellow')

        quitGui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui')
        quitHover = quitGui.find('**/QuitBtn_RLVR')

        trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui')
        trashClsd = trashcanGui.find('**/TrashCan_CLSD')
        trashOpen = trashcanGui.find('**/TrashCan_OPEN')
        trashRlvr = trashcanGui.find('**/TrashCan_RLVR')

        self.bg = DirectFrame(image=bgImage, relief=None)
        self.bg.hide()
        Mickey = ToontownGlobals.getSignFont()

        topBar = DirectFrame(parent=self.bg, relief=None, text='Pick  A  Toon  To  Play', text_fg=(1, 0.92, 0.2, 1), text_font=Mickey, scale=0.15, pos=(0, 0, 0.82))

        self.b1 = DirectButton(parent=self.bg, image=avBtn1, relief=None, pos=self.posList[0], scale=1.01, text=self.panelText, text_scale=self.textScale, text_font=Mickey, text_fg=self.textColor, text1_scale=self.textScaleRlvr, text1_font=Mickey, text1_fg=self.textColorRlvr, text2_scale=self.textScaleRlvr, text2_font=Mickey, text2_fg=self.textColorRlvr, command=self.startMakeAToon, extraArgs=[1])
        self.b1Delete = DirectButton(parent=self.b1, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[0], scale=0.45, command=self.__handleDelete, extraArgs=[1])
        self.b1Delete.hide()

        self.b2 = DirectButton(parent=self.bg, image=avBtn2, relief=None, pos=self.posList[1], scale=1.01, text=self.panelText, text_scale=self.textScale, text_font=Mickey, text_fg=self.textColor, text1_scale=self.textScaleRlvr, text1_font=Mickey, text1_fg=self.textColorRlvr, text2_scale=self.textScaleRlvr, text2_font=Mickey, text2_fg=self.textColorRlvr, command=self.startMakeAToon, extraArgs=[2])
        self.b2Delete = DirectButton(parent=self.b2, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[1], scale=0.45, command=self.__handleDelete, extraArgs=[2])
        self.b2Delete.hide()

        self.b3 = DirectButton(parent=self.bg, image=avBtn3, relief=None, pos=self.posList[2], scale=1.01, text=self.panelText, text_scale=self.textScale, text_font=Mickey, text_fg=self.textColor, text1_scale=self.textScaleRlvr, text1_font=Mickey, text1_fg=self.textColorRlvr, text2_scale=self.textScaleRlvr, text2_font=Mickey, text2_fg=self.textColorRlvr, command=self.startMakeAToon, extraArgs=[3])
        self.b3Delete = DirectButton(parent=self.b3, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[2], scale=0.45, command=self.__handleDelete, extraArgs=[3])
        self.b3Delete.hide()

        self.b4 = DirectButton(parent=self.bg, image=avBtn4, relief=None, pos=self.posList[3], scale=1.01, text=self.panelText, text_scale=self.textScale, text_font=Mickey, text_fg=self.textColor, text1_scale=self.textScaleRlvr, text1_font=Mickey, text1_fg=self.textColorRlvr, text2_scale=self.textScaleRlvr, text2_font=Mickey, text2_fg=self.textColorRlvr, command=self.startMakeAToon, extraArgs=[4])
        self.b4Delete = DirectButton(parent=self.b4, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[3], scale=0.45, command=self.__handleDelete, extraArgs=[4])
        self.b4Delete.hide()

        self.b5 = DirectButton(parent=self.bg, image=avBtn5, relief=None, pos=self.posList[4], scale=1.01, text=self.panelText, text_scale=self.textScale, text_font=Mickey, text_fg=self.textColor, text1_scale=self.textScaleRlvr, text1_font=Mickey, text1_fg=self.textColorRlvr, text2_scale=self.textScaleRlvr, text2_font=Mickey, text2_fg=self.textColorRlvr, command=self.startMakeAToon, extraArgs=[5])
        self.b5Delete = DirectButton(parent=self.b5, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[4], scale=0.45, command=self.__handleDelete, extraArgs=[5])
        self.b5Delete.hide()

        self.b6 = DirectButton(parent=self.bg, image=avBtn6, relief=None, pos=self.posList[5], scale=1.01, text=self.panelText, text_scale=self.textScale, text_font=Mickey, text_fg=self.textColor, text1_scale=self.textScaleRlvr, text1_font=Mickey, text1_fg=self.textColorRlvr, text2_scale=self.textScaleRlvr, text2_font=Mickey, text2_fg=self.textColorRlvr, command=self.startMakeAToon, extraArgs=[6])
        self.b6Delete = DirectButton(parent=self.b6, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[5], scale=0.45, command=self.__handleDelete, extraArgs=[6])
        self.b6Delete.hide()

        self.quitButton = DirectButton(parent=self.bg, image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserQuit, text_font=ToontownGlobals.getSignFont(), text_fg=(0.977, 0.816, 0.133, 1), text_pos=TTLocalizer.ACquitButtonPos, text_scale=TTLocalizer.ACquitButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(1.08, 0, -0.907), command=sys.exit)
        self.logoutButton = DirectButton(parent=self.bg, relief=None, image=(quitHover, quitHover, quitHover), text=TTLocalizer.OptionsPageLogout, text_font=ToontownGlobals.getSignFont(), text_fg=(0.977, 0.816, 0.133, 1), text_scale=TTLocalizer.AClogoutButton, text_pos=(0, -0.035), pos=(-1.17, 0, -0.914), image_scale=1.15, image1_scale=1.15, image2_scale=1.18, scale=0.5, command=self.__handleLogout)

        self.checkData()
        gui.removeNode()
        quitGui.removeNode()
        trashcanGui.removeNode()
        return

    def unload(self):
        self.isLoaded = 0
        self.bg.destroy()
        del self.bg

    def startMakeAToon(self, index):
        base.transitions.fadeOut()
        Sequence(Wait(1), Func(self.loadMakeAToon, index)).start()

    def loadMakeAToon(self, index):
        self.exit()
        if self.mat:
            del self.mat
        self.mat = MakeAToon('MakeAToon-done', index, 1)
        self.mat.load()
        self.mat.enter()

    def __handleLogout(self):
        base.transitions.fadeOut()
        Sequence(Wait(1), Func(self.exit), Func(base.cr.enterLogin)).start()

    def checkData(self):
        if dataMgr.checkToonFiles(playToken):
            for x in range(1, 7):
                data = dataMgr.loadToonData(x, playToken)
                if data != None:
                    if x == 1:
                        self.displayHead(data, self.b1)
                        self.b1Delete.show()
                    elif x == 2:
                        self.displayHead(data, self.b2)
                        self.b2Delete.show()
                    elif x == 3:
                        self.displayHead(data, self.b3)
                        self.b3Delete.show()
                    elif x == 4:
                        self.displayHead(data, self.b4)
                        self.b4Delete.show()
                    elif x == 5:
                        self.displayHead(data, self.b5)
                        self.b5Delete.show()
                    elif x == 6:
                        self.displayHead(data, self.b6)
                        self.b6Delete.show()

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

        toonText = DirectLabel(parent=button, text=data.setName, relief=None, scale=0.08, pos=NAME_POSITIONS[data.index - 1], hpr=(0, 0, NAME_ROTATIONS[data.index - 1]), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_wordwrap=8, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
        button['text'] = None
        button.name = data.setName
        button.bind(DGG.ENTER, self.__showText, [button])
        button.bind(DGG.EXIT, self.__hideText)
        button.bind(DGG.B1CLICK, self.enterTheTooniverse, [data])

    def enterTheTooniverse(self, data, event):
        base.transitions.fadeOut()
        Sequence(Wait(1), Func(self.__handleDone, data)).start()

    def __showText(self, button, event):
        self.playText = OnscreenText(parent=button, text='Play\nThis Toon', font=ToontownGlobals.getSignFont(), scale=self.textScaleRlvr, fg=(1, 0.92, 0.2, 1))

    def __hideText(self, event):
        self.playText.hide()

    def __handleDelete(self, index):
        if index == 1:
            name = self.b1.name
        elif index == 2:
            name = self.b2.name
        elif index == 3:
            name = self.b3.name
        elif index == 4:
            name = self.b4.name
        elif index == 5:
            name = self.b5.name
        elif index == 6:
            name = self.b6.name
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
            dataMgr.deleteToonData(index, playToken)
            # Hacky way of updating the gui
            self.unload()
            self.load()
            self.enter()

    def __handleDone(self, data):
        loader.beginBulkLoad('main', 'Entering. . .', 1000, TTLocalizer.TIP_GENERAL)
        dataMgr.createLocalAvatar(data)
        self.exit()
        loader.endBulkLoad('main')
        base.cr.enterTheTooniverse(data.setLastHood)
