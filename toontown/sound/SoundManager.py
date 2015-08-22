from pandac.PandaModules import *
from toontown.toonbase import FFTime

class SoundManager:
<<<<<<< HEAD
	
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
				'phase_12/audio/bgm/Bossbot_Entry_v2.ogg'
			]
		)
=======
>>>>>>> origin/master

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
                        'phase_14/audio/bgm/SS_SZ.ogg'
                ]
        )

    def playMusic(self, music, volume=1.0):
        self.stopAllMusic()
        base.playMusic(music, looping=1, volume=volume)

    def stopAllMusic(self):
        for x in self.musicList:
            x.stop()

    def startLogin(self):
        self.playMusic(self.musicList[0])

    def stopLogin(self):
        self.musicList[0].stop()

    def startPAT(self):
        if FFTime.isWinter():
            self.playMusic(self.musicList[2])
        elif FFTime.isHalloween():
            self.playMusic(self.musicList[3])
        else:
            self.playMusic(self.musicList[1])

    def stopPAT(self):
        self.musicList[1].stop()
        self.musicList[2].stop()
        self.musicList[3].stop()

    def startMAT(self):
        self.playMusic(self.musicList[4])

    def stopMAT(self):
        self.musicList[4].stop()

    def startTutorial(self):
        self.playMusic(self.musicList[5], volume=0.5)

    def stopTutorial(self):
        self.musicList[5].stop()

    def startFFNbrhood(self):
        self.playMusic(self.musicList[6])

    def stopFFNbrhood(self):
        self.musicList[6].stop()

    def startFFSZ(self):
        self.playMusic(self.musicList[7], volume=0.5)

    def stopFFSZ(self):
        self.musicList[7].stop()

    def startFFActivity(self):
        self.playMusic(self.musicList[8])

    def stopFFActivity(self):
        self.musicList[8].stop()

    def startSSNbrhood(self):
        self.playMusic(self.musicList[9])

    def stopSSNbrhood(self):
        self.musicList[9].stop()

<<<<<<< HEAD
	def startSecretArea(self):
		self.playMusic(self.musicList[11])

	def stopSecretArea(self):
		self.musicList[11].stop()

=======
    def startSSSZ(self):
        self.playMusic(self.musicList[10], volume=0.5)
>>>>>>> origin/master

    def stopSSSZ(self):
        self.musicList[10].stop()
