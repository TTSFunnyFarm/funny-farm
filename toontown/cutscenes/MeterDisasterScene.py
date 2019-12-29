from toontown.cutscenes.CutsceneBase import CutsceneBase
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class MeterDisasterScene(CutsceneBase):
    id = 1004
    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        self.actors = {'flippy': base.cr.playGame.hood.place.flippy,
            'dimm': base.cr.playGame.hood.place.npcs[0],
            'surlee': base.cr.playGame.hood.place.npcs[1],
            'prepostera': base.cr.playGame.hood.place.npcs[2]}
        flippy = self.actors['flippy']
        track = Sequence()
        track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(8, 8, flippy.getHeight() - 0.5), hpr=Vec3(120, 0, 0), other=flippy, blendType='easeInOut'))
        track.append(Func(self.doDialog, 0, 0))
        self.track = track

    def enter(self):
        CutsceneBase.enter(self)
        aspect2d.hide()

    def exit(self):
        CutsceneBase.exit(self)

    def sillyMeterScene(self, elapsedTime):
        flippy = self.actors['flippy']
        smtrack = Sequence()
        smtrack.append(Func(base.transitions.fadeOut, 1.0))
        smtrack.append(Wait(1.0))
        smtrack.append(Func(camera.setPosHpr, 18, -29, 14, 30, -5, 0))
        smtrack.append(Func(base.transitions.fadeIn, 1.0))
        smtrack.append(Wait(1.0))
        smtrack.append(Func(messenger.send, 'SillyMeterPhase', ['4To5']))
        smtrack.append(Wait(7.0))
        smtrack.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(12, 10, 5), hpr=Vec3(120, -5, 0), other=flippy, blendType='easeInOut'))
        smtrack.append(Func(flippy.setLocalPageChat, self.dialog[1], 1))
        smtrack.append(Func(flippy.acceptOnce, flippy.uniqueName('doneChatPage'), self.sceneFinish))
        smtrack.append(Func(aspect2d.show))
        smtrack.start()

    def sceneFinish(self, elapsedTime):
        base.localAvatar.removeQuest(1004)
        base.localAvatar.addQuestHistory(1004)
        base.localAvatar.addQuest(1005)
        mtrack = Sequence()
        mtrack.append(Func(base.transitions.fadeOut, 1.0))
        mtrack.append(Wait(1.0))
        mtrack.append(Func(base.cr.playGame.hood.place.unloadQuestChanges))
        mtrack.append(Func(messenger.send, 'cutscene-done'))
        mtrack.append(Func(base.transitions.fadeIn, 1.0))
        mtrack.start()

    def doDialog(self, index, elapsedTime):
        dialog = self.dialog[0][index]
        dimm = self.actors['dimm']
        flippy = self.actors['flippy']
        surlee = self.actors['surlee']
        prepostera = self.actors['prepostera']
        if index == 0:
            flippy.setLocalPageChat(dialog, None)
            flippy.acceptOnce(flippy.uniqueName('doneChatPage'), self.doDialog, [index + 1])
        elif index == 1:
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=2.0, pos=Point3(-10, 10, 4), hpr=Vec3(-135, 0, 0), other=dimm, blendType='easeInOut'))
            mtrack.append(Func(dimm.setLocalPageChat, dialog, None))
            mtrack.append(Func(dimm.acceptOnce, dimm.uniqueName('doneChatPage'), self.doDialog, [index + 1]))
            mtrack.start()
        elif index == 2:
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=1.0, pos=Point3(10, 10, 4), hpr=Vec3(135, 0, 0), other=surlee, blendType='easeInOut'))
            mtrack.append(Func(surlee.setLocalPageChat, dialog, None))
            mtrack.append(Func(surlee.acceptOnce, surlee.uniqueName('doneChatPage'), self.doDialog, [index + 1]))
            mtrack.start()
        elif index == 3:
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=1.0, pos=Point3(0, 10, 4), hpr=Vec3(180, 0, 0), other=prepostera, blendType='easeInOut'))
            mtrack.append(Func(prepostera.setLocalPageChat, dialog, None))
            mtrack.append(Func(prepostera.acceptOnce, prepostera.uniqueName('doneChatPage'), self.sillyMeterScene))
            mtrack.start()
