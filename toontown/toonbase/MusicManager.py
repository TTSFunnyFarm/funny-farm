from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.building.Interior import Interior

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
            FunnyFarmGlobals.SillySprings: base.loader.loadMusic('phase_14/audio/bgm/SS_nbrhood.ogg'),
            FunnyFarmGlobals.Estate: None
        }
        self.townMusic = {
            FunnyFarmGlobals.FunnyFarm: base.loader.loadMusic('phase_14/audio/bgm/FF_SZ.ogg'),
            FunnyFarmGlobals.ChillyVillage: base.loader.loadMusic('phase_14/audio/bgm/CV_SZ.ogg'),
        }
        self.activityMusic = {
            FunnyFarmGlobals.FunnyFarm: base.loader.loadMusic('phase_14/audio/bgm/FF_SZ_activity.ogg'),
            FunnyFarmGlobals.SillySprings: base.loader.loadMusic('phase_14/audio/bgm/SS_SZ_activity.ogg'),
            FunnyFarmGlobals.Estate: None
        }

    def playMusic(self, music, looping=0, volume=1.0):
        self.stopMusic()
        if music:
            base.playMusic(music, looping=looping, volume=volume)

    def stopMusic(self):
        for t in self.pickAToonMusic:
            if t != None:
                t.stop()
        for t in self.safezoneMusic.keys():
            if self.safezoneMusic[t] != None:
                self.safezoneMusic[t].stop()
        for t in self.townMusic.keys():
            if self.townMusic[t] != None:
                self.townMusic[t].stop()
        for t in self.activityMusic.keys():
            if self.activityMusic[t] != None:
                self.activityMusic[t].stop()

    def playCurrentZoneMusic(self):
        zoneId = FunnyFarmGlobals.getHoodId(base.localAvatar.getZoneId())
        zone = base.cr.playGame.getActiveZone()
        if zone.place:
            lookupTable = self.activityMusic
            volume = 0.7
        elif base.cr.playGame.hood:
            lookupTable = self.safezoneMusic
            volume = 1.0
        elif base.cr.playGame.street:
            lookupTable = self.townMusic
            volume = 1.0
        else:
            self.notify.warning('playCurrentZoneMusic(): localAvatar is not currently in a valid zone.')
            return None
        if zoneId in lookupTable.keys():
            music = lookupTable[zoneId]
        else:
            self.notify.warning('playCurrentZoneMusic(): music for zone %s not in MusicManager.' % str(zoneId))
            return None
        if music is not None:
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
