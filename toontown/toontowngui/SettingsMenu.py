from direct.gui.DirectGui import *
from direct.gui.DirectGuiBase import *
from toontown.toonbase import ToontownGlobals, DisplayOptions, TTLocalizer
from toontown.toontowngui import TTDialog
from panda3d.core import *
AUDIO = 0
VIDEO = 1
CONTROLS = 2
EXTRA = 3
class SettingsMenu(DirectFrame):
    def __init__(self, parent = aspect2d, **kw):
        self.settingsGui = loader.loadModel("phase_14/models/gui/settings_gui")
        base.localAvatar.book.hideButton()
        base.localAvatar.disable()
        base.localAvatar.chatMgr.disableKeyboardShortcuts()
        base.localAvatar.setAnimState('neutral')
        self.background = self.settingsGui.find('**/settingsBackground')
        optiondefs = (('relief', None, None),
         ('image', self.background, None),
         ('image_scale', (1.0, 1.0, 1.0), None),
         ('state', DGG.NORMAL, None))
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, aspect2d, relief=None)
        self.initialiseoptions(SettingsMenu)
        self.categoryNames = ["Audio", "Video", "Controls", "Extras"]
        self.frame = DirectScrolledFrame(self, canvasSize = (-0.85,0.85,-3,1.5), frameSize = (-0.9,0.9,-.45,.25), image=None, relief=None)
        text_scale = (0.1, 0.1, 1.0)
        self.title = DirectLabel(parent=self, relief=None, text_scale=text_scale, text="", text_font=ToontownGlobals.getMinnieFont(), text_pos=(0, 0.23, 0), text_fg=(0.24, 0.13, 0.008, 1), text_align=TextNode.ACenter)
        buttonIcons = [self.settingsGui.find('**/settingsAudio'), self.settingsGui.find('**/settingsVideo'), self.settingsGui.find('**/settingsControls'), self.settingsGui.find('**/settingsExtra')]
        self.hover = self.settingsGui.find('**/settingsHover')
        self.hover = OnscreenImage(image = self.hover, pos = (0, 0, 0))
        self.hover.setTransparency(True)
        self.buttons = []
        self.categories = {}
        self.currentIndex = -1
        self.changed = False
        i = -1
        for icon in buttonIcons:
            i += 1
            self.categories[i] = {}
            button = DirectButton(parent=self, relief=None, pos=(i * 0.22 - 0.28, 0, 0.43), image_scale=(1.0, 1.0, 1.0), state=DGG.NORMAL, image=buttonIcons[i], command=self.switchCategory, extraArgs=[i])
            button.bind(DGG.WITHIN, self._onHover, [button])
            button.bind(DGG.WITHOUT, self._onExit, [button])
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.buttons.append(DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.75, 0.75, 1), text="Apply", text_scale=0.06, text_pos=(0, -0.02), pos=(0.60, 0, -0.47), command=self.handleSettingsApply))
        self.finalApply = TTDialog.TTDialog(text="Are you sure you want to apply these settings?", text_align=TextNode.ACenter, style=TTDialog.YesNo, command=self.handleSettingsSave)
        self.finalApply.hide()
        self.resTimeoutSeconds = 15
        self.resDialog = TTDialog.TTDialog(style=TTDialog.TwoChoice, text=TTLocalizer.DisplaySettingsAccept % self.resTimeoutSeconds, text_wordwrap=15, command=self.handleResApply)
        self.resDialog.setBin('gui-popup', 0)
        self.resDialog.hide()
        category = self.categories[AUDIO]
        category["musicVol"] = DirectSlider(parent=self.frame.getCanvas(), scale=(0.35,1.0,0.65), pos=(0.47, 0, -0.165), range=(0,100), value=settings["musicVol"] * 100, pageSize=0, color=(0.33, 0.2, 0.031,255), thumb_relief=None, thumb_image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), thumb_color=(1.0,1.0,1.0,255), command=self._onMusicVolumeUpdate)
        category["musicVolLabel"] = DirectLabel(parent=self.frame.getCanvas(), relief=None, text="", text_fg=(0.24, 0.13, 0.008, 1), text_scale=text_scale, text_pos=(-0.35, -0.195, 0))
        category["sfxVol"] = DirectSlider(parent=self.frame.getCanvas(), scale=(0.35,1.0,0.65), pos=(0.47, 0, -0.32), range=(0,100), value=settings["sfxVol"] * 100, pageSize=0, color=(0.33, 0.2, 0.031,255), thumb_relief=None, thumb_image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), thumb_color=(1.0,1.0,1.0,255), command=self._onSFXVolumeUpdate)
        category["sfxVolLabel"] = DirectLabel(parent=self.frame.getCanvas(), relief=None, text="", text_fg=(0.24, 0.13, 0.008, 1), text_scale=text_scale, text_pos=(-0.35, -0.35, 0))
        category = self.categories[VIDEO]
        if settings["fullscreen"]:
            text = "Fullscreen is on."
            image = self.settingsGui.find('**/settingsTicked')
        else:
            text = "Fullscreen is off."
            image = self.settingsGui.find('**/settingsUnticked')
        category["fullscreenCheck"] = DirectButton(parent=self.frame.getCanvas(), relief=None, scale=1, pos=(0.58, 0, -0.155), image=(self.settingsGui.find('**/settingsUnticked')), command=self._onFullscreenTick)
        category["fullscreenCheck"].key = "fullscreen"
        category["fullscreenCheck"].title = "Fullscreen"
        category["fullscreenCheckLabel"] = DirectLabel(parent=self.frame.getCanvas(), relief=None, text=text, text_fg=(0.24, 0.13, 0.008, 1), text_scale=text_scale, text_pos=(-0.35, -0.195, 0))
        category["vSyncCheck"] = DirectButton(parent=self.frame.getCanvas(), relief=None, scale=1, pos=(0.58, 0, -0.31), image=(self.settingsGui.find('**/settingsUnticked')), command=self._onVSyncTick)
        category["vSyncCheck"].key = "vsync"
        category["vSyncCheck"].title = "V-Sync"
        category["vSyncCheckLabel"] = DirectLabel(parent=self.frame.getCanvas(), relief=None, text=text, text_fg=(0.24, 0.13, 0.008, 1), text_scale=text_scale, text_pos=(-0.35, -0.35, 0))
        for item in list(category):
            key = item
            element = category[item]
            if isinstance(element, DirectGuiWidget):
                element.hide()
            if isinstance(element, DirectButton):
                if hasattr(element, "key") and hasattr(element, "title"):
                    category[key + "Ticked"] = settings[element.key]
                    if settings[element.key]:
                        element["image"] = self.settingsGui.find('**/settingsTicked')
                        category[key + "Label"].setText(element.title + " is on.")
                    else:
                        element["image"] = self.settingsGui.find('**/settingsUnticked')
                        category[key + "Label"].setText(element.title + " is off.")

        self.oldSettings = settings
        self.setBin('gui-popup', 0)
        self.switchCategory(AUDIO)
        base.transitions.fadeScreen()

    def close(self, save=False):
        base.localAvatar.book.showButton()
        base.transitions.noFade()
        base.localAvatar.enable()
        base.localAvatar.chatMgr.enableKeyboardShortcuts()
        category = self.categories[AUDIO]
        sfxVol = int(category["sfxVol"]["value"]) / 100
        musicVol = int(category["musicVol"]["value"]) / 100
        category = self.categories[VIDEO]
        if save:
            settings["sfxVol"] = sfxVol
            settings["sfx"] = sfxVol > 0.0
            settings["musicVol"] = musicVol
            settings["music"] = musicVol > 0.0
            for element in list(category):
                if isinstance(element, DirectButton):
                    if hasattr(element, "key") and hasattr(element, "title"):
                        settings[key] = category[key + "CheckTicked"]
        else:
            for sfxMgr in base.sfxManagerList:
                sfxMgr.setVolume(self.oldSettings["sfxVol"])
            musicMgr.setVolume(self.oldSettings["musicVol"])
            if category["fullscreenCheckTicked"] != self.oldSettings['fullscreen']:
                self._onFullscreenTick()
        self.frame.getCanvas().removeNode()
        self.hover.removeNode()
        self.finalApply.removeNode()
        self.resDialog.removeNode()
        taskMgr.remove('res-countdown')
        self.removeNode()

    def handleSettingsApply(self):
        if self.changed:
            self.finalApply.show()
        else:
            self.close()

    def handleSettingsSave(self, arg=-1):
        self.finalApply.hide()
        base.transitions.fadeScreen()
        self.close(arg > 0)

    def handleResChange(self):
        self.resDialog.show()
        taskMgr.doMethodLater(1, self._resCountdown, 'res-countdown')

    def handleResApply(self, arg=-1):
        taskMgr.remove('res-countdown')
        self.resTimeoutSeconds = 15
        self.resDialog.setText(TTLocalizer.DisplaySettingsAccept % self.resTimeoutSeconds)
        if arg != DGG.DIALOG_OK:
            self._closeResDialog()
        else:
            self.resDialog.hide()
        base.transitions.fadeScreen()

    def _closeResDialog(self):
        category = self.categories[VIDEO]
        self.resDialog.hide()
        if category["fullscreenCheckTicked"] != self.oldSettings['fullscreen']:
            self._onFullscreenTick(handle=False) # We don't want this to be handled or else we go into a bit of a loop.

    def _onSFXVolumeUpdate(self):
        category = self.categories[self.currentIndex]
        if self.currentIndex != AUDIO:
            return # THIS REALLY. REALLY. SHOULD NOT HAPPEN.
        vol = int(category["sfxVol"]["value"])
        category["sfxVolLabel"].setText("SFX Volume: " + str(vol) + "%")
        vol = vol / 100
        if not vol == self.oldSettings["sfxVol"]:
            self.changed = True
        for sfxMgr in base.sfxManagerList:
            sfxMgr.setVolume(vol)

    def _onMusicVolumeUpdate(self):
        category = self.categories[self.currentIndex]
        if self.currentIndex != AUDIO:
            return #THIS ALSO SHOULD NOT HAPPEN. GOD.
        vol = int(category["musicVol"]["value"])
        category["musicVolLabel"].setText("Music Volume: " + str(vol) + "%")
        vol = vol / 100
        if not vol == self.oldSettings["musicVol"]:
            self.changed = True
        musicMgr.setVolume(vol)

    def _onFullscreenTick(self, handle=True):
        category = self.categories[VIDEO]
        fullscreen = not category["fullscreenCheckTicked"]
        category["fullscreenCheckTicked"] = fullscreen
        properties = WindowProperties()
        #width, height = (base.pipe.getDisplayWidth(), base.pipe.getDisplayHeight())
        if fullscreen:
            w, h = (base.pipe.getDisplayWidth(), base.pipe.getDisplayHeight())
        else:
            w, h = (settings['res'][0], settings['res'][1])
        properties.setSize(w, h)
        properties.setFullscreen(fullscreen)
        base.win.requestProperties(properties)
        base.graphicsEngine.renderFrame()
        if fullscreen:
            category["fullscreenCheck"]["image"] = self.settingsGui.find('**/settingsTicked')
            category["fullscreenCheckLabel"]["text"] = "Fullscreen is on."
            # Save their new resolution since we're fullscreened now.
            #settings['res'] = [width, height]
        else:
            category["fullscreenCheck"]["image"] = self.settingsGui.find('**/settingsUnticked')
            category["fullscreenCheckLabel"]["text"] = "Fullscreen is off."
        if handle:
            self.handleResChange()

    def _onVSyncTick(self):
        category = self.categories[VIDEO]
        val = not category["vSyncCheckTicked"]
        category["vSyncCheckTicked"] = val
        if val:
            category["vSyncCheck"]["image"] = self.settingsGui.find('**/settingsTicked')
            category["vSyncCheckLabel"]["text"] = "V-Sync is on.\nRequires restart!"
        else:
            category["vSyncCheck"]["image"] = self.settingsGui.find('**/settingsUnticked')
            category["vSyncCheckLabel"]["text"] = "V-Sync is off.\nRequires restart!"

    def _resCountdown(self, task):
        self.resTimeoutSeconds -= 1
        if self.resTimeoutSeconds > 0:
            self.resDialog.setText(TTLocalizer.DisplaySettingsAccept % self.resTimeoutSeconds)
            taskMgr.doMethodLater(1, self._resCountdown, 'res-countdown')
        else:
            self._closeResDialog()
        return task.done

    def _onHover(self, button, val):
        if self.hover:
            self.hover.reparentTo(button)

    def _onExit(self, button, val):
        if self.hover:
            self.hover.reparentTo(hidden)

    def _onPress(self, bar, val):
        bar.setValue()

    def switchCategory(self, cat):
        if self.currentIndex > -1:
            for key, element in self.categories [self.currentIndex].items():
                if isinstance(element, DirectGuiWidget):
                    element.hide()
        diff = 0.02
        height = 0
        for key, element in self.categories[cat].items():
            if isinstance(element, DirectGuiWidget):
                if isinstance(element, DirectLabel):
                    if element["text_pos"][1] < height:
                        height = element["text_pos"][1]
                element.show()
            else:
                continue
        self.frame["canvasSize"] = (-0.85,0.85,height - 0.03,0)
        self.title.setText(self.categoryNames[cat])
        self.currentIndex = cat
