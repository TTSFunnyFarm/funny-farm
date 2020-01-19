from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.quest import Quests
from direct.directnotify import DirectNotifyGlobal

from toontown.cutscenes.BuyGagsScene import BuyGagsScene
from toontown.cutscenes.DualTasksScene import DualTasksScene
from toontown.cutscenes.FirstBuildingScene import FirstBuildingScene
from toontown.cutscenes.FlippySuitIntroScene import FlippySuitIntroScene
from toontown.cutscenes.MeterAlertScene import MeterAlertScene
from toontown.cutscenes.MeterDisasterScene import MeterDisasterScene
from toontown.cutscenes.IntroScene import IntroScene

cutscenes = [
    BuyGagsScene,
    DualTasksScene,
    FirstBuildingScene,
    FlippySuitIntroScene,
    MeterAlertScene,
    MeterDisasterScene,
    IntroScene
]

class CutsceneManager(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('CutsceneManager')

    def __init__(self):
        self.track = None
        self.currScene = None
        self.cutscenes = {}
        self.initCutscenes()

    def initCutscenes(self):
        for cutscene in cutscenes:
            self.cutscenes[cutscene.id] = cutscene

    def enterCutscene(self, questId):
        currZone = base.cr.playGame.getActiveZone()
        # if currZone.place:
        #     if currZone.place.zoneId != Quests.getToNpcLocation(questId):
        #         return self.notify.warning('Failed to start cutscene %d, not in correct zone.' % questId)
        # else:
        #     if currZone.zoneId != Quests.getToNpcLocation(questId):
        #         return self.notify.warning('Failed to start cutscene %d, not in correct zone.' % questId)
        if self.track:
            self.track.finish()
            self.track = None
        self.currScene = self.getCutscene(questId)()
        self.currScene.enter()
        self.track = self.currScene.getTrack()
        if self.track:
            self.track.start()
            self.acceptOnce('cutscene-done', self.exitCutscene)

    def getCutscene(self, questId):
        return self.cutscenes.get(questId)

    def getCurrentScene(self):
        return self.currScene

    def exitCutscene(self):
        if not self.currScene:
            return
        self.track.finish()
        self.track = None
        self.currScene.exit()
        self.currScene.delete()
        self.currScene = None
