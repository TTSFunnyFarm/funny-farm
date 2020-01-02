from toontown.cutscenes.CutsceneBase import CutsceneBase
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class BuyGagsScene(CutsceneBase):
    id = 1007
    
    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        camTrack1 = Sequence()
        camTrack2 = Sequence()

        camTrack1.append(Func(base.localAvatar.acceptOnce, 'nextInfoPage', camTrack2.start))
        camTrack1.append(LerpPosHprInterval(camera, duration=3.0, pos=Point3(-25, 25, 9), hpr=Vec3(0, -2, 0), blendType='easeInOut'))

        camTrack2.append(Func(camTrack1.finish))
        camTrack2.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(30, 20, 9), hpr=Vec3(-15, -2, 0), blendType='easeInOut'))

        track = Sequence()
        track.append(Func(base.localAvatar.showInfoBubble, 1, 'cutscene-done'))
        track.append(Func(base.localAvatar.acceptOnce, 'nextInfoPage', camTrack1.start))
        # All info bubbles will be added to quest history so that they only happen once.
        track.append(Func(base.localAvatar.acceptOnce, 'cutscene-done', base.localAvatar.addQuestHistory, [1]))
        self.track = track

    def enter(self):
        CutsceneBase.enter(self)

    def exit(self):
        CutsceneBase.exit(self)
