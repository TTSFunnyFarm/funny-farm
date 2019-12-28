from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.building.Interior import Interior
from toontown.building.SuitInteriorBase import SuitInteriorBase

class MusicManager:
    notify = directNotify.newCategory('MusicManager')

    def __init__(self):
        self.pickAToonMusic = [
            base.loader.loadMusic('phase_3/audio/bgm/ff_theme.ogg'),
            base.loader.loadMusic('phase_3/audio/bgm/ff_theme_winter.ogg'),
            base.loader.loadMusic('phase_3/audio/bgm/ff_theme_halloween.ogg')
        ]
        self.safezoneMusic = {
            FunnyFarmGlobals.Tutorial: base.loader.loadMusic('phase_6/audio/bgm/OZ_SZ.ogg'),
            FunnyFarmGlobals.FunnyFarm: base.loader.loadMusic('phase_14/audio/bgm/FF_nbrhood.ogg'),
            FunnyFarmGlobals.SillySprings: base.loader.loadMusic('phase_14/audio/bgm/SS_nbrhood.ogg')
        }
        self.townMusic = {
            FunnyFarmGlobals.FunnyFarm: base.loader.loadMusic('phase_14/audio/bgm/FF_SZ.ogg'),
            FunnyFarmGlobals.ChillyVillage: base.loader.loadMusic('phase_14/audio/bgm/CV_SZ.ogg'),
        }
        self.activityMusic = {
            FunnyFarmGlobals.FunnyFarm: base.loader.loadMusic('phase_14/audio/bgm/FF_SZ_activity.ogg'),
            FunnyFarmGlobals.SillySprings: base.loader.loadMusic('phase_14/audio/bgm/SS_SZ_activity.ogg')
        }

    def playMusic(self, music, looping=0, volume=1.0, time=0.0):
        self.stopMusic()
        if music:
            base.playMusic(music, looping=looping, volume=volume, time=time)

    def stopMusic(self):
        stopTime = 0.0
        for t in self.pickAToonMusic:
            if t.status() == AudioSound.PLAYING:
                stopTime = t.getTime()
            t.stop()
        for t in list(self.safezoneMusic.keys()):
            if self.safezoneMusic[t].status() == AudioSound.PLAYING:
                stopTime = self.safezoneMusic[t].getTime()
            self.safezoneMusic[t].stop()
        for t in list(self.townMusic.keys()):
            if self.townMusic[t].status() == AudioSound.PLAYING:
                stopTime = self.townMusic[t].getTime()
            self.townMusic[t].stop()
        for t in list(self.activityMusic.keys()):
            if self.activityMusic[t].status() == AudioSound.PLAYING:
                stopTime = self.activityMusic[t].getTime()
            self.activityMusic[t].stop()
        return stopTime

    def playCurrentZoneMusic(self, time=0.0):
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
        self.playMusic(music, looping=1, volume=volume, time=time)

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
