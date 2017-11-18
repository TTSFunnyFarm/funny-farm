from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
import Cutscenes
import Quests

class CutsceneManager(DirectObject):
    notify = directNotify.newCategory('CutsceneManager')

    def __init__(self):
        self.track = None
        self.currQuest = None

    def enterCutscene(self, questId):
        currZone = base.cr.playGame.getActiveZone()
        # if currZone.place:
        #     if currZone.place.zoneId != Quests.getToNpcLocation(questId):
        #         return self.notify.warning('Failed to start cutscene %d, not in correct zone.' % questId)
        # else:
        #     if currZone.zoneId != Quests.getToNpcLocation(questId):
        #         return self.notify.warning('Failed to start cutscene %d, not in correct zone.' % questId)
        self.currQuest = questId
        base.localAvatar.disable()
        base.localAvatar.setAnimState('neutral')
        if self.track:
            self.track.pause()
            self.track = None
        self.track = Cutscenes.getCutscene(questId)
        if self.track:
            self.track.start()
            self.acceptOnce('cutscene-done', self.exitCutscene)

    def exitCutscene(self):
        base.localAvatar.enable()
        self.track.pause()
        self.track = None
