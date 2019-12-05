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
        self.videoTimeoutSeconds = 15
        self.videoDialog = TTDialog.TTDialog(style=TTDialog.TwoChoice, text=TTLocalizer.DisplaySettingsAccept % self.videoTimeoutSeconds, text_wordwrap=15, command=self.handleVideoApply)
        self.videoDialog.setBin('gui-popup', 0)
        self.videoDialog.hide()
        category = self.categories[AUDIO]
        category["musicVol"] = DirectSlider(parent=self.frame.getCanvas(), scale=(0.35,1.0,0.65), pos=(0.47, 0, -0.165), range=(0,100), value=settings["musicVol"] * 100, pageSize=0, color=(0.33, 0.2, 0.031,255), thumb_relief=None, thumb_image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), thumb_color=(1.0,1.0,1.0,255), command=self._onMusicVolumeUpdate)
        category["musicVolLabel"] = DirectLabel(parent=self.frame.getCanvas(), relief=None, text="", text_fg=(0.24, 0.13, 0.008, 1), text_scale=text_scale, text_pos=(-0.35, -0.195, 0))
        category["sfxVol"] = DirectSlider(parent=self.frame.getCanvas(), scale=(0.35,1.0,0.65), pos=(0.47, 0, -0.32), range=(0,100), value=settings["sfxVol"] * 100, pageSize=0, color=(0.33, 0.2, 0.031,255), thumb_relief=None, thumb_image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), thumb_color=(1.0,1.0,1.0,255), command=self._onSFXVolumeUpdate)
        category["sfxVolLabel"] = DirectLabel(parent=self.frame.getCanvas(), relief=None, text="", text_fg=(0.24, 0.13, 0.008, 1), text_scale=text_scale, text_pos=(-0.35, -0.35, 0))
        category = self.categories[VIDEO]
        category["isFullscreenTicked"] = settings["fullscreen"]
        category["fullscreenCheck"] = DirectButton(parent=self.frame.getCanvas(), relief=None, scale=1, pos=(0.58, 0, -0.155), geom=(self.settingsGui.find('**/settingsUnticked')), command=self._onFullscreenTick)
        if settings["fullscreen"]:
            text = "Fullscreen is on."
        else:
            text = "Fullscreen is off."
        category["fullscreenCheckLabel"] = DirectLabel(parent=self.frame.getCanvas(), relief=None, text=text, text_fg=(0.24, 0.13, 0.008, 1), text_scale=text_scale, text_pos=(-0.25, -0.195, 0))
        for element in category:
            element = category[element]
            if isinstance(element, DirectGuiWidget):
                element.hide()
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
            settings["fullscreen"] = category["isFullscreenTicked"]
        else:
            for sfxMgr in base.sfxManagerList:
                sfxMgr.setVolume(self.oldSettings["sfxVol"])
            musicMgr.setVolume(self.oldSettings["musicVol"])
            if category["isFullscreenTicked"] != self.oldSettings['fullscreen']:
                self._onFullscreenTick()
        self.frame.getCanvas().removeNode()
        self.hover.removeNode()
        self.finalApply.removeNode()
        self.videoDialog.removeNode()
        taskMgr.remove('video-countdown')
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

    def handleVideoChange(self):
        self.videoTimeoutSeconds = 15
        self.videoDialog.show()
        taskMgr.doMethodLater(1, self._videoCountdown, 'video-countdown')

    def handleVideoApply(self, arg=-1):
        if arg != DGG.DIALOG_OK:
            self._closeVideoDialog()
        else:
            self.videoDialog.hide()

    def _closeVideoDialog(self):
        category = self.categories[VIDEO]
        self.videoDialog.hide()
        if category["isFullscreenTicked"] != self.oldSettings['fullscreen']:
            self._onFullscreenTick()

    def _onSFXVolumeUpdate(self):
        if self.currentIndex != AUDIO:
            return # THIS REALLY. REALLY. SHOULD NOT HAPPEN.
        category = self.categories[self.currentIndex]
        vol = int(category["sfxVol"]["value"])
        category["sfxVolLabel"].setText("SFX Volume: " + str(vol) + "%")
        if not vol / 100 == self.oldSettings["sfxVol"]:
            self.changed = True
        for sfxMgr in base.sfxManagerList:
            sfxMgr.setVolume(vol / 100)

    def _onMusicVolumeUpdate(self):
        if self.currentIndex != AUDIO:
            return #THIS ALSO SHOULD NOT HAPPEN. GOD.
        category = self.categories[self.currentIndex]
        vol = int(category["musicVol"]["value"])
        category["musicVolLabel"].setText("Music Volume: " + str(vol) + "%")
        if not vol / 100 == self.oldSettings["musicVol"]:
            self.changed = True
        musicMgr.setVolume(vol / 100)

    def _onFullscreenTick(self):
        category = self.categories[VIDEO]
        fullscreen = not category["isFullscreenTicked"]
        category["isFullscreenTicked"] = fullscreen
        properties = WindowProperties()
        #width, height = (base.pipe.getDisplayWidth(), base.pipe.getDisplayHeight())
        properties.setSize(settings['res'][0], settings['res'][1])
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
        self.handleVideoChange()
        # Hackfix: In order to avoid resolution issues when the user has their window fullscreened
        # (which most people do), we're gonna first set their resolution to an acceptable size,
        # and THEN correct the resolution with their actual display size.

    def _videoCountdown(self, task):
        self.videoTimeoutSeconds -= 1
        self.videoDialog.setText(TTLocalizer.DisplaySettingsAccept % self.videoTimeoutSeconds)
        if self.videoTimeoutSeconds > 0:
            taskMgr.doMethodLater(1, self._videoCountdown, 'video-countdown')
        else:
            self._closeVideoDialog()
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
            if isinstance(element, DirectLabel):
                if element["text_pos"][1] < height:
                    height = element["text_pos"][1]
                element.show()
            elif isinstance(element, DirectGuiWidget):
                element.show()
            else:
                continue
        self.frame["canvasSize"] = (-0.85,0.85,height - 0.03,0)
        self.title.setText(self.categoryNames[cat])
        self.currentIndex = cat
