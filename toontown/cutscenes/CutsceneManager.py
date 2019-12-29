from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.cutscenes import *
cutscenes = [BuyGagsScene.BuyGagsScene, DualTasksScene.DualTasksScene, FirstBuildingScene.FirstBuildingScene, FlippySuitIntroScene.FlippySuitIntroScene, MeterAlertScene.MeterAlertScene, MeterDisasterScene.MeterDisasterScene, IntroScene.IntroScene]
from toontown.quest import Quests

class CutsceneManager(DirectObject):
    notify = directNotify.newCategory('CutsceneManager')

    def initCutscenes(self):
        for cutscene in cutscenes:
            self.cutscenes[cutscene.id] = cutscene

    def __init__(self):
        self.track = None
        self.currScene = None
        self.cutscenes = {}
        self.initCutscenes()

    def enterCutscene(self, questId):
        currZone = base.cr.playGame.getActiveZone()
        # if currZone.place:
        #     if currZone.place.zoneId != Quests.getToNpcLocation(questId):
        #         return self.notify.warning('Failed to start cutscene %d, not in correct zone.' % questId)
        # else:
        #     if currZone.zoneId != Quests.getToNpcLocation(questId):
        #         return self.notify.warning('Failed to start cutscene %d, not in correct zone.' % questId)
        self.currScene = self.getCutscene(questId)()
        if self.track:
            self.track.finish()
            self.track = None
        self.track = self.currScene.getTrack()
        if self.track:
            self.track.start()
            self.acceptOnce('cutscene-done', self.exitCutscene)
        self.currScene.enter()

    def getCutscene(self, questId):
        print(questId)
        print(self.cutscenes)
        return self.cutscenes.get(questId)

    def getCurrentScene():
        return self.currScene

    def exitCutscene(self):
        if not self.currScene:
            return
        self.currScene.exit()
        self.currScene = None
        self.track.finish()
        self.track = None
