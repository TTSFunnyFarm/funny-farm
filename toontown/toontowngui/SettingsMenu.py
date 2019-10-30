from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TTDialog
from panda3d.core import *
AUDIO = 0
VIDEO = 1
CONTROLS = 2
EXTRA = 3
class SettingsMenu(DirectFrame):
    def __init__(self, parent = aspect2d, **kw):
        self.settingsGui = loader.loadModel("phase_14/models/gui/settings_gui")
        if base.localAvatar.book.isOpen:
            base.localAvatar.book.close()
        base.transitions.fadeScreen()
        base.localAvatar.disable()
        base.localAvatar.chatMgr.disableKeyboardShortcuts()
        self.background = self.settingsGui.find('**/settingsBackground')
        optiondefs = (('relief', None, None),
         ('image', self.background, None),
         ('image_scale', (1.0, 1.0, 1.0), None),
         ('state', DGG.NORMAL, None))
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, aspect2d, relief=None)
        self.initialiseoptions(SettingsMenu)
        self.categoryNames = ["Audio", "Video", "Controls", "Extras"]
        self.title = DirectLabel(parent=self, relief=None, text_scale=(0.1, 0.1, 1.0), text=self.categoryNames[0], text_font=ToontownGlobals.getMinnieFont(), text_pos=(0, 0.43, 0), text_fg=(0.24, 0.13, 0.008, 1), text_align=TextNode.ACenter)
        buttonIcons = [self.settingsGui.find('**/settingsAudio'), self.settingsGui.find('**/settingsVideo'), self.settingsGui.find('**/settingsControls'), self.settingsGui.find('**/settingsExtra')]
        self.hover = self.settingsGui.find('**/settingsHover')
        self.hover = OnscreenImage(image = self.hover, pos = (0, 0, 0))
        self.hover.setTransparency(True)
        self.buttons = []
        self.categories = {}
        self.currentIndex = 0
        i = -1
        for icon in buttonIcons:
            i += 1
            self.categories[i] = {}
            button = DirectButton(parent=self, relief=None, pos=(i * 0.22 - 0.28, 0, 0.3), image_scale=(1.0, 1.0, 1.0), state=DGG.NORMAL, image=buttonIcons[i], command=self.switchCategory, extraArgs=[i])
            button.bind(DGG.WITHIN, self._onHover, [button])
            button.bind(DGG.WITHOUT, self._onExit, [button])
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.buttons.append(DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.75, 0.75, 1), text="Apply", text_scale=0.06, text_pos=(0, -0.02), pos=(0.60, 0, -0.47), command=self._handleSettingsApply))
        self.dialog = TTDialog.TTDialog(text="Are you sure you want to apply these settings?", text_align=TextNode.ACenter, style=TTDialog.YesNo, command=self.handleSettingsSave)
        category = self.categories[AUDIO]
        category["musicVol"] = DirectSlider(parent=self, scale=(0.4,1.0,0.65), pos=(0.47, 0, 0.07), range=(0,100), value=settings["musicVol"] * 100, pageSize=0, color=(0.33, 0.2, 0.031,255), thumb_relief=None, thumb_image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), thumb_color=(1.0,1.0,1.0,255), command=self._onMusicVolumeUpdate)
        category["musicVolLabel"] = DirectLabel(parent=self, relief=None, text="", text_scale=(0.1, 0.1, 1.0), text_pos=(-0.4, 0.05, 0))
        category["sfxVol"] = DirectSlider(parent=self, scale=(0.4,1.0,0.65), pos=(0.47, 0, -0.10), range=(0,100), value=settings["sfxVol"] * 100, pageSize=0, color=(0.33, 0.2, 0.031,255), thumb_relief=None, thumb_image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), thumb_color=(1.0,1.0,1.0,255), command=self._onSFXVolumeUpdate)
        category["sfxVolLabel"] = DirectLabel(parent=self, relief=None, text="", text_scale=(0.1, 0.1, 1.0), text_pos=(-0.4, -0.13, 0))
        self.oldSettings = settings
        self.setBin('gui-popup', 0)

    def close(self, save=False):
        base.transitions.noFade()
        base.localAvatar.enable()
        base.localAvatar.chatMgr.enableKeyboardShortcuts()
        category = self.categories[AUDIO]
        sfxVol = int(category["sfxVol"]["value"]) / 100
        musicVol = int(category["musicVol"]["value"]) / 100
        if save:
            settings["sfxVol"] = sfxVol
            settings["musicVol"] = musicVol
        else:
            for sfxMgr in base.sfxManagerList:
                sfxMgr.setVolume(self.oldSettings["sfxVol"])
            musicMgr.setVolume(self.oldSettings["musicVol"])
        self.hover.removeNode()
        self.removeNode()

    def _handleSettingsApply(self):
        self.dialog.show()

    def handleSettingsSave(self, arg=-1):
        self.dialog.hide()
        base.transitions.fadeScreen()
        print(arg)
        self.close(arg > 0)

    def _onSFXVolumeUpdate(self):
        if self.currentIndex != AUDIO:
            return # THIS REALLY. REALLY. SHOULD NOT HAPPEN.
        category = self.categories[self.currentIndex]
        vol = int(category["sfxVol"]["value"])
        category["sfxVolLabel"].setText("SFX Volume: " + str(vol) + "%")
        for sfxMgr in base.sfxManagerList:
            sfxMgr.setVolume(vol / 100)

    def _onMusicVolumeUpdate(self):
        if self.currentIndex != AUDIO:
            return #THIS ALSO SHOULD NOT HAPPEN. GOD.
        category = self.categories[self.currentIndex]
        vol = int(category["musicVol"]["value"])
        category["musicVolLabel"].setText("Music Volume: " + str(vol) + "%")
        musicMgr.setVolume(vol / 100)

    def _onHover(self, button, huh):
        self.hover.reparentTo(button)

    def _onExit(self, button, huh):
        self.hover.reparentTo(hidden)

    def _onPress(self, bar, huh):
        bar.setValue()

    def switchCategory(self, cat):
        if self.currentIndex > -1:
            for category in self.categories[self.currentIndex]:
                category.hide()
        for element in self.categories[cat]:
            element.show()
        self.title.setText(self.categoryNames[cat])
        self.currentIndex = cat
