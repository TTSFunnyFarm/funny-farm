from pandac.PandaModules import *

loadPrcFile('config/general.prc')

from direct.showbase import ShowBase

base = ShowBase.ShowBase()

import __builtin__

class game:
    name = 'toontown'
    process = 'client'

base.game = game()

from otp.settings.Settings import Settings
from direct.gui import DirectGuiGlobals as DGG
from direct.interval.IntervalGlobal import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import FunnyFarmLoader
from toontown.sound import SoundManager
from toontown.login import DataManager
from toontown.distributed import FFClientRepository
from toontown.misc import Injector
import os

class FunnyFarmStart:
    notify = directNotify.newCategory('FunnyFarmStart')
    notify.setInfo(True)

    def __init__(self):
        self.notify.info('Starting the game.')

        preferencesFilename = Filename(Filename.getUserAppdataDirectory() + '/FunnyFarm/preferences.json')
        dir = os.path.dirname(preferencesFilename.toOsSpecific())
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.notify.info('Reading %s...' % preferencesFilename.getBasename())
        __builtin__.settings = Settings(preferencesFilename.toOsSpecific())
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
        base.toonChatSounds = base.config.GetBool('toon-chat-sounds', 1)
        base.drawFps = False

        if settings['music'] == False:
            base.enableMusic(0)
        if settings['sfx'] == False:
            base.enableSoundEffects(0)
        if settings['drawFps'] == True:
            base.setFrameRateMeter(True)
            base.drawFps = True

        __builtin__.loader = FunnyFarmLoader.FunnyFarmLoader(base)
        __builtin__.soundMgr = SoundManager.SoundManager()
        __builtin__.dataMgr = DataManager.DataManager()

        self.notify.info('Setting default GUI sounds')
        click = loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg')
        rollover = loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg')
        DGG.setDefaultClickSound(click)
        DGG.setDefaultRolloverSound(rollover)

        self.notify.info('Setting default font')
        DGG.setDefaultFont(ToontownGlobals.getInterfaceFont())

        FunnyFarmGlobals.addCullBins()
        FunnyFarmGlobals.setNametagGlobals()
        base.enableParticles()

        self.notify.info('Setting up Client Repository...')
        base.cr = FFClientRepository.FFClientRepository()
        if base.config.GetBool('quick-start', 0):
            __builtin__.playToken = base.config.GetString('quick-start-playToken', '')
            if playToken:
                self.notify.info('Quick-starting game with playToken: %s' % playToken)
                dataMgr.loadAccount(playToken)
                self.startFunnyFarm()
            else:
                self.notify.error('Quick-start failed. No playToken given.')
        else:
            base.cr.enterLogin()

    def startFunnyFarm(self):
        base.transitions.noTransitions()
        soundMgr.startPAT()
        loader.beginBulkLoad('init', 0, 0, 0)
        base.cr.loadPAT()
        loader.endBulkLoad('init')
        base.cr.fakeConnect()

__builtin__.start = FunnyFarmStart()
Injector.openInjector()

base.run()
