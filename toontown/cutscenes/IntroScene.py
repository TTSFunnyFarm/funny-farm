from toontown.cutscenes.CutsceneBase import CutsceneBase
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class IntroScene(CutsceneBase):
    id = 1001
    
    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        track = Sequence()
        track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(20, -20, 7), hpr=Vec3(22.5, -10, 0), blendType='easeInOut'))
        track.append(Func(base.localAvatar.showInfoBubble, 1001, 'cutscene-done'))
        self.track = track

    def enter(self):
        CutsceneBase.enter(self)

    def exit(self):
        CutsceneBase.exit(self)
        base.localAvatar.removeQuest(1001)
        base.localAvatar.addQuest(1002)
