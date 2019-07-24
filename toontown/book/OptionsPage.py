from panda3d.core import *
from direct.gui.DirectGui import *
from direct.task import Task
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals, FunnyFarmGlobals
from toontown.toontowngui import TTDialog
from toontown.book.DisplaySettingsDialog import DisplaySettingsDialog
from toontown.book import ShtikerPage

class OptionsPage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('OptionsPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

        self.optionsTabPage = None
        self.codesTabPage = None
        self.title = None
        self.optionsTab = None
        self.codesTab = None

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.optionsTabPage = OptionsTabPage(self)
        self.optionsTabPage.hide()
        self.title = DirectLabel(
                parent=self, relief=None, text=TTLocalizer.OptionsPageTitle,
                text_scale=0.12, pos=(0, 0, 0.61))

    def enter(self):
        self.optionsTabPage.enter()
        ShtikerPage.ShtikerPage.enter(self)
        self.accept('exitFunnyFarm', self.book.exitFunnyFarm)

    def exit(self):
        self.optionsTabPage.exit()
        ShtikerPage.ShtikerPage.exit(self)

    def unload(self):
        if self.optionsTabPage is not None:
            self.optionsTabPage.unload()
            self.optionsTabPage = None

        if self.codesTabPage is not None:
            self.codesTabPage.unload()
            self.codesTabPage = None

        if self.title is not None:
            self.title.destroy()
            self.title = None

        if self.optionsTab is not None:
            self.optionsTab.destroy()
            self.optionsTab = None

        if self.codesTab is not None:
            self.codesTab.destroy()
            self.codesTab = None

        ShtikerPage.ShtikerPage.unload(self)

class OptionsTabPage(DirectFrame):
    notify = directNotify.newCategory('OptionsTabPage')
    ChangeDisplaySettings = config.GetBool('change-display-settings', 1)
    ChangeDisplayAPI = config.GetBool('change-display-api', 0)

    def __init__(self, parent = aspect2d):
        self._parent = parent
        self.currentSizeIndex = None

        DirectFrame.__init__(self, parent=self._parent, relief=None, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

        self.load()

    def destroy(self):
        self._parent = None

        DirectFrame.destroy(self)

    def load(self):
        self.displaySettings = None
        self.displaySettingsChanged = 0
        self.displaySettingsSize = (None, None)
        self.displaySettingsApi = None
        self.displaySettingsApiChanged = 0
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        matGui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        helpGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_brd_help.bam')
        titleHeight = 0.61
        textStartHeight = 0.45
        textRowHeight = 0.11
        leftMargin = -0.72
        buttonbase_xcoord = 0.36
        buttonbase_ycoord = 0.45
        button_image_scale = (0.7, 1, 1)
        button_textpos = (0, -0.02)
        options_text_scale = 0.052
        disabled_arrow_color = Vec4(0.6, 0.6, 0.6, 1.0)
        self.speed_chat_scale = 0.055

        self.audioLabel = DirectLabel(parent=self, relief=None, text=TTLocalizer.OptionsPageAudioLabel, text_font=ToontownGlobals.getSignFont(), text_fg=(0.3, 0.3, 0.3, 1), text_align=TextNode.ALeft, text_scale=0.07, pos=(-0.8, 0, textStartHeight - 0.03))
        self.videoLabel = DirectLabel(parent=self, relief=None, text=TTLocalizer.OptionsPageVideoLabel, text_font=ToontownGlobals.getSignFont(), text_fg=(0.3, 0.3, 0.3, 1), text_align=TextNode.ALeft, text_scale=0.07, pos=(-0.8, 0, (textStartHeight - textRowHeight * 3) - 0.03))

        self.Music_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, pos=(leftMargin, 0, textStartHeight - textRowHeight))
        self.SoundFX_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 2))
        self.Fullscreen_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 4))
        self.Resolution_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 5))
        self.Vsync_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 6))
        self.Antialias_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 7))
        self.Fps_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 8))
        self.Smooth_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 5))
        self.Blend_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 6))
        self.LOD_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 7))
        self.WaterShader_Label = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, text_scale=options_text_scale, text_wordwrap=16, pos=(leftMargin, 0, textStartHeight - textRowHeight * 8))

        self.Music_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight), command=self.__doToggleMusic)
        self.SoundFX_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 2), command=self.__doToggleSfx)
        self.Fullscreen_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=button_image_scale, text=TTLocalizer.OptionsPageChange, text3_fg=(0.5, 0.5, 0.5, 0.75), text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 4), command=self.__doToggleFullscreen)
        self.Resolution_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 5), command=self.__doChangeResolution)
        self.Vsync_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 6), command=self.__doToggleVsync)
        self.Antialias_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 7), command=self.__doToggleAntialias)
        self.Fps_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 8), command=self.__doToggleFps)
        self.Smooth_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 5), command=self.__doToggleSmooth)
        self.Blend_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 6), command=self.__doToggleBlend)
        self.Blend_tempText = DirectLabel(parent=self, relief=None, text='Coming soon', text_scale=options_text_scale, text_wordwrap=16, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 6))
        self.Blend_tempText.hide()
        self.LOD_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 7), command=self.__doToggleLOD)
        self.WaterShader_toggleButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=button_image_scale, text='', text_scale=options_text_scale, text_pos=button_textpos, pos=(buttonbase_xcoord, 0.0, buttonbase_ycoord - textRowHeight * 8), command=self.__doChangeWaterShader)

        self.rightArrow = DirectButton(parent=self, relief=None, image=(matGui.find('**/tt_t_gui_mat_nextUp'), matGui.find('**/tt_t_gui_mat_nextDown'), matGui.find('**/tt_t_gui_mat_nextUp'), matGui.find('**/tt_t_gui_mat_nextDisabled')), pos=(-0.05, 0, 0.11), image_scale=(0.18, 0.18, 0.18), image1_scale=(0.21, 0.21, 0.21), image2_scale=(0.21, 0.21, 0.21), image3_scale=(0.18, 0.18, 0.18), command=self.enterAdvancedVideoOptions)
        self.leftArrow = DirectButton(parent=self, relief=None, image=(matGui.find('**/tt_t_gui_mat_nextUp'), matGui.find('**/tt_t_gui_mat_nextDown'), matGui.find('**/tt_t_gui_mat_nextUp'), matGui.find('**/tt_t_gui_mat_nextDisabled')), pos=(-0.15, 0, 0.11), image_scale=(-0.18, 0.18, 0.18), image1_scale=(-0.21, 0.21, 0.21), image2_scale=(-0.21, 0.21, 0.21), image3_scale=(-0.18, 0.18, 0.18), command=self.enterVideoOptions)

        self.exitButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=1.15, text=TTLocalizer.OptionsPageExitToontown, text_scale=options_text_scale, text_pos=button_textpos, textMayChange=0, pos=(0.45, 0, -0.6), command=self.__handleExitShowWithConfirm)

        self.Vsync_Help = DirectButton(parent=self, relief=None, image=(helpGui.find('**/tt_t_gui_brd_helpUp'), helpGui.find('**/tt_t_gui_brd_helpDown'), helpGui.find('**/tt_t_gui_brd_helpHover')), pos=(leftMargin + 0.345, 0, (textStartHeight - textRowHeight * 6) + 0.01), scale=0.45, command=self.enterVsyncHelp)
        self.Antialias_Help = DirectButton(parent=self, relief=None, image=(helpGui.find('**/tt_t_gui_brd_helpUp'), helpGui.find('**/tt_t_gui_brd_helpDown'), helpGui.find('**/tt_t_gui_brd_helpHover')), pos=(leftMargin + 0.45, 0, (textStartHeight - textRowHeight * 7) + 0.01), scale=0.45, command=self.enterAntialiasHelp)
        self.Fps_Help = DirectButton(parent=self, relief=None, image=(helpGui.find('**/tt_t_gui_brd_helpUp'), helpGui.find('**/tt_t_gui_brd_helpDown'), helpGui.find('**/tt_t_gui_brd_helpHover')), pos=(leftMargin + 0.42, 0, (textStartHeight - textRowHeight * 8) + 0.01), scale=0.45, command=self.enterFpsHelp)
        self.LOD_Help = DirectButton(parent=self, relief=None, image=(helpGui.find('**/tt_t_gui_brd_helpUp'), helpGui.find('**/tt_t_gui_brd_helpDown'), helpGui.find('**/tt_t_gui_brd_helpHover')), pos=(leftMargin + 0.47, 0, (textStartHeight - textRowHeight * 7) + 0.01), scale=0.45, command=self.enterLODHelp)
        self.WaterShader_Help = DirectButton(parent=self, relief=None, image=(helpGui.find('**/tt_t_gui_brd_helpUp'), helpGui.find('**/tt_t_gui_brd_helpDown'), helpGui.find('**/tt_t_gui_brd_helpHover')), pos=(leftMargin + 0.47, 0, (textStartHeight - textRowHeight * 8) + 0.01), scale=0.45, command=self.enterShaderLevelHelp)

        guiButton.removeNode()
        gui.removeNode()
        helpGui.removeNode()

    def enter(self):
        self.show()
        self.settingsChanged = 0
        self.__setMusicButton()
        self.__setSoundFXButton()
        self.exitButton.show()
        self.enterVideoOptions()
        self.accept(base.win.getWindowEvent(), self.__handleWindowEvent)

    def exit(self):
        self.ignoreAll()
        self.hide()

    def unload(self):
        self.writeDisplaySettings()
        if self.displaySettings != None:
            self.ignore(self.displaySettings.doneEvent)
            self.displaySettings.unload()
        self.displaySettings = None
        self.Music_toggleButton.destroy()
        self.SoundFX_toggleButton.destroy()
        self.Fullscreen_toggleButton.destroy()
        self.Resolution_toggleButton.destroy()
        self.Vsync_toggleButton.destroy()
        self.Antialias_toggleButton.destroy()
        self.Fps_toggleButton.destroy()
        self.Smooth_toggleButton.destroy()
        self.Blend_toggleButton.destroy()
        self.LOD_toggleButton.destroy()
        self.WaterShader_toggleButton.destroy()
        self.exitButton.destroy()
        self.Vsync_Help.destroy()
        self.Antialias_Help.destroy()
        self.LOD_Help.destroy()
        self.Fps_Help.destroy()
        self.WaterShader_Help.destroy()
        del self.audioLabel
        del self.videoLabel
        del self.Music_Label
        del self.SoundFX_Label
        del self.Fullscreen_Label
        del self.Resolution_Label
        del self.Vsync_Label
        del self.Antialias_Label
        del self.Fps_Label
        del self.Smooth_Label
        del self.Blend_Label
        del self.Blend_tempText
        del self.LOD_Label
        del self.WaterShader_Label
        del self.Music_toggleButton
        del self.SoundFX_toggleButton
        del self.Fullscreen_toggleButton
        del self.Resolution_toggleButton
        del self.Vsync_toggleButton
        del self.Antialias_toggleButton
        del self.Fps_toggleButton
        del self.Smooth_toggleButton
        del self.Blend_toggleButton
        del self.LOD_toggleButton
        del self.WaterShader_toggleButton
        del self.exitButton
        del self.Vsync_Help
        del self.Antialias_Help
        del self.Fps_Help
        del self.LOD_Help
        del self.WaterShader_Help
        self.currentSizeIndex = None

    def enterVideoOptions(self):
        self.Smooth_Label.hide()
        self.Smooth_toggleButton.hide()
        self.Blend_Label.hide()
        self.Blend_toggleButton.hide()
        self.Blend_tempText.hide()
        self.LOD_Label.hide()
        self.LOD_toggleButton.hide()
        self.LOD_Help.hide()
        self.WaterShader_Label.hide()
        self.WaterShader_toggleButton.hide()
        self.WaterShader_Help.hide()
        self.Fullscreen_Label.show()
        self.Fullscreen_toggleButton.show()
        self.Resolution_Label.show()
        self.Resolution_toggleButton.show()
        self.Vsync_Label.show()
        self.Vsync_toggleButton.show()
        self.Vsync_Help.show()
        self.Antialias_Label.show()
        self.Antialias_toggleButton.show()
        self.Antialias_Help.show()
        self.Fps_Label.show()
        self.Fps_toggleButton.show()
        self.Fps_Help.show()
        self.__setFullscreenButton()
        self.__setResolutionButton()
        self.__setVsyncButton()
        self.__setAntialiasingButton()
        self.__setFpsButton()
        self.videoLabel['text'] = TTLocalizer.OptionsPageVideoLabel
        self.leftArrow['state'] = DGG.DISABLED
        self.rightArrow['state'] = DGG.NORMAL
        self.currVideoPage = 1

    def enterAdvancedVideoOptions(self):
        self.Fullscreen_Label.hide()
        self.Fullscreen_toggleButton.hide()
        self.Resolution_Label.hide()
        self.Resolution_toggleButton.hide()
        self.Vsync_Label.hide()
        self.Vsync_toggleButton.hide()
        self.Vsync_Help.hide()
        self.Antialias_Label.hide()
        self.Antialias_toggleButton.hide()
        self.Antialias_Help.hide()
        self.Fps_Label.hide()
        self.Fps_toggleButton.hide()
        self.Fps_Help.hide()
        self.Smooth_Label.show()
        self.Smooth_toggleButton.show()
        self.Blend_Label.show()
        self.Blend_toggleButton.show()
        self.LOD_Label.show()
        self.LOD_toggleButton.show()
        self.LOD_Help.show()
        self.WaterShader_Label.show()
        self.WaterShader_toggleButton.show()
        self.WaterShader_Help.show()
        self.__setSmoothingButton()
        self.__setBlendingButton()
        self.__setLODButton()
        self.__setWaterShaderButton()
        self.videoLabel['text'] = TTLocalizer.OptionsPageAdvancedLabel
        self.leftArrow['state'] = DGG.NORMAL
        self.rightArrow['state'] = DGG.DISABLED
        self.currVideoPage = 2

    def __handleWindowEvent(self, win):
        if win == base.win:
            self.__setResolutionButton()

    def __doToggleMusic(self):
        if base.musicActive:
            musicMgr.stopMusic()
            base.enableMusic(0)
            settings['music'] = False
        else:
            base.enableMusic(1)
            settings['music'] = True
            musicMgr.playCurrentZoneMusic()
        self.settingsChanged = 1
        self.__setMusicButton()

    def __doToggleSfx(self):
        if base.sfxActive:
            base.enableSoundEffects(0)
            settings['sfx'] = False
        else:
            base.enableSoundEffects(1)
            settings['sfx'] = True
            base.localAvatar.stopSound()
        self.settingsChanged = 1
        self.__setSoundFXButton()

    def __doToggleToonChatSounds(self):
        if base.toonChatSounds:
            base.toonChatSounds = 0
            settings['toonChatSounds'] = False
        else:
            base.toonChatSounds = 1
            settings['toonChatSounds'] = True
        self.settingsChanged = 1
        self.__setToonChatSoundsButton()

    def __doToggleFullscreen(self):
        settings['fullscreen'] = not settings['fullscreen']
        # Hackfix: In order to avoid resolution issues when the user has their window fullscreened
        # (which most people do), we're gonna first set their resolution to an acceptable size,
        # and THEN correct the resolution with their actual display size.
        if settings['fullscreen']:
            tempProperties = WindowProperties()
            tempProperties.setSize(1024, 768)
            tempProperties.setFullscreen(settings['fullscreen'])
            base.win.requestProperties(tempProperties)
            base.graphicsEngine.renderFrame()

        properties = WindowProperties()
        if settings['fullscreen']:
            width, height = (base.pipe.getDisplayWidth(), base.pipe.getDisplayHeight())
            # Save their new resolution since we're fullscreened now.
            settings['res'] = [width, height]
        else:
            # Set the default res back to 1280x720.
            settings['res'] = [1280, 720]
            width, height = tuple(settings['res'])

        properties.setSize(width, height)
        properties.setFullscreen(settings['fullscreen'])
        base.win.requestProperties(properties)
        base.graphicsEngine.renderFrame()

        newProperties = base.win.getProperties()
        if properties.getFullscreen() and not newProperties.getFullscreen():
            # Either their video card can't display 1024x768 or some other weird problem occurred.
            self.__revertBack()
            return
        self.__setFullscreenButton()

    def __revertBack(self):
        settings['fullscreen'] = False
        self.revertDialog = TTDialog.TTDialog(text=TTLocalizer.OptionsPageFullscreenFailed, text_wordwrap=14, style=TTDialog.Acknowledge, command=self.__revertDone)
        self.revertDialog.show()

    def __revertDone(self, command):
        self.revertDialog.destroy()
        self.revertDialog = None
        return

    def __doChangeResolution(self):
        if self.displaySettings == None:
            self.displaySettings = DisplaySettingsDialog()
            self.displaySettings.load()
            self.accept(self.displaySettings.doneEvent, self.__doneDisplaySettings)
        self.displaySettings.enter(self.ChangeDisplaySettings, self.ChangeDisplayAPI)

    def __doneDisplaySettings(self, anyChanged, apiChanged):
        if anyChanged:
            properties = base.win.getProperties()
            self.displaySettingsChanged = 1
            self.displaySettingsSize = (properties.getXSize(), properties.getYSize())
            self.displaySettingsApi = base.pipe.getInterfaceName()
            self.displaySettingsApiChanged = apiChanged
            self.__setResolutionButton()
            self.writeDisplaySettings()

    def writeDisplaySettings(self, task=None):
        if not self.displaySettingsChanged:
            return
        # Only save the resolution if we're in fullscreen mode.
        if settings['fullscreen']:
            settings['res'] = [self.displaySettingsSize[0], self.displaySettingsSize[1]]
        # Otherwise, we want the default window size to be 1280x720 (i.e. the starting window size)
        else:
            settings['res'] = [1280, 720]
        return Task.done

    def __doToggleVsync(self):
        settings['vsync'] = not settings['vsync']
        loadPrcFileData('Settings: vsync', 'sync-video %s' % settings['vsync'])
        base.needRestartVsync = True
        self.__setVsyncButton()

    def __doToggleAntialias(self):
        if settings['antialiasing']:
            settings['antialiasing'] = 0
        else:
            settings['antialiasing'] = 4
        loadPrcFileData('Settings: MSAA', 'framebuffer-multisample %s' % (settings['antialiasing'] > 0))
        loadPrcFileData('Settings: MSAA samples', 'multisamples %i' % settings['antialiasing'])
        base.needRestartAntialiasing = True
        self.__setAntialiasingButton()

    def __doToggleFps(self):
        if base.drawFps:
            base.setFrameRateMeter(False)
            base.drawFps = False
            settings['drawFps'] = False
        else:
            base.setFrameRateMeter(True)
            base.drawFps = True
            settings['drawFps'] = True
        self.__setFpsButton()

    def __doToggleSmooth(self):
        settings['smoothAnimations'] = not settings['smoothAnimations']
        loadPrcFileData('Settings: smoothAnimations', 'smooth-animations %s' % settings['smoothAnimations'])
        base.needRestartSmoothing = True
        self.__setSmoothingButton()

    def __doToggleBlend(self):
        pass # todo

    def __doToggleLOD(self):
        settings['enableLODs'] = not settings['enableLODs']
        loadPrcFileData('Settings: enableLODs', 'enable-lods %s' % settings['enableLODs'])
        base.needRestartLOD = True
        self.__setLODButton()

    def __getWaterShaderIndex(self):
        idx = FunnyFarmGlobals.ShaderCustom
        for lvl in FunnyFarmGlobals.WaterShaderLevels:
            if [settings['waterReflectionScale'], settings['waterRefractionScale']] == lvl:
                idx = FunnyFarmGlobals.WaterShaderLevels.index(lvl)
        return idx

    def __doChangeWaterShader(self):
        idx = self.__getWaterShaderIndex()
        if idx == FunnyFarmGlobals.ShaderCustom:
            idx = 0
        else:
            idx = (idx + 1) % len(FunnyFarmGlobals.WaterShaderLevels)
        settings['waterReflectionScale'], settings['waterRefractionScale'] = FunnyFarmGlobals.WaterShaderLevels[idx]
        settings['waterShader'] = idx != 0
        messenger.send('update-shader-settings')
        self.__setWaterShaderButton()

    def __setMusicButton(self):
        if base.musicActive:
            self.Music_Label['text'] = TTLocalizer.OptionsPageMusicOnLabel
            self.Music_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.Music_Label['text'] = TTLocalizer.OptionsPageMusicOffLabel
            self.Music_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn

    def __setSoundFXButton(self):
        if base.sfxActive:
            self.SoundFX_Label['text'] = TTLocalizer.OptionsPageSFXOnLabel
            self.SoundFX_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.SoundFX_Label['text'] = TTLocalizer.OptionsPageSFXOffLabel
            self.SoundFX_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn

    def __setToonChatSoundsButton(self):
        if base.toonChatSounds:
            self.ToonChatSounds_Label['text'] = TTLocalizer.OptionsPageToonChatSoundsOnLabel
            self.ToonChatSounds_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.ToonChatSounds_Label['text'] = TTLocalizer.OptionsPageToonChatSoundsOffLabel
            self.ToonChatSounds_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn
        if base.sfxActive:
            self.ToonChatSounds_Label.setColorScale(1.0, 1.0, 1.0, 1.0)
            self.ToonChatSounds_toggleButton['state'] = DGG.NORMAL
        else:
            self.ToonChatSounds_Label.setColorScale(0.5, 0.5, 0.5, 0.5)
            self.ToonChatSounds_toggleButton['state'] = DGG.DISABLED

    def __setFullscreenButton(self):
        if settings['fullscreen']:
            self.Fullscreen_Label['text'] = TTLocalizer.OptionsPageFullscreenOnLabel
            self.Fullscreen_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.Fullscreen_Label['text'] = TTLocalizer.OptionsPageFullscreenOffLabel
            self.Fullscreen_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn
        if config.GetBool('fullscreen-requires-restart', False):
            self.Fullscreen_Label['text'] += TTLocalizer.OptionsPageRequiresRestart

    def __setResolutionButton(self):
        properties = base.win.getProperties()
        screenSizeIndex = DisplaySettingsDialog.chooseClosestScreenSize(properties.getXSize(), properties.getYSize())
        width, height = DisplaySettingsDialog.screenSizes[screenSizeIndex]
        self.Resolution_Label['text'] = TTLocalizer.OptionsPageResolution % {'screensize': str(width) + ' x ' + str(height)}
        self.Resolution_toggleButton['text'] = TTLocalizer.OptionsPageChange

    def __setVsyncButton(self):
        if settings['vsync']:
            self.Vsync_Label['text'] = TTLocalizer.OptionsPageVsyncOnLabel
            self.Vsync_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.Vsync_Label['text'] = TTLocalizer.OptionsPageVsyncOffLabel
            self.Vsync_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn
        if base.needRestartVsync:
            self.Vsync_Label['text'] += TTLocalizer.OptionsPageRequiresRestart

    def __setAntialiasingButton(self):
        if settings['antialiasing']:
            self.Antialias_Label['text'] = TTLocalizer.OptionsPageAntialiasingOnLabel
            self.Antialias_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.Antialias_Label['text'] = TTLocalizer.OptionsPageAntialiasingOffLabel
            self.Antialias_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn
        if base.needRestartAntialiasing:
            self.Antialias_Label['text'] += TTLocalizer.OptionsPageRequiresRestart

    def __setFpsButton(self):
        if base.drawFps:
            self.Fps_Label['text'] = TTLocalizer.OptionsPageFpsOnLabel
            self.Fps_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.Fps_Label['text'] = TTLocalizer.OptionsPageFpsOffLabel
            self.Fps_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn

    def __setSmoothingButton(self):
        if settings['smoothAnimations']:
            self.Smooth_Label['text'] = TTLocalizer.OptionsPageSmoothingOnLabel
            self.Smooth_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.Smooth_Label['text'] = TTLocalizer.OptionsPageSmoothingOffLabel
            self.Smooth_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn
        if base.needRestartSmoothing:
            self.Smooth_Label['text'] += TTLocalizer.OptionsPageRequiresRestart

    def __setBlendingButton(self):
        self.Blend_Label['text'] = TTLocalizer.OptionsPageBlendingOffLabel
        self.Blend_toggleButton.hide()
        self.Blend_tempText.show()

    def __setLODButton(self):
        if settings['enableLODs']:
            self.LOD_Label['text'] = TTLocalizer.OptionsPageLODOnLabel
            self.LOD_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.LOD_Label['text'] = TTLocalizer.OptionsPageLODOffLabel
            self.LOD_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn
        if base.needRestartLOD:
            self.LOD_Label['text'] += TTLocalizer.OptionsPageRequiresRestart

    def __setWaterShaderButton(self):
        idx = self.__getWaterShaderIndex()
        if not settings['waterShader']:
            idx = 0
        self.WaterShader_Label['text'] = TTLocalizer.OptionsPageWaterShader
        self.WaterShader_toggleButton['text'] = TTLocalizer.OptionsPageShaderLevels[idx]

    def __doToggleAcceptFriends(self):
        acceptingNewFriends = settings.get('acceptingNewFriends', {})
        if base.localAvatar.acceptingNewFriends:
            base.localAvatar.acceptingNewFriends = 0
            acceptingNewFriends[str(base.localAvatar.doId)] = False
        else:
            base.localAvatar.acceptingNewFriends = 1
            acceptingNewFriends[str(base.localAvatar.doId)] = True
        settings['acceptingNewFriends'] = acceptingNewFriends
        self.settingsChanged = 1
        self.__setAcceptFriendsButton()

    def __doToggleAcceptWhispers(self):
        acceptingNonFriendWhispers = settings.get('acceptingNonFriendWhispers', {})
        if base.localAvatar.acceptingNonFriendWhispers:
            base.localAvatar.acceptingNonFriendWhispers = 0
            acceptingNonFriendWhispers[str(base.localAvatar.doId)] = False
        else:
            base.localAvatar.acceptingNonFriendWhispers = 1
            acceptingNonFriendWhispers[str(base.localAvatar.doId)] = True
        settings['acceptingNonFriendWhispers'] = acceptingNonFriendWhispers
        self.settingsChanged = 1
        self.__setAcceptWhispersButton()

    def __setAcceptFriendsButton(self):
        if base.localAvatar.acceptingNewFriends:
            self.Friends_Label['text'] = TTLocalizer.OptionsPageFriendsEnabledLabel
            self.Friends_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.Friends_Label['text'] = TTLocalizer.OptionsPageFriendsDisabledLabel
            self.Friends_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn

    def __setAcceptWhispersButton(self):
        if base.localAvatar.acceptingNonFriendWhispers:
            self.Whispers_Label['text'] = TTLocalizer.OptionsPageWhisperEnabledLabel
            self.Whispers_toggleButton['text'] = TTLocalizer.OptionsPageToggleOff
        else:
            self.Whispers_Label['text'] = TTLocalizer.OptionsPageWhisperDisabledLabel
            self.Whispers_toggleButton['text'] = TTLocalizer.OptionsPageToggleOn

    def __doSpeedChatStyleLeft(self):
        if self.speedChatStyleIndex > 0:
            self.speedChatStyleIndex = self.speedChatStyleIndex - 1
            self.updateSpeedChatStyle()

    def __doSpeedChatStyleRight(self):
        if self.speedChatStyleIndex < len(speedChatStyles) - 1:
            self.speedChatStyleIndex = self.speedChatStyleIndex + 1
            self.updateSpeedChatStyle()

    def updateSpeedChatStyle(self):
        nameKey, arrowColor, rolloverColor, frameColor = speedChatStyles[self.speedChatStyleIndex]
        newSCColorScheme = SCColorScheme.SCColorScheme(arrowColor=arrowColor, rolloverColor=rolloverColor, frameColor=frameColor)
        self.speedChatStyleText.setColorScheme(newSCColorScheme)
        self.speedChatStyleText.clearMenu()
        colorName = SCStaticTextTerminal.SCStaticTextTerminal(nameKey)
        self.speedChatStyleText.append(colorName)
        self.speedChatStyleText.finalize()
        self.speedChatStyleText.setPos(0.445 - self.speedChatStyleText.getWidth() * self.speed_chat_scale / 2, 0, self.speedChatStyleText.getPos()[2])
        if self.speedChatStyleIndex > 0:
            self.speedChatStyleLeftArrow['state'] = DGG.NORMAL
        else:
            self.speedChatStyleLeftArrow['state'] = DGG.DISABLED
        if self.speedChatStyleIndex < len(speedChatStyles) - 1:
            self.speedChatStyleRightArrow['state'] = DGG.NORMAL
        else:
            self.speedChatStyleRightArrow['state'] = DGG.DISABLED
        base.localAvatar.b_setSpeedChatStyleIndex(self.speedChatStyleIndex)

    def enterVsyncHelp(self):
        self.help = TTDialog.TTDialog(text=TTLocalizer.OptionsPageVsyncHelp, text_wordwrap=13, pos=(0, 0, 0.2), style=TTDialog.Acknowledge, command=self.exitHelp)
        self.heading = DirectLabel(parent=self.help, relief=None, text=TTLocalizer.OptionsPageVsyncHeading, text_font=ToontownGlobals.getSignFont(), text_fg=(0.3, 0.3, 0.3, 1), text_scale=0.07, pos=(-0.31, 0, 0.4))
        self.help.show()

    def enterAntialiasHelp(self):
        self.help = TTDialog.TTDialog(text=TTLocalizer.OptionsPageAntialiasingHelp, text_wordwrap=14, pos=(0, 0, 0.2), style=TTDialog.Acknowledge, command=self.exitHelp)
        self.heading = DirectLabel(parent=self.help, relief=None, text=TTLocalizer.OptionsPageAntialiasingHeading, text_font=ToontownGlobals.getSignFont(), text_fg=(0.3, 0.3, 0.3, 1), text_scale=0.07, pos=(-0.205, 0, 0.345))
        self.help.show()

    def enterFpsHelp(self):
        self.help = TTDialog.TTDialog(text=TTLocalizer.OptionsPageFpsHelp, text_wordwrap=14, pos=(0, 0, 0.2), style=TTDialog.Acknowledge, command=self.exitHelp)
        self.heading = DirectLabel(parent=self.help, relief=None, text=TTLocalizer.OptionsPageFpsHeading, text_font=ToontownGlobals.getSignFont(), text_fg=(0.3, 0.3, 0.3, 1), text_scale=0.07, pos=(-0.245, 0, 0.24))
        self.help.show()

    def enterLODHelp(self):
        self.help = TTDialog.TTDialog(text=TTLocalizer.OptionsPageLODHelp, text_wordwrap=14, pos=(0, 0, 0.2), style=TTDialog.Acknowledge, command=self.exitHelp)
        self.heading = DirectLabel(parent=self.help, relief=None, text=TTLocalizer.OptionsPageLODHeading, text_font=ToontownGlobals.getSignFont(), text_fg=(0.3, 0.3, 0.3, 1), text_scale=0.07, pos=(-0.285, 0, 0.345))
        self.help.show()

    def enterShaderLevelHelp(self):
        self.help = TTDialog.TTDialog(text=TTLocalizer.OptionsPageShaderLevelHelp, text_wordwrap=14, pos=(0, 0, 0.2), style=TTDialog.Acknowledge, command=self.exitHelp)
        self.heading = DirectLabel(parent=self.help, relief=None, text=TTLocalizer.OptionsPageShaderLevelHeading, text_font=ToontownGlobals.getSignFont(), text_fg=(0.3, 0.3, 0.3, 1), text_scale=0.07, pos=(-0.215, 0, 0.345))
        self.help.show()

    def exitHelp(self, response):
        self.help.destroy()
        self.heading.destroy()
        del self.help
        del self.heading

    def __handleExitShowWithConfirm(self):
        self.confirm = TTDialog.TTGlobalDialog(doneEvent='confirmDone', message=TTLocalizer.OptionsPageExitConfirm, style=TTDialog.TwoChoice)
        self.confirm.show()
        self.accept('confirmDone', self.__handleConfirm)

    def __handleConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            messenger.send('exitFunnyFarm')
