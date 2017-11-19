from panda3d.core import *
import __builtin__, os
from otp.settings.Settings import Settings
from toontown.toonbase.FunnyFarmLogger import FunnyFarmLogger

__builtin__.logger = FunnyFarmLogger()

if __debug__:
    loadPrcFile('config/general.prc')

# This has to be done before ToonBase loads so we can use antialiasing
preferencesFilename = ConfigVariableString('preferences-filename', 'preferences.json').getValue()
dir = os.path.dirname(os.getcwd() + '/' + preferencesFilename)
if not os.path.exists(dir):
    os.makedirs(dir)
print('Reading %s...' % preferencesFilename)
__builtin__.settings = Settings(preferencesFilename)
if 'antialiasing' not in settings:
    settings['antialiasing'] = 0
loadPrcFileData('Settings: MSAA', 'framebuffer-multisample %s' % (settings['antialiasing'] > 0))
loadPrcFileData('Settings: MSAA samples', 'multisamples %i' % settings['antialiasing'])

import ToonBase
ToonBase.ToonBase()

class game:
    name = 'toontown'
    process = 'client'

__builtin__.game = game()

from direct.gui import DirectGuiGlobals
from direct.interval.IntervalGlobal import *
from direct.stdpy import threading
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase.MusicManager import MusicManager
from toontown.toonbase.ScreenshotManager import ScreenshotManager
from toontown.login.DataManager import DataManager
from toontown.login.TitleScreen import TitleScreen
from toontown.ai.FFAIRepository import FFAIRepository
from toontown.distributed.FFClientRepository import FFClientRepository
from toontown.misc import Injector
from toontown.misc import PythonUtil

class FunnyFarmStart:
    notify = directNotify.newCategory('FunnyFarmStart')
    notify.setInfo(True)

    def __init__(self):
        self.notify.info('Starting the game.')

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
        if 'enableLODs' not in settings:
            settings['enableLODs'] = False
        loadPrcFileData('Settings: res', 'win-size %d %d' % tuple(settings.get('res', (800, 600))))
        loadPrcFileData('Settings: fullscreen', 'fullscreen %s' % settings['fullscreen'])
        loadPrcFileData('Settings: music', 'audio-music-active %s' % settings['music'])
        loadPrcFileData('Settings: sfx', 'audio-sfx-active %s' % settings['sfx'])
        loadPrcFileData('Settings: musicVol', 'audio-master-music-volume %s' % settings['musicVol'])
        loadPrcFileData('Settings: sfxVol', 'audio-master-sfx-volume %s' % settings['sfxVol'])
        loadPrcFileData('Settings: loadDisplay', 'load-display %s' % settings['loadDisplay'])
        loadPrcFileData('Settings: toonChatSounds', 'toon-chat-sounds %s' % settings['toonChatSounds'])
        loadPrcFileData('Settings: enableLODs', 'enable-lods %s' % settings['enableLODs'])
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

        self.notify.info('Setting default GUI globals')
        DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
        DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
        DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))
        DirectGuiGlobals.setDefaultFont(ToontownGlobals.getInterfaceFont())

        self.notify.info('Initializing AI Repository...')
        base.air = FFAIRepository()
        base.air.preloadAvatars()
        base.air.createManagers()
        loader.loadingScreen.load()

        __builtin__.musicMgr = MusicManager()
        __builtin__.screenshotMgr = ScreenshotManager()
        __builtin__.dataMgr = DataManager()

        self.notify.info('Initializing Client Repository...')
        cr = FFClientRepository()
        base.initNametagGlobals()
        base.startShow(cr)
        # Can't start a new thread right away otherwise we'll crash panda
        taskMgr.doMethodLater(0.1, self.startAI, 'startAI')

    def startAI(self, task):
        threading.Thread(target=base.air.createSafeZones).start()
        return task.done

__builtin__.start = FunnyFarmStart()

base.run()
