from direct.showbase.DirectObject import DirectObject

from libotp import *
from otp.otpbase import OTPLocalizer
from toontown.discord.FFDiscordIntegration import FFDiscordIntegration
from toontown.distributed.PlayGame import PlayGame
from toontown.login.AvatarChooser import AvatarChooser
from toontown.makeatoon.MakeAToon import MakeAToon
from toontown.cutscenes.CutsceneManager import CutsceneManager
from toontown.quest.QuestManager import QuestManager
from toontown.book.CogPageMgr import CogPageMgr
from toontown.toonbase import FunnyFarmGlobals
from toontown.toontowngui import TTDialog


class FFClientRepository(DirectObject):
    notify = directNotify.newCategory('ClientRepository')
    notify.setInfo(True)
    AI_TIMEOUT = 30

    def __init__(self):
        DirectObject.__init__(self)
        if config.GetBool('want-discord-integration', 0):
            self.discordIntegration = FFDiscordIntegration(self)
        else:
            self.discordIntegration = None

        self.avChoice = None
        self.avCreate = None
        self.playGame = PlayGame()
        self.questManager = QuestManager()
        self.cogPageMgr = CogPageMgr()
        self.cutsceneMgr = CutsceneManager()
        self.playingGame = 0
        self.waitDialog = None

    def begin(self):
        if not base.air.isLoaded:
            base.transitions.fadeIn(1.0)
            # We usually won't get here, but just in case the AI is taking extra long, we'll have them wait.
            # In the future, as we build up our AI more and more, there's a better chance we'll get here.
            self.waitDialog = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.NoButtons,
                                                text=OTPLocalizer.AIPleaseWait)
            self.waitDialog.show()
            self.accept('ai-done', self.enterChooseAvatar, [True])
            taskMgr.doMethodLater(self.AI_TIMEOUT, self.aiTimeout, 'aiTimeout')
        else:
            self.enterChooseAvatar()

    def aiTimeout(self, task):
        # Even more unlikely that we'll get here, but better safe than sorry!
        self.ignore('ai-done')
        base.handleGameError('AI services either took too long or could not be started.')
        return task.done

    def enterChooseAvatar(self, fade=False):
        if self.waitDialog:
            self.waitDialog.destroy()
            self.waitDialog = None
            self.ignore('ai-done')
            taskMgr.remove('aiTimeout')
        if fade:
            base.transitions.fadeOut(1.0)
        else:
            base.transitions.fadeScreen(1.0)
        self.avChoice = AvatarChooser()
        self.avChoice.load()
        self.avChoice.enter()

    def exitChooseAvatar(self):
        base.transitions.noTransitions()
        self.avChoice.exit()
        self.avChoice = None

    def enterCreateAvatar(self, index):
        if self.avChoice:
            self.exitChooseAvatar()
        self.avCreate = MakeAToon('MakeAToon-done', index, 1)
        self.avCreate.load()
        self.avCreate.enter()

    def exitCreateAvatar(self, tutorialFlag=0):
        base.transitions.noTransitions()
        self.avCreate = None
        if tutorialFlag:
            self.playGame.enterTutorial()
            self.setupLocalAvatar(tutorialFlag=tutorialFlag)
            NametagGlobals.setMasterArrowsOn(1)
            self.playingGame = 1
        else:
            self.enterTheTooniverse(FunnyFarmGlobals.FunnyFarm)

    def setupLocalAvatar(self, tutorialFlag=0):
        base.localAvatar.reparentTo(render)
        base.localAvatar.generate()
        base.localAvatar.initInterface()
        if not tutorialFlag:
            base.localAvatar.book.showButton()
            base.localAvatar.laffMeter.start()
            base.localAvatar.experienceBar.show()
            base.localAvatar.startChat()
        # Enable the avatar for a moment so that it initializes the camera's position.
        # Otherwise the camera would just be staring at render while the teleportIn animation plays.
        base.localAvatar.enable()
        base.localAvatar.disable()

    def teleportTo(self, zoneId):
        base.localAvatar.enterTeleportOut(callback=self.__handleTeleport, extraArgs=[zoneId])

    def __handleTeleport(self, zoneId):
        base.localAvatar.exitTeleportOut()
        if self.playGame.hood and zoneId == self.playGame.hood.zoneId:
            if self.playGame.hood.place:
                # Teleporting to the playground from a local shop
                self.playGame.hood.exitPlace()
                base.transitions.irisIn()
                self.playGame.hood.enter()
            else:
                # Teleporting to the same playground you're currently in (via the map)
                base.transitions.irisIn()
                base.localAvatar.setRandomSpawn(zoneId)
                base.localAvatar.enterTeleportIn(callback=self.playGame.hood.handleEntered)
        else:
            self.playGame.exitActiveZone()
            self.playGame.enterHood(zoneId)

    def enterTheTooniverse(self, zoneId):
        base.transitions.noTransitions()
        self.playGame.enterHood(zoneId, init=1)
        self.setupLocalAvatar()
        NametagGlobals.setMasterArrowsOn(1)
        self.playingGame = 1

    def exitTheTooniverse(self):
        base.localAvatar.enterTeleportOut(callback=self.__handleExit)

    def __handleExit(self):
        self.cleanupGame()
        musicMgr.playPickAToon()
        self.enterChooseAvatar()

    def cleanupGame(self):
        if hasattr(self.playGame, 'hood') and self.playGame.hood:
            if hasattr(self.playGame.hood, 'unloaded') and self.playGame.hood.unloaded:
                self.playGame.hood = None
        self.playGame.exitActiveZone()

        camera.reparentTo(render)
        base.air.cheesyEffectMgr.stopTimer()
        # If we're in the tutorial, don't even bother cleaning up localAvatar; too many errors
        if base.localAvatar.tutorialAck:
            base.localAvatar.delete()
            base.localAvatar = None
        NametagGlobals.setMasterArrowsOn(0)
        self.playingGame = 0

    def shutdown(self, errorCode=None):
        if self.playingGame:
            self.cleanupGame()
        self.notify.info('Exiting cleanly')
        base.exitShow(errorCode)

    def isPaid(self):
        return True
