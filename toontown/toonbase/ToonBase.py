from otp.otpbase import OTPBase
from otp.otpbase import OTPGlobals
from otp.ai.MagicWordGlobal import *
from direct.showbase.PythonUtil import *
from toontown.toonbase import ToontownGlobals
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import FunnyFarmLoader
from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import *
from direct.showbase.Transitions import Transitions
from panda3d.core import *
from libotp import *
from direct.interval.IntervalGlobal import Sequence, Func, Wait
import sys
import os
import math
import tempfile
import shutil
import atexit
import io
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.toontowngui import TTDialog
from sys import platform
import time
from panda3d.core import TrueClock

class ToonBase(OTPBase.OTPBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToonBase')
    notify.setInfo(1)

    def __init__(self):
        OTPBase.OTPBase.__init__(self)
        self.disableShowbaseMouse()
        base.debugRunningMultiplier /= OTPGlobals.ToonSpeedFactor
        self.toonChatSounds = self.config.GetBool('toon-chat-sounds', 1)
        self.placeBeforeObjects = config.GetBool('place-before-objects', 1)
        self.toonChatSounds = self.config.GetBool('enable-lods', True)
        self.endlessQuietZone = False
        self.wantDynamicShadows = 0
        self.exitErrorCode = 0
        camera.setPosHpr(0, 0, 0, 0, 0, 0)
        self.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
        self.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
        self.cam2d.node().setCameraMask(BitMask32.bit(1))
        self.musicManager.setVolume(0.65)
        self.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        tpm = TextPropertiesManager.getGlobalPtr()
        candidateActive = TextProperties()
        candidateActive.setTextColor(0, 0, 1, 1)
        tpm.setProperties('candidate_active', candidateActive)
        candidateInactive = TextProperties()
        candidateInactive.setTextColor(0.3, 0.3, 0.7, 1)
        tpm.setProperties('candidate_inactive', candidateInactive)
        self.transitions.IrisModelName = 'phase_3/models/misc/iris'
        self.transitions.FadeModelName = 'phase_3/models/misc/fade'
        self.snapshotSfx = base.loader.loadSfx('phase_4/audio/sfx/Photo_shutter.ogg')
        self.flashTrack = None
        self.exitFunc = self.userExit
        globalClock.setMaxDt(0.2)
        if self.config.GetBool('want-particles', 1) == 1:
            self.notify.debug('Enabling particles')
            self.enableParticles()

        # OS X Specific Actions
        if platform == "darwin":
            self.acceptOnce(ToontownGlobals.QuitGameHotKeyOSX, self.exitOSX)
            self.accept(ToontownGlobals.QuitGameHotKeyRepeatOSX, self.exitOSX)
            self.acceptOnce(ToontownGlobals.HideGameHotKeyOSX, self.hideGame)
            self.accept(ToontownGlobals.HideGameHotKeyRepeatOSX, self.hideGame)
            self.acceptOnce(ToontownGlobals.MinimizeGameHotKeyOSX, self.minimizeGame)
            self.accept(ToontownGlobals.MinimizeGameHotKeyRepeatOSX, self.minimizeGame)

        self.accept('f3', self.toggleGui)
        self.accept('panda3d-render-error', self.panda3dRenderError)
        oldLoader = self.loader
        self.loader = FunnyFarmLoader.FunnyFarmLoader(self)
        __builtins__['loader'] = self.loader
        oldLoader.destroy()
        self.accept('PandaPaused', self.disableAllAudio)
        self.accept('PandaRestarted', self.enableAllAudio)
        self.friendMode = self.config.GetBool('switchboard-friends', 0)
        self.wantPets = self.config.GetBool('want-pets', 1)
        self.wantBingo = self.config.GetBool('want-fish-bingo', 1)
        self.wantKarts = self.config.GetBool('want-karts', 1)
        self.wantNewSpecies = self.config.GetBool('want-new-species', 0)
        self.inactivityTimeout = self.config.GetFloat('inactivity-timeout', ToontownGlobals.KeyboardTimeout)
        if self.inactivityTimeout:
            self.notify.debug('Enabling Panda timeout: %s' % self.inactivityTimeout)
            self.mouseWatcherNode.setInactivityTimeout(self.inactivityTimeout)
        self.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
        self.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
        self.mouseWatcherNode.setButtonDownPattern('button-down-%r')
        self.mouseWatcherNode.setButtonUpPattern('button-up-%r')
        self.randomMinigameAbort = self.config.GetBool('random-minigame-abort', 0)
        self.randomMinigameDisconnect = self.config.GetBool('random-minigame-disconnect', 0)
        self.randomMinigameNetworkPlugPull = self.config.GetBool('random-minigame-netplugpull', 0)
        self.autoPlayAgain = self.config.GetBool('auto-play-again', 0)
        self.skipMinigameReward = self.config.GetBool('skip-minigame-reward', 0)
        self.wantMinigameDifficulty = self.config.GetBool('want-minigame-difficulty', 0)
        self.minigameDifficulty = self.config.GetFloat('minigame-difficulty', -1.0)
        if self.minigameDifficulty == -1.0:
            del self.minigameDifficulty
        self.minigameSafezoneId = self.config.GetInt('minigame-safezone-id', -1)
        if self.minigameSafezoneId == -1:
            del self.minigameSafezoneId
        cogdoGameSafezoneId = self.config.GetInt('cogdo-game-safezone-id', -1)
        cogdoGameDifficulty = self.config.GetFloat('cogdo-game-difficulty', -1)
        if cogdoGameDifficulty != -1:
            self.cogdoGameDifficulty = cogdoGameDifficulty
        if cogdoGameSafezoneId != -1:
            self.cogdoGameSafezoneId = cogdoGameSafezoneId
        ToontownBattleGlobals.SkipMovie = self.config.GetBool('skip-battle-movies', 0)
        self.creditCardUpFront = self.config.GetInt('credit-card-up-front', -1)
        if self.creditCardUpFront == -1:
            del self.creditCardUpFront
        else:
            self.creditCardUpFront = self.creditCardUpFront != 0
        self.housingEnabled = self.config.GetBool('want-housing', 1)
        self.cannonsEnabled = self.config.GetBool('estate-cannons', 0)
        self.fireworksEnabled = self.config.GetBool('estate-fireworks', 0)
        self.dayNightEnabled = self.config.GetBool('estate-day-night', 0)
        self.cloudPlatformsEnabled = self.config.GetBool('estate-clouds', 0)
        self.greySpacing = self.config.GetBool('allow-greyspacing', 0)
        self.goonsEnabled = self.config.GetBool('estate-goon', 0)
        self.restrictTrialers = self.config.GetBool('restrict-trialers', 1)
        self.roamingTrialers = self.config.GetBool('roaming-trialers', 1)
        self.slowQuietZone = self.config.GetBool('slow-quiet-zone', 0)
        self.slowQuietZoneDelay = self.config.GetFloat('slow-quiet-zone-delay', 5)
        self.killInterestResponse = self.config.GetBool('kill-interest-response', 0)
        tpMgr = TextPropertiesManager.getGlobalPtr()
        WLDisplay = TextProperties()
        WLDisplay.setSlant(0.3)
        WLEnter = TextProperties()
        WLEnter.setTextColor(1.0, 0.0, 0.0, 1)
        tpMgr.setProperties('WLDisplay', WLDisplay)
        tpMgr.setProperties('WLEnter', WLEnter)
        del tpMgr
        if not __debug__:
            CullBinManager.getGlobalPtr().addBin('gui-popup', CullBinManager.BTUnsorted, 60)
        CullBinManager.getGlobalPtr().addBin('shadow', CullBinManager.BTFixed, 15)
        CullBinManager.getGlobalPtr().addBin('ground', CullBinManager.BTFixed, 14)
        self.lastScreenShotTime = globalClock.getRealTime()
        self.accept('InputState-forward', self.__walking)
        self.canScreenShot = 1
        self.glitchCount = 0
        self.walking = 0
        self.oldX = max(1, base.win.getXSize())
        self.oldY = max(1, base.win.getYSize())
        self.aspectRatio = float(self.oldX) / self.oldY
        self.localAvatarStyle = None
        self.drawFps = 0
        self.secretAreaFlag = 1
        self.needRestartVsync = False
        self.needRestartAntialiasing = False
        self.needRestartSmoothing = False
        self.needRestartLOD = False
        self.consoleDisplay = OnscreenText(text='h', fg=(1, 1, 1, 1), bg=(0,0,0,0.5), wordwrap=93, pos=(0.11, -0.04), scale=0.04, align=TextNode.ALeft, parent = base.a2dTopLeft, mayChange=1)
        self.consoleData = io.StringIO()
        logger.setDisplay(self.consoleDisplay)
        self.consoleDisplay.hide()
        taskMgr.add(logger.refreshDisplay, 'refreshConsole')
        return

    def openMainWindow(self, *args, **kw):
        result = OTPBase.OTPBase.openMainWindow(self, *args, **kw)
        self.setCursorAndIcon()
        return result

    def setFrameRateMeter(self, flag):
        OTPBase.OTPBase.setFrameRateMeter(self, flag)
        if self.frameRateMeter:
            self.frameRateMeter.setFont(ToontownGlobals.getSignFont())

    def windowEvent(self, win):
        OTPBase.OTPBase.windowEvent(self, win)
        if not config.GetInt('keep-aspect-ratio', 0):
            return
        x = max(1, win.getXSize())
        y = max(1, win.getYSize())
        maxX = base.pipe.getDisplayWidth()
        maxY = base.pipe.getDisplayHeight()
        cwp = win.getProperties()
        originX = 0
        originY = 0
        if cwp.hasOrigin():
            originX = cwp.getXOrigin()
            originY = cwp.getYOrigin()
            if originX > maxX:
                originX = originX - maxX
            if originY > maxY:
                oringY = originY - maxY
        maxX -= originX
        maxY -= originY
        if math.fabs(x - self.oldX) > math.fabs(y - self.oldY):
            newY = x / self.aspectRatio
            newX = x
            if newY > maxY:
                newY = maxY
                newX = self.aspectRatio * maxY
        else:
            newX = self.aspectRatio * y
            newY = y
            if newX > maxX:
                newX = maxX
                newY = maxX / self.aspectRatio
        wp = WindowProperties()
        wp.setSize(newX, newY)
        base.win.requestProperties(wp)
        base.cam.node().getLens().setFilmSize(newX, newY)
        self.oldX = newX
        self.oldY = newY

    def setCursorAndIcon(self):
        tempdir = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, tempdir)
        vfs = VirtualFileSystem.getGlobalPtr()

        searchPath = DSearchPath()
        searchPath.appendDirectory(Filename('resources/phase_3/etc'))

        for filename in ['toonmono.cur', 'funnyfarm.ico']:
            p3filename = Filename(filename)
            found = vfs.resolveFilename(p3filename, searchPath)
            if not found:
                return  # Can't do anything past this point.

            with open(os.path.join(tempdir, filename), 'wb') as f:
                f.write(vfs.readFile(p3filename, False))

        wp = WindowProperties()
        wp.setCursorFilename(Filename.fromOsSpecific(os.path.join(tempdir, 'toonmono.cur')))
        wp.setIconFilename(Filename.fromOsSpecific(os.path.join(tempdir, 'funnyfarm.ico')))
        self.win.requestProperties(wp)

    def disableShowbaseMouse(self):
        self.useDrive()
        self.disableMouse()
        if self.mouseInterface:
            self.mouseInterface.detachNode()
        if base.mouse2cam:
            self.mouse2cam.detachNode()

    def __walking(self, pressed):
        self.walking = pressed

    def toggleGui(self):
        if aspect2d.isHidden() and not base.cr.cutsceneMgr.getCurrentScene():
            if settings['drawFps']:
                base.setFrameRateMeter(True)
            self.showUI()
        else:
            if settings['drawFps']:
                base.setFrameRateMeter(False)
            self.hideUI()

    def initNametagGlobals(self):
        arrow = loader.loadModel('phase_3/models/props/arrow')
        card = loader.loadModel('phase_3/models/props/panel')
        speech3d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox'))
        thought3d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox_thought_cutout'))
        speech2d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox_noarrow'))
        chatButtonGui = loader.loadModel('phase_3/models/gui/chat_button_gui')
        NametagGlobals.setCamera(self.cam)
        NametagGlobals.setArrowModel(arrow)
        NametagGlobals.setNametagCard(card, VBase4(-0.5, 0.5, -0.5, 0.5))
        if self.mouseWatcherNode:
            NametagGlobals.setMouseWatcher(self.mouseWatcherNode)
        NametagGlobals.setSpeechBalloon3d(speech3d)
        NametagGlobals.setThoughtBalloon3d(thought3d)
        NametagGlobals.setSpeechBalloon2d(speech2d)
        NametagGlobals.setThoughtBalloon2d(thought3d)
        NametagGlobals.setPageButton(PGButton.SReady, chatButtonGui.find('**/Horiz_Arrow_UP'))
        NametagGlobals.setPageButton(PGButton.SDepressed, chatButtonGui.find('**/Horiz_Arrow_DN'))
        NametagGlobals.setPageButton(PGButton.SRollover, chatButtonGui.find('**/Horiz_Arrow_Rllvr'))
        NametagGlobals.setQuitButton(PGButton.SReady, chatButtonGui.find('**/CloseBtn_UP'))
        NametagGlobals.setQuitButton(PGButton.SDepressed, chatButtonGui.find('**/CloseBtn_DN'))
        NametagGlobals.setQuitButton(PGButton.SRollover, chatButtonGui.find('**/CloseBtn_Rllvr'))
        rolloverSound = DirectGuiGlobals.getDefaultRolloverSound()
        if rolloverSound:
            NametagGlobals.setRolloverSound(rolloverSound)
        clickSound = DirectGuiGlobals.getDefaultClickSound()
        if clickSound:
            NametagGlobals.setClickSound(clickSound)
        NametagGlobals.setToon(self.cam)
        self.marginManager = MarginManager()
        self.margins = self.aspect2d.attachNewNode(self.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
        mm = self.marginManager
        self.leftCells = [mm.addGridCell(0, 1, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -1.5)), mm.addGridCell(0, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -1.16667)), mm.addGridCell(0, 3, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -0.833333))]
        self.bottomCells = [mm.addGridCell(1.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (-0.8, 0, 0.166667)), mm.addGridCell(3.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (0.8, 0, 0.166667))]
        self.rightCells = [mm.addGridCell(5, 1, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopRight, (-0.222222, 0, -1.5)), mm.addGridCell(5, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopRight, (-0.222222, 0, -1.16667)), mm.addGridCell(5, 3, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopRight, (-0.222222, 0, -0.833333))]

    def setCellsAvailable(self, cell_list, available):
        for cell in cell_list:
            self.marginManager.setCellAvailable(cell, available)

    def cleanupDownloadWatcher(self):
        self.downloadWatcher.cleanup()
        self.downloadWatcher = None
        return

    def startShow(self, cr):
        self.cr = cr
        if settings['antialiasing']:
            render.setAntialias(AntialiasAttrib.MAuto)
        from toontown.login.TitleScreen import TitleScreen
        musicMgr.playPickAToon()
        titleScreen = TitleScreen()
        titleScreen.startShow()

    def removeGlitchMessage(self):
        self.ignore('InputState-forward')
        print('ignoring InputState-forward')

    def exitShow(self, errorCode = None):
        self.notify.setInfo(1)
        self.notify.info('Exiting Toontown: errorCode = %s' % errorCode)
        sys.exit()

    def setExitErrorCode(self, code):
        self.exitErrorCode = code

    def getExitErrorCode(self):
        return self.exitErrorCode

    def userExit(self):
        try:
            self.localAvatar.setAnimState('TeleportOut', 1)
        except:
            pass

        try:
            localAvatar
        except:
            pass

        messenger.send('clientLogout')
        self.cr.shutdown()
        self.notify.warning('Could not request shutdown; exiting anyway.')
        self.ignore(ToontownGlobals.QuitGameHotKeyOSX)
        self.ignore(ToontownGlobals.QuitGameHotKeyRepeatOSX)
        self.ignore(ToontownGlobals.HideGameHotKeyOSX)
        self.ignore(ToontownGlobals.HideGameHotKeyRepeatOSX)
        self.ignore(ToontownGlobals.MinimizeGameHotKeyOSX)
        self.ignore(ToontownGlobals.MinimizeGameHotKeyRepeatOSX)
        self.exitShow()

    def panda3dRenderError(self):
        sys.exit()

    def getShardPopLimits(self):
        return (config.GetInt('shard-low-pop', ToontownGlobals.LOW_POP), config.GetInt('shard-mid-pop', ToontownGlobals.MID_POP), config.GetInt('shard-high-pop', ToontownGlobals.HIGH_POP))

    def playMusic(self, music, looping = 0, interrupt = 1, volume = None, time = 0.0):
        OTPBase.OTPBase.playMusic(self, music, looping, interrupt, volume, time)

    def handleGameError(self, details):
        if self.cr.playingGame:
            self.cr.cleanupGame()
        self.enableMusic(0)
        render.hide()
        self.hideUI()
        self.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        dialog = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.GameError % details, style=TTDialog.Acknowledge, text_wordwrap=16, command=self.exitShow)
        dialog.show()

    # OS X Specific Actions
    def exitOSX(self):
        self.confirm = TTDialog.TTGlobalDialog(doneEvent='confirmDone', message=TTLocalizer.OptionsPageExitConfirm, style=TTDialog.TwoChoice)
        self.confirm.show()
        self.accept('confirmDone', self.handleConfirm)

    def handleConfirm(self):
        status = self.confirm.doneStatus
        self.ignore('confirmDone')
        self.confirm.cleanup()
        del self.confirm
        if status == 'ok':
            self.userExit()

    def hideGame(self):
        # Hacky, I know, but it works
        hideCommand = """osascript -e 'tell application "System Events"
                                            set frontProcess to first process whose frontmost is true
                                            set visible of frontProcess to false
                                       end tell'"""
        os.system(hideCommand)

    def minimizeGame(self):
        wp = WindowProperties()
        wp.setMinimized(True)
        base.win.requestProperties(wp)

    def showUI(self):
        aspect2d.show()
        NodePath(self.marginManager).reparentTo(aspect2d)

    def hideUI(self):
        NodePath(self.marginManager).reparentTo(aspect2dp)
        aspect2d.hide()

    @magicWord()
    def console():
        if base.consoleDisplay.isHidden():
            base.consoleDisplay.show()
        else:
            base.consoleDisplay.hide()
