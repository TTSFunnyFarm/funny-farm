from pandac.PandaModules import *
from toontown.toonbase import FunnyFarmGlobals

class MusicManager:

    def __init__(self):
        self.musicList = map(
            base.loadMusic, [
                    'phase_4/audio/bgm/minigame_race.ogg',
                    'phase_3/audio/bgm/ff_theme.ogg',
                    'phase_3/audio/bgm/ff_theme_winter.ogg',
                    'phase_3/audio/bgm/ff_theme_halloween.ogg',
                    'phase_3/audio/bgm/create_a_toon.ogg',
                    'phase_6/audio/bgm/OZ_SZ.ogg',
                    'phase_14/audio/bgm/FF_nbrhood.ogg',
                    'phase_14/audio/bgm/FF_SZ.ogg',
                    'phase_14/audio/bgm/FF_SZ_activity.ogg',
                    'phase_14/audio/bgm/SS_nbrhood.ogg',
                    'phase_14/audio/bgm/SS_SZ.ogg',
                    'phase_14/audio/bgm/SS_SZ_activity.ogg',
                    'phase_14/audio/bgm/CV_SZ.ogg',
                    'phase_12/audio/bgm/Bossbot_Entry_v2.ogg'
            ]
        )
        self.safezoneMusicMap = {
            FunnyFarmGlobals.FunnyFarm : self.startFFNbrhood,
            FunnyFarmGlobals.FunnyFarmCentral : self.startFFSZ,
            FunnyFarmGlobals.SillySprings : self.startSSNbrhood,
            FunnyFarmGlobals.RicketyRoad : self.startSSSZ,
            FunnyFarmGlobals.WintryWay : self.startCVSZ,
            FunnyFarmGlobals.SecretArea : self.startSecretArea
        }
        self.shopMusicMap = {
            FunnyFarmGlobals.FunnyFarm : self.startFFActivity,
            FunnyFarmGlobals.SillySprings : self.startSSActivity
        }

    def playMusic(self, index, volume=1.0):
        self.stopAllMusic()
        base.playMusic(self.musicList[index], looping=1, volume=volume)

    def stopAllMusic(self):
        for x in self.musicList:
            x.stop()

    def startLogin(self):
        self.playMusic(0)

    def stopLogin(self):
        self.musicList[0].stop()

    def startPAT(self):
        if base.air.holidayMgr.isWinter():
            self.playMusic(2)
        elif base.air.holidayMgr.isHalloween():
            self.playMusic(3)
        else:
            self.playMusic(1, volume=0.5)

    def stopPAT(self):
        self.musicList[1].stop()
        self.musicList[2].stop()
        self.musicList[3].stop()

    def startMAT(self):
        self.playMusic(4)

    def stopMAT(self):
        self.musicList[4].stop()

    def startTutorial(self):
        self.playMusic(5)

    def stopTutorial(self):
        self.musicList[5].stop()

    def startFFNbrhood(self):
        self.playMusic(6)

    def stopFFNbrhood(self):
        self.musicList[6].stop()

    def startFFSZ(self):
        self.playMusic(7)

    def stopFFSZ(self):
        self.musicList[7].stop()

    def startFFActivity(self):
        self.playMusic(8, volume=0.5)

    def stopFFActivity(self):
        self.musicList[8].stop()

    def startSSNbrhood(self):
        self.playMusic(9)

    def stopSSNbrhood(self):
        self.musicList[9].stop()

    def startSSSZ(self):
        self.playMusic(10)

    def stopSSSZ(self):
        self.musicList[10].stop()

    def startSSActivity(self):
        self.playMusic(11)

    def stopSSActivity(self):
        self.musicList[11].stop()

    def startCVSZ(self):
        self.playMusic(12)

    def stopCVSZ(self):
        self.musicList[12].stop()

    def startSecretArea(self):
        self.playMusic(13)

    def stopSecretArea(self):
        self.musicList[13].stop()
