from pandac.PandaModules import *
from toontown.toonbase import FunnyFarmGlobals

class MusicManager:
    notify = directNotify.newCategory('MusicManager')

    def __init__(self):
        self.pickAToonMusic = [
            (base.loadMusic('phase_3/audio/bgm/ff_theme.ogg'), 0.5),
            (base.loadMusic('phase_3/audio/bgm/ff_theme_winter.ogg'), 1.0),
            (base.loadMusic('phase_3/audio/bgm/ff_theme_halloween.ogg'), 1.0)
        ]
        self.safezoneMusic = {
            FunnyFarmGlobals.Tutorial: (base.loadMusic('phase_6/audio/bgm/OZ_SZ.ogg'), 1.0),
            FunnyFarmGlobals.FunnyFarm: (base.loadMusic('phase_14/audio/bgm/FF_nbrhood.ogg'), 1.0),
            FunnyFarmGlobals.RicketyRoad: (base.loadMusic('phase_14/audio/bgm/FF_SZ.ogg'), 1.0),
            FunnyFarmGlobals.FunnyFarmCentral: (base.loadMusic('phase_14/audio/bgm/FC_SZ.ogg'), 1.0),
            FunnyFarmGlobals.SillySprings: (base.loadMusic('phase_14/audio/bgm/SS_nbrhood.ogg'), 1.0),
            FunnyFarmGlobals.WintryWay: (base.loadMusic('phase_14/audio/bgm/CV_SZ.ogg'), 1.0),
            FunnyFarmGlobals.SecretArea: (base.loadMusic('phase_12/audio/bgm/Bossbot_Entry_v2.ogg'), 1.0)
        }
        self.shopMusic = {
            FunnyFarmGlobals.FunnyFarm: (base.loadMusic('phase_14/audio/bgm/FF_SZ_activity.ogg'), 0.5),
            FunnyFarmGlobals.SillySprings: (base.loadMusic('phase_14/audio/bgm/SS_SZ_activity.ogg'), 1.0)
        }

    def playMusic(self, music, looping=0, volume=1.0):
        self.stopMusic()
        if music:
            base.playMusic(music, looping=looping, volume=volume)

    def stopMusic(self):
        for t in self.pickAToonMusic:
            t[0].stop()
        for t in self.safezoneMusic.keys():
            self.safezoneMusic[t][0].stop()
        for t in self.shopMusic.keys():
            self.shopMusic[t][0].stop()

    def playCurrentZoneMusic(self):
        zoneId = base.localAvatar.getZoneId()
        if base.cr.playGame.hood or base.cr.playGame.street:
            if zoneId in self.safezoneMusic.keys():
                music, volume = self.safezoneMusic[zoneId]
            else:
                self.notify.warning('Safezone music for zone %s not in MusicManager.' % str(zoneId))
                return
        else:
            if zoneId in self.shopMusic.keys():
                music, volume = self.shopMusic[zoneId]
            else:
                self.notify.warning('Activity music for zone %s not in MusicManager.' % str(zoneId))
                return
        self.playMusic(music, looping=1, volume=volume)

    def playPickAToon(self):
        if base.air.holidayMgr.isWinter():
            music, volume = self.pickAToonMusic[1]
        elif base.air.holidayMgr.isHalloween():
            music, volume = self.pickAToonMusic[2]
        else:
            music, volume = self.pickAToonMusic[0]
        self.playMusic(music, looping=1, volume=volume)
