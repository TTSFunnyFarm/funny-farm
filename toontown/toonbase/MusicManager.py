from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.building.Interior import Interior
from toontown.building.SuitInteriorBase import SuitInteriorBase
from direct.showbase.DirectObject import DirectObject

class MusicManager(DirectObject):
    notify = directNotify.newCategory('MusicManager')

    def __init__(self):
        self.volume = settings['musicVol']
        self.track = None
        self.trackName = None
        self.multiplier = 1.0
        self.pauseTime = None
        self.pickAToonMusic = [
            base.loader.loadMusic('phase_3/audio/bgm/ff_theme.ogg'),
            base.loader.loadMusic('phase_3/audio/bgm/ff_theme_winter.ogg'),
            base.loader.loadMusic('phase_3/audio/bgm/ff_theme_halloween.ogg')
        ]
        self.safezoneMusic = {
            FunnyFarmGlobals.Tutorial: base.loader.loadMusic('phase_6/audio/bgm/OZ_SZ.ogg'),
            FunnyFarmGlobals.FunnyFarm: base.loader.loadMusic('phase_14/audio/bgm/FF_nbrhood.ogg'),
            FunnyFarmGlobals.SillySprings: base.loader.loadMusic('phase_14/audio/bgm/SS_nbrhood.ogg'),
            FunnyFarmGlobals.Estate: base.loader.loadMusic('phase_4/audio/bgm/TC_nbrhood.ogg')
        }
        self.townMusic = {
            FunnyFarmGlobals.FunnyFarm: base.loader.loadMusic('phase_14/audio/bgm/FF_SZ.ogg'),
            FunnyFarmGlobals.ChillyVillage: base.loader.loadMusic('phase_14/audio/bgm/CV_SZ.ogg'),
        }
        self.activityMusic = {
            FunnyFarmGlobals.FunnyFarm: base.loader.loadMusic('phase_14/audio/bgm/FF_SZ_activity.ogg'),
            FunnyFarmGlobals.SillySprings: base.loader.loadMusic('phase_14/audio/bgm/SS_SZ_activity.ogg'),
            FunnyFarmGlobals.Estate: base.loader.loadMusic('phase_3.5/audio/bgm/TC_SZ_activity.ogg')
        }
        self.accept('PandaPaused', self.__audioPaused)
        self.accept('PandaRestarted', self.__audioRestarted)

    def setVolume(self, volume):
        self.volume = volume
        if self.track:
            self.track.setVolume(volume * self.getMultiplier())

    def getVolume(self):
        return self.volume

    def setMultiplier(self, multi):
        self.multiplier = multi

    def getMultiplier(self):
        return self.multiplier

    def playMusic(self, music, looping=0, volume=1.0, time=0.0):
        if music:
            self.stopMusic()
            if self.pauseTime:
                volume = self.getMultiplier()
            else:
                self.setMultiplier(volume)
            volume = self.getMultiplier() * self.getVolume()
            self.track = music
            self.trackName = self.track
            self.track.setLoop(looping)
            self.track.setVolume(volume)
            self.track.setTime(time)
            self.track.play()
            return self.track
        else:
            self.notify.warning("Invalid track %s was passed to playMusic." % str(music))
            return None

    def stopMusic(self):
        if self.track:
            self.track.stop()

    def playCurrentZoneMusic(self):
        zoneId = FunnyFarmGlobals.getHoodId(base.localAvatar.getZoneId())
        zone = base.cr.playGame.getActiveZone()
        if zone.place:
            if isinstance(zone.place, SuitInteriorBase):
                return
            lookupTable = self.activityMusic
            volume = 0.5
        elif base.cr.playGame.hood:
            lookupTable = self.safezoneMusic
            volume = 1.0
        elif base.cr.playGame.street:
            lookupTable = self.townMusic
            volume = 1.0
        else:
            self.notify.warning('playCurrentZoneMusic(): localAvatar is not currently in a valid zone.')
            return
        if zoneId in list(lookupTable.keys()):
            music = lookupTable[zoneId]
        else:
            self.notify.warning('playCurrentZoneMusic(): music for zone %s not in MusicManager.' % str(zoneId))
            return
        self.playMusic(music, looping=1, volume=volume)

    def playPickAToon(self):
        if base.air.holidayMgr.isWinter():
            music = self.pickAToonMusic[1]
            volume = 1.0
        elif base.air.holidayMgr.isHalloween():
            music = self.pickAToonMusic[2]
            volume = 1.0
        else:
            music = self.pickAToonMusic[0]
            volume = 0.5
        self.playMusic(music, looping=1, volume=volume)

    def pauseMusic(self):
        self.__audioPaused()
        self.stopMusic()

    def unpauseMusic(self):
        self.__audioRestarted()

    def __audioPaused(self):
        if self.track:
            self.pauseTime = self.track.getTime()

    def __audioRestarted(self):
        if hasattr(base, "localAvatar") and base.localAvatar:
            base.localAvatar.stopSound()
        if self.pauseTime and self.track:
            self.track.setTime(self.pauseTime)
            self.track.play()
            self.pauseTime = None
