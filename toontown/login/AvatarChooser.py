from panda3d.core import *
from direct.gui.DirectGui import *
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownGlobals, FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
from toontown.toon import ToonHead
from toontown.toon import ToonDNA
import sys, re

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

class AvatarChooser(DirectObject):

    def __init__(self):
        self.isLoaded = 0

    def enter(self):
        if not self.isLoaded:
            self.load()
        self.bg.show()
        self.quitButton.show()
        base.transitions.fadeIn(1.0)

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
            base.setBackgroundColor(Vec4(0.682, 0.847, 0.99, 1))
        elif base.air.holidayMgr.isHalloween():
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_halloween')
            base.setBackgroundColor(Vec4(0.118, 0.118, 0.118, 1))
        else:
            gui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui')
            base.setBackgroundColor(Vec4(0.145, 0.368, 0.78, 1))
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
        self.bg.setBin('background', 1)
        self.bg.hide()
        self.title = OnscreenText(TTLocalizer.AvatarChooserPickAToon, scale=TTLocalizer.ACtitle, parent=self.bg, font=ToontownGlobals.getSignFont(), fg=(1, 0.9, 0.1, 1), pos=(0.0, 0.82))

        for i in range(0, FunnyFarmGlobals.MaxAvatars):
            button = DirectButton(parent=self.bg, image=btnImages[i], relief=None, pos=POSITIONS[i], scale=1.01, text=(TTLocalizer.AvatarChoiceMakeAToon,), text_scale=0.1, text_font=ToontownGlobals.getSignFont(), text_fg=(0, 1, 0.8, 0.5), text1_scale=TTLocalizer.ACmakeAToon, text1_font=ToontownGlobals.getSignFont(), text1_fg=(0, 1, 0.8, 1), text2_scale=TTLocalizer.ACmakeAToon, text2_font=ToontownGlobals.getSignFont(), text2_fg=(0.3, 1, 0.9, 1), command=self.__handleCreate, extraArgs=[i + 1])
            button.delete = DirectButton(parent=button, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[i], scale=0.45, command=self.__handleDelete, extraArgs=[i + 1])
            button.delete.hide()
            button.rename = DirectButton(parent=button, relief=None, image=(quitGui.find('**/QuitBtn_UP'), quitGui.find('**/QuitBtn_DN'), quitGui.find('**/QuitBtn_RLVR')), text=(TTLocalizer.AvatarChoiceNameYourToon, TTLocalizer.AvatarChoiceNameYourToon, TTLocalizer.AvatarChoiceNameYourToon), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_scale=0.15, text_pos=(0, 0.03), text_font=ToontownGlobals.getInterfaceFont(), pos=(-0.2, 0, -0.3), scale=0.45, image_scale=(2, 1, 3), command=self.__handleRename, extraArgs=[i + 1])
            button.rename.hide()
            self.buttons.append(button)

        self.quitButton = DirectButton(parent=base.a2dBottomRight, image=(quitHover, quitHover, quitHover), relief=None, text=TTLocalizer.AvatarChooserQuit, text_font=ToontownGlobals.getSignFont(), text_fg=(0.977, 0.816, 0.133, 1), text_pos=TTLocalizer.ACquitButtonPos, text_scale=TTLocalizer.ACquitButton, image_scale=1, image1_scale=1.05, image2_scale=1.05, scale=1.05, pos=(-0.253333, 0, 0.093), command=base.userExit)
        self.loadAvatars()
        gui.removeNode()
        quitGui.removeNode()
        trashcanGui.removeNode()
        self.renameFrame = None
        self.renameEntry = None
        self.avatarIndex = -1
        if base.gamepad:
            self.avatarIndex = 1
            self.handleDeviceEnabled(base.gamepad)
        self.accept('device-enable', self.handleDeviceEnabled)
        self.isLoaded = 1

    def unload(self):
        if not self.isLoaded:
            return
        for button in self.buttons:
            self.buttons.remove(button)
            button.destroy()
            button.delete.destroy()
            button.rename.destroy()
        del self.buttons
        self.quitButton.destroy()
        del self.quitButton
        self.title.removeNode()
        del self.title
        self.bg.destroy()
        del self.bg
        self.isLoaded = 0

    def cycleAvatar(self, input):
        keybinds = settings['keybinds'][base.getCurrentDevice()]
        delta = 0
        x = False
        if input in ['dpad_right', keybinds['turn_right']]:
            delta = 1
            x = True
        elif input in ['dpad_down', keybinds['reverse']]:
            delta = 3
        elif input in ['dpad_up', keybinds['forward']]:
            delta = -3
        else:
            delta = -1
            x = True
        messenger.send(PGButton.getExitPrefix() + self.buttons[self.avatarIndex].guiId)
        index = self.avatarIndex + delta
        if index < 0:
            if x:
                self.avatarIndex = 0
            else:
                self.avatarIndex = abs(index)
        elif x:
            if self.avatarIndex < index and (index == 3 or index == 6):
                self.avatarIndex = index - 3
            elif self.avatarIndex > index and (index == 2 or index == -1):
                self.avatarIndex = index + 3
        messenger.send(PGButton.getEnterPrefix() + self.buttons[self.avatarIndex].guiId)

    def loadAvatars(self):
        if dataMgr.checkToonFiles():
            for i in range(0, FunnyFarmGlobals.MaxAvatars):
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

        colorstring = TTLocalizer.NumToColor[dna.headColor]
        animaltype = TTLocalizer.AnimalToSpecies[dna.getAnimal()]
        tempname = colorstring + ' ' + animaltype
        reviewedName = self.reviewName(data.setName, data.index)
        if reviewedName == tempname:
            # oh no! this toon has a rejected name probably
            if data.setName != reviewedName:
                data.setName = reviewedName
                dataMgr.saveToonData(data)

            button.rename.show()

        nameText = DirectLabel(parent=button, text=data.setName, relief=None, scale=0.08, pos=NAME_POSITIONS[data.index - 1], hpr=(0, 0, NAME_ROTATIONS[data.index - 1]), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), text_wordwrap=8, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
        button.name = data.setName
        button['command'] = self.__handleChoice
        button['extraArgs'] = [data]
        button['text'] = ('', TTLocalizer.AvatarChoicePlayThisToon, TTLocalizer.AvatarChoicePlayThisToon)
        button['text_scale'] = TTLocalizer.ACplayThisToon
        button['text_fg'] = (1, 0.9, 0.1, 1)
        button.delete.show()

    def reviewName(self, name, index):
        vfs = VirtualFileSystem.getGlobalPtr()
        filename = Filename('tblacklist.dat')
        searchPath = DSearchPath()
        searchPath.appendDirectory(Filename('resources/phase_4/etc'))
        found = vfs.resolveFilename(filename, searchPath)
        if not found:
            self.notify.info("Couldn't find blacklist data file!")
        data = vfs.readFile(filename, 1)

        # We need two lists: one uppercase and one lowercase.
        badWords = data.split()
        badWordsTitled = data.title().split()
        nameWords = re.sub('[^\w]', ' ',  name).split()
        for word in nameWords:
            if word.encode() in badWords or word.encode() in badWordsTitled:
                name = self.findTempName(name, index)
                break
        if len(name) < 3 or len(nameWords) > 4:
            name = self.findTempName(name, index)
        if name.replace(' ', '').strip() == '':
            name = self.findTempName(name, index)
        return name

    def findTempName(self, name, index):
        data = dataMgr.loadToonData(index)
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(*data.setDNA)
        colorstring = TTLocalizer.NumToColor[dna.headColor]
        animaltype = TTLocalizer.AnimalToSpecies[dna.getAnimal()]
        tempname = colorstring + ' ' + animaltype
        return tempname

    def __handleCreate(self, index):
        base.transitions.fadeOut()
        Sequence(Wait(1), Func(base.cr.enterCreateAvatar, index)).start()

    def __handleChoice(self, data):
        base.transitions.fadeOut()
        Sequence(Wait(1), Func(self.__handleDone, data)).start()

    def __handleRename(self, index):
        deleteText = TTLocalizer.AvatarChoiceRename
        if self.renameFrame == None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            nameBalloon = loader.loadModel('phase_3/models/props/chatbox_input')
            okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            cancelButtonImage = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))
            self.renameFrame = DirectFrame(pos=(0, 0, 0), parent=aspect2dp, relief=None, image=DGG.getDefaultDialogGeom(), image_color=ToontownGlobals.GlobalDialogColor, image_scale=(1.4, 1.0, 1.0), text=deleteText, text_wordwrap=19, text_scale=TTLocalizer.ACdeleteWithPasswordFrame, text_pos=(0, 0.25), textMayChange=1, sortOrder=DGG.NO_FADE_SORT_INDEX)
            self.renameFrame.hide()
            self.renameEntry = DirectEntry(parent=self.renameFrame, relief=None, image=nameBalloon, image1_color=(0.8, 0.8, 0.8, 1.0), scale=0.064, pos=(-0.3, 0.0, -0.2), width=10, numLines=1, focus=1, cursorKeys=1, autoCapitalize=1, command=self.__handleRenameOK, extraArgs = [index])
            DirectLabel(parent=self.renameFrame, relief=None, pos=(0, 0, 0.35), text=TTLocalizer.AvatarChoiceRenameTitle, textMayChange=0, text_scale=0.08)
            DirectButton(parent=self.renameFrame, image=okButtonImage, relief=None, text=TTLocalizer.AvatarChoiceDeletePasswordOK, text_scale=0.06, text_pos=(0.0, -0.1), textMayChange=0, pos=(-0.22, 0.0, -0.35), command=self.__handleRenameOK, extraArgs = [None, index])
            DirectButton(parent=self.renameFrame, image=cancelButtonImage, relief=None, text=TTLocalizer.AvatarChoiceDeletePasswordCancel, text_scale=0.06, text_pos=(0.0, -0.1), textMayChange=1, pos=(0.2, 0.0, -0.35), command=self.__handleRenameCancel)
            buttons.removeNode()
            nameBalloon.removeNode()
        else:
            self.renameFrame['text'] = deleteText
            self.renameEntry['focus'] = 1
            self.renameEntry.enterText('')
        base.transitions.fadeScreen(0.5)
        self.renameFrame.show()
        return

    def __handleRenameOK(self, _, index):
        name = self.renameEntry.get()
        data = dataMgr.loadToonData(index)
        reviewedName = self.reviewName(name, index)
        if name == reviewedName:
            self.renameFrame.hide()
            base.transitions.noTransitions()
            if data.setName != name:
                data.setName = name
                dataMgr.saveToonData(data)

            # Hacky way of updating the gui
            self.unload()
            self.load()
            self.enter()
        else:
            self.renameFrame['text'] = TTLocalizer.AvatarChoiceRenameRejected
            self.renameEntry['focus'] = 1
            self.renameEntry.enterText('')

    def __handleRenameCancel(self):
        self.renameFrame.hide()
        base.transitions.noTransitions()

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
        if not base.localAvatar.tutorialAck:
            base.cr.exitCreateAvatar(tutorialFlag=1)
            # If they crashed/exited in the tutorial, there's a chance they lost some laff points
            base.localAvatar.setHealth(20, 20)
        else:
            base.cr.enterTheTooniverse(data.setLastHood)

    def handleDeviceEnabled(self, device):
        messenger.send(PGButton.getEnterPrefix() + self.buttons[self.avatarIndex].guiId)
        keybinds = settings['keybinds'][base.getCurrentDevice()]
        self.accept('dpad_left', self.cycleAvatar, ['dpad_left'])
        self.accept(keybinds['turn_left'], self.cycleAvatar, [keybinds['turn_left']])
        self.accept('dpad_right', self.cycleAvatar, ['dpad_right'])
        self.accept(keybinds['turn_right'], self.cycleAvatar, [keybinds['turn_right']])
        self.accept('dpad_down', self.cycleAvatar, ['dpad_down'])
        self.accept(keybinds['reverse'], self.cycleAvatar, [keybinds['reverse']])
        self.accept('dpad_up', self.cycleAvatar, ['dpad_up'])
        self.accept(keybinds['forward'], self.cycleAvatar, [keybinds['forward']])
