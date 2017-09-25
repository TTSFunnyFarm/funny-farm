from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer

def getCutscene(questId):
    if questId == 1001:
        return scene1001()

def scene1001():
    track = Sequence()
    track.append(Func(camera.wrtReparentTo, render))
    track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(20, -20, 7), hpr=Vec3(22.5, -10, 0), blendType='easeInOut'))
    track.append(Func(base.localAvatar.showInfoBubble, 1001, 'cutscene-done'))
    base.localAvatar.removeQuest(1001)
    base.localAvatar.addQuest(1002)
    return track
