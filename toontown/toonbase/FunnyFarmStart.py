import __builtin__

from toontown.toonbase.FunnyFarmLogger import FunnyFarmLogger

__builtin__.logger = FunnyFarmLogger()

from panda3d.core import *

if __debug__:
    loadPrcFile('config/general.prc')

import ToonBase
ToonBase.ToonBase()

class game:
    name = 'toontown'
    process = 'client'

__builtin__.game = game()

from otp.settings.Settings import Settings
from direct.gui import DirectGuiGlobals
from direct.interval.IntervalGlobal import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import FunnyFarmLoader
from toontown.toonbase import MusicManager
from toontown.toonbase import ScreenshotManager
from toontown.login import DataManager
from toontown.distributed import FFClientRepository
from toontown.ai import FFAIRepository
from toontown.misc import Injector
import os

class FunnyFarmStart:
    notify = directNotify.newCategory('FunnyFarmStart')
    notify.setInfo(True)

    def __init__(self):
        self.notify.info('Starting the game.')

        preferencesFilename = ConfigVariableString('preferences-filename', 'preferences.json').getValue()
        dir = os.path.dirname(os.getcwd() + '/' + preferencesFilename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.notify.info('Reading %s...' % preferencesFilename)
        __builtin__.settings = Settings(preferencesFilename)
        if 'fullscreen' not in settings:
            settings['fullscreen'] = False
        if 'music' not in settings:
            settings['music'] = True
        if 'sfx' not in settings:
            settings['sfx'] = True
        if 'musicVol' not in settings:
            settings['musicVol'] = 1.0
        if 'sfxVol' not in settings:
            settings['sfxVol'] = 1.0
        if 'loadDisplay' not in settings:
            settings['loadDisplay'] = 'pandagl'
        if 'toonChatSounds' not in settings:
            settings['toonChatSounds'] = True
        if 'drawFps' not in settings:
            settings['drawFps'] = False
        loadPrcFileData('Settings: res', 'win-size %d %d' % tuple(settings.get('res', (800, 600))))
        loadPrcFileData('Settings: fullscreen', 'fullscreen %s' % settings['fullscreen'])
        loadPrcFileData('Settings: music', 'audio-music-active %s' % settings['music'])
        loadPrcFileData('Settings: sfx', 'audio-sfx-active %s' % settings['sfx'])
        loadPrcFileData('Settings: musicVol', 'audio-master-music-volume %s' % settings['musicVol'])
        loadPrcFileData('Settings: sfxVol', 'audio-master-sfx-volume %s' % settings['sfxVol'])
        loadPrcFileData('Settings: loadDisplay', 'load-display %s' % settings['loadDisplay'])
        loadPrcFileData('Settings: toonChatSounds', 'toon-chat-sounds %s' % settings['toonChatSounds'])
        if settings['fullscreen'] == True:
            properties = WindowProperties()
            properties.setSize(settings['res'][0], settings['res'][1])
            properties.setFullscreen(1)
            properties.setParentWindow(0)
            base.win.requestProperties(properties)
        if settings['music'] == False:
            base.enableMusic(0)
        if settings['sfx'] == False:
            base.enableSoundEffects(0)
        if settings['drawFps'] == True:
            base.setFrameRateMeter(True)
            base.drawFps = 1

        __builtin__.loader = FunnyFarmLoader.FunnyFarmLoader(base)
        __builtin__.musicMgr = MusicManager.MusicManager()
        __builtin__.screenshotMgr = ScreenshotManager.ScreenshotManager()
        __builtin__.dataMgr = DataManager.DataManager()

        self.notify.info('Setting default GUI sounds')
        DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
        DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
        DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))

        self.notify.info('Setting default font')
        DirectGuiGlobals.setDefaultFont(ToontownGlobals.getInterfaceFont())

        self.notify.info('Initializing AI Repository...')
        base.air = FFAIRepository.FFAIRepository()
        base.air.preloadAvatars()
        base.air.createManagers()
        base.air.createSafeZones()
        loader.loadingScreen.load()

        self.notify.info('Initializing Client Repository...')
        cr = FFClientRepository.FFClientRepository()
        base.initNametagGlobals()
        base.startShow(cr)

__builtin__.start = FunnyFarmStart()

base.run()
