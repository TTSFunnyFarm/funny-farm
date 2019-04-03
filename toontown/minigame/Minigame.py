from panda3d.core import *
from direct.gui.DirectGui import *
from direct.distributed.ClockDelta import *
from toontown.toonbase import ToontownGlobals
from direct.showbase.DirectObject import DirectObject
from direct.fsm import ClassicFSM, State
from toontown.minigame import MinigameRulesPanel
from toontown.toon import Toon
from direct.showbase import RandomNumGen
from toontown.toonbase import TTLocalizer
import random
from toontown.minigame import MinigameGlobals
from direct.showbase import PythonUtil
from toontown.toon import TTEmote
from otp.avatar import Emote
from toontown.book.PurchaseManagerConstants import *

class Minigame(DirectObject):
    notify = directNotify.newCategory('Minigame')

    def __init__(self):
        self.waitingStartLabel = DirectLabel(text=TTLocalizer.MinigameWaitingForOtherPlayers, text_fg=VBase4(1, 1, 1, 1), relief=None, pos=(-0.6, 0, -0.75), scale=0.075)
        self.waitingStartLabel.hide()
        self.localAvId = base.localAvatar.doId
        self.avIdList = [self.localAvId]
        self.remoteAvIdList = []
        self.frameworkFSM = ClassicFSM.ClassicFSM('Minigame', [State.State('frameworkInit', self.enterFrameworkInit, self.exitFrameworkInit, ['frameworkRules', 'frameworkCleanup', 'frameworkAvatarExited']),
         State.State('frameworkRules', self.enterFrameworkRules, self.exitFrameworkRules, ['frameworkWaitServerStart', 'frameworkCleanup', 'frameworkAvatarExited']),
         State.State('frameworkWaitServerStart', self.enterFrameworkWaitServerStart, self.exitFrameworkWaitServerStart, ['frameworkGame', 'frameworkCleanup', 'frameworkAvatarExited']),
         State.State('frameworkGame', self.enterFrameworkGame, self.exitFrameworkGame, ['frameworkWaitServerFinish', 'frameworkCleanup', 'frameworkAvatarExited']),
         State.State('frameworkWaitServerFinish', self.enterFrameworkWaitServerFinish, self.exitFrameworkWaitServerFinish, ['frameworkCleanup']),
         State.State('frameworkAvatarExited', self.enterFrameworkAvatarExited, self.exitFrameworkAvatarExited, ['frameworkCleanup']),
         State.State('frameworkCleanup', self.enterFrameworkCleanup, self.exitFrameworkCleanup, [])], 'frameworkInit', 'frameworkCleanup')
        self.rulesDoneEvent = 'rulesDone'
        base.curMinigame = self
        self.numPlayers = 1
        self.hasLocalToon = True
        self.modelCount = 500
        self.cleanupActions = []
        self.usesSmoothing = 0
        self.usesLookAround = 0
        self.difficultyOverride = None
        self.trolleyZoneOverride = None
        self.frameworkFSM.enterInitialState()
        self.startingVotes = {}
        self.metagameRound = -1
        self._telemLimiter = None
        self.doId = id(self)
        return

    def addChildGameFSM(self, gameFSM):
        self.frameworkFSM.getStateNamed('frameworkGame').addChild(gameFSM)

    def removeChildGameFSM(self, gameFSM):
        self.frameworkFSM.getStateNamed('frameworkGame').removeChild(gameFSM)

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, str(self.doId)))

    def isSinglePlayer(self):
        return True

    def setUsesSmoothing(self):
        self.usesSmoothing = 1

    def setUsesLookAround(self):
        self.usesLookAround = 1

    def getTitle(self):
        return TTLocalizer.DefaultMinigameTitle

    def getInstructions(self):
        return TTLocalizer.DefaultMinigameInstructions

    def getMaxDuration(self):
        raise Exception('Minigame implementer: you must override getMaxDuration()')

    def __createRandomNumGen(self):
        self.notify.debug('BASE: self.doId=0x%08X' % self.doId)
        self.randomNumGen = RandomNumGen.RandomNumGen(self.doId)

        def destroy(self = self):
            self.notify.debug('BASE: destroying random num gen')
            del self.randomNumGen

        self.cleanupActions.append(destroy)

    def generate(self):
        self.notify.debug('BASE: generate, %s' % self.getTitle())
        self.__createRandomNumGen()

    def announceGenerate(self):
        self.normalExit = 1
        count = self.modelCount
        loader.beginBulkLoad('minigame', TTLocalizer.HeadingToMinigameTitle % self.getTitle(), count, TTLocalizer.TIP_MINIGAME)
        self.load()
        loader.endBulkLoad('minigame')
        globalClock.syncFrameTime()
        self.onstage()

        def cleanup(self = self):
            self.notify.debug('BASE: cleanup: normalExit=%s' % self.normalExit)
            self.offstage()

        self.cleanupActions.append(cleanup)
        self.frameworkFSM.request('frameworkRules')

    def disable(self):
        self.notify.debug('BASE: disable')
        if self._telemLimiter:
            self._telemLimiter.destroy()
            self._telemLimiter = None
        self.frameworkFSM.request('frameworkCleanup')
        return

    def delete(self):
        self.notify.debug('BASE: delete')
        self.unload()
        self.ignoreAll()
        self.waitingStartLabel.destroy()
        del self.waitingStartLabel
        del self.frameworkFSM

    def load(self):
        self.notify.debug('BASE: load')
        Toon.loadMinigameAnims()

    def onstage(self):
        self.notify.debug('BASE: onstage')
        self.setGameReady()

    def offstage(self):
        self.notify.debug('BASE: offstage')
        messenger.send('minigameOffstage')

    def unload(self):
        self.notify.debug('BASE: unload')
        if hasattr(base, 'curMinigame'):
            del base.curMinigame
        Toon.unloadMinigameAnims()

    def setTrolleyZone(self, trolleyZone):
        self.notify.debug('BASE: setTrolleyZone: %s' % trolleyZone)
        self.trolleyZone = trolleyZone

    def setDifficultyOverrides(self, difficultyOverride, trolleyZoneOverride):
        if difficultyOverride != MinigameGlobals.NoDifficultyOverride:
            self.difficultyOverride = difficultyOverride / float(MinigameGlobals.DifficultyOverrideMult)
        if trolleyZoneOverride != MinigameGlobals.NoTrolleyZoneOverride:
            self.trolleyZoneOverride = trolleyZoneOverride

    def setGameReady(self):
        self.notify.debug('BASE: setGameReady: Ready for game with avatars: %s' % self.avIdList)
        self.__serverFinished = 0

        def cleanupAvatars(self = self):
            base.localAvatar.startLookAround()

        self.cleanupActions.append(cleanupAvatars)
        self.numJellybeans = 0
        return 0

    def setGameStart(self, timestamp):
        self.notify.debug('BASE: setGameStart: Starting game')
        self.gameStartTime = globalClockDelta.networkToLocalTime(timestamp)
        self.frameworkFSM.request('frameworkGame')

    def setGameAbort(self):
        self.notify.warning('BASE: setGameAbort: Aborting game')
        self.normalExit = 0
        self.frameworkFSM.request('frameworkCleanup')

    def gameOver(self):
        self.notify.debug('BASE: gameOver')
        self.frameworkFSM.request('frameworkWaitServerFinish')

    def getAvatar(self):
        return base.localAvatar

    def getAvatarName(self):
        return base.localAvatar.getName()

    def enterFrameworkInit(self):
        self.notify.debug('BASE: enterFrameworkInit')
        self.setEmotes()
        self.cleanupActions.append(self.unsetEmotes)

    def exitFrameworkInit(self):
        pass

    def enterFrameworkRules(self):
        self.notify.debug('BASE: enterFrameworkRules')
        self.accept(self.rulesDoneEvent, self.handleRulesDone)
        self.rulesPanel = MinigameRulesPanel.MinigameRulesPanel('MinigameRulesPanel', self.getTitle(), self.getInstructions(), self.rulesDoneEvent)
        self.rulesPanel.load()
        self.rulesPanel.enter()

    def exitFrameworkRules(self):
        self.ignore(self.rulesDoneEvent)
        self.rulesPanel.exit()
        self.rulesPanel.unload()
        del self.rulesPanel

    def handleRulesDone(self):
        self.notify.debug('BASE: handleRulesDone')
        self.frameworkFSM.request('frameworkWaitServerStart')

    def enterFrameworkWaitServerStart(self):
        self.notify.debug('BASE: enterFrameworkWaitServerStart')
        self.waitingStartLabel['text'] = TTLocalizer.MinigamePleaseWait
        self.waitingStartLabel.show()
        self.setGameStart(globalClockDelta.getFrameNetworkTime())

    def exitFrameworkWaitServerStart(self):
        self.waitingStartLabel.hide()

    def enterFrameworkGame(self):
        self.notify.debug('BASE: enterFrameworkGame')

    def exitFrameworkGame(self):
        pass

    def enterFrameworkWaitServerFinish(self):
        self.notify.debug('BASE: enterFrameworkWaitServerFinish')
        self.frameworkFSM.request('frameworkCleanup')

    def setGameExit(self):
        self.notify.debug('BASE: setGameExit -- it is now safe to exit the game.')
        if self.frameworkFSM.getCurrentState().getName() != 'frameworkWaitServerFinish':
            self.__serverFinished = 1
        else:
            self.notify.debug("Must wait for server to exit game: ask the framework to cleanup.")
            self.frameworkFSM.request('frameworkCleanup')

    def exitFrameworkWaitServerFinish(self):
        pass

    def enterFrameworkAvatarExited(self):
        self.notify.debug('BASE: enterFrameworkAvatarExited')

    def exitFrameworkAvatarExited(self):
        pass

    def enterFrameworkCleanup(self):
        self.notify.debug('BASE: enterFrameworkCleanup')
        for action in self.cleanupActions:
            action()

        self.cleanupActions = []
        self.ignoreAll()
        toon = base.localAvatar
        pointsArray = [int(round(self.numJellybeans))]
        if pointsArray[0] <= 0:
            pointsArray = [1]
        playerMoney = [toon.getMoney()]
        ids = [toon.doId]
        states = [PURCHASE_WAITING_STATE]
        remain = PURCHASE_COUNTDOWN_TIME
        base.cr.playGame.exitMinigame()
        base.cr.playGame.enterMinigamePurchase(toon, pointsArray, playerMoney, ids, states, remain, 'purchaseDone')

    def exitFrameworkCleanup(self):
        pass

    def local2GameTime(self, timestamp):
        return timestamp - self.gameStartTime

    def game2LocalTime(self, timestamp):
        return timestamp + self.gameStartTime

    def getCurrentGameTime(self):
        return self.local2GameTime(globalClock.getFrameTime())

    def getDifficulty(self):
        return MinigameGlobals.getDifficulty(self.getSafezoneId())

    def getSafezoneId(self):
        return base.cr.playGame.hood.TTZoneId

    def setEmotes(self):
        Emote.globalEmote.disableAll(base.localAvatar)

    def unsetEmotes(self):
        Emote.globalEmote.releaseAll(base.localAvatar)

    def setStartingVotes(self, startingVotesArray):
        if not len(startingVotesArray) == len(self.avIdList):
            self.notify.error('length does not match, startingVotes=%s, avIdList=%s' % (startingVotesArray, self.avIdList))
            return
        for index in range(len(self.avIdList)):
            avId = self.avIdList[index]
            self.startingVotes[avId] = startingVotesArray[index]

        self.notify.debug('starting votes = %s' % self.startingVotes)

    def setMetagameRound(self, metagameRound):
        self.metagameRound = metagameRound
