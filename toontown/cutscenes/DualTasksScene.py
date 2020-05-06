from toontown.cutscenes.CutsceneBase import CutsceneBase
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class DualTasksScene(CutsceneBase):
    id = 1014
    
    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        self.toonHq = None
        camTrack = Sequence()
        camTrack.append(Func(base.localAvatar.questPage.hideQuestsOnscreen))
        camTrack.append(LerpPosHprInterval(camera, duration=3.0, pos=Point3(-27, -10, 8), hpr=Vec3(-45, 0, 0), blendType='easeInOut'))

        track = Sequence()
        track.append(Func(base.localAvatar.questPage.showQuestsOnscreen))
        track.append(Func(base.localAvatar.showInfoBubble, 4, 'cutscene-done'))
        track.append(Func(base.localAvatar.acceptOnce, 'nextInfoPage', base.localAvatar.acceptOnce, ['nextInfoPage', camTrack.start]))
        self.track = track

    def delete(self):
        CutsceneBase.delete(self)
        del self.toonHq

    def enter(self):
        CutsceneBase.enter(self)
        for building in base.cr.playGame.getActiveZone().buildings:
            if 'toon_landmark_hq' in building.getBuildingNodePath().getName():
                self.toonHq = building
        if not self.toonHq.getQuestOffer():
            self.toonHq.setQuestOffer(4, hq=1)

    def exit(self):
        CutsceneBase.exit(self)
        if self.toonHq.getQuestOffer() == 4:
            self.toonHq.clearQuestOffer()
        base.localAvatar.addQuestHistory(4)
