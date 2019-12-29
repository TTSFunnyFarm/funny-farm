from toontown.cutscenes.CutsceneBase import CutsceneBase
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class FirstBuildingScene(CutsceneBase):
    id = 1028
    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        self.interior = base.cr.playGame.street.place.interior
        self.street = base.cr.playGame.street.geom
        self.sky = base.cr.playGame.street.sky

        track = Sequence()
        track.append(Func(base.transitions.fadeOut, 1.0))
        track.append(Wait(1.0))
        track.append(Func(loadStreet))
        track.append(Wait(1.0))
        track.append(Func(messenger.send, 'spawnBuilding-1100', [18]))
        track.append(Wait(10.0))
        track.append(Func(base.transitions.fadeOut, 1.0))
        track.append(Wait(1.0))
        track.append(Func(loadInterior))
        track.append(Wait(1.0))
        track.append(Func(base.localAvatar.showInfoBubble, 1028, 'cutscene-done', 1001))
        track.append(Func(base.localAvatar.addQuestHistory, 1028))
        self.track = track

    def loadStreet():
        interior.reparentTo(hidden)
        interior.stash()
        street.unstash()
        street.reparentTo(render)
        sky.unstash()
        sky.reparentTo(render)
        base.cr.playGame.street.setupLandmarkBuildings()
        aspect2d.hide()
        camera.setPosHpr(55, 163, 12, 39, 0, 0)
        base.transitions.fadeIn(1.0)

    def loadInterior():
        street.reparentTo(hidden)
        street.stash()
        sky.reparentTo(hidden)
        sky.stash()
        base.cr.playGame.street.destroyLandmarkBuildings()
        interior.unstash()
        interior.reparentTo(render)
        aspect2d.show()
        base.localAvatar.disable()
        base.localAvatar.setAnimState('neutral')
        base.transitions.fadeIn(1.0)

    def enter(self):
        CutsceneBase.enter(self)

    def exit(self):
        CutsceneBase.exit(self)
