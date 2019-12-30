from toontown.cutscenes.CutsceneBase import CutsceneBase
from toontown.cutscenes.CutscenesGlobals import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class MeterDisasterScene(CutsceneBase):
    id = 1004
    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        self.actors = {'flippy': [TOON, [-12, -25, 0, 330, 0, 0], 1001, base.cr.playGame.hood.place.interior],
            'dimm': base.cr.playGame.hood.place.npcs[0],
            'surlee': base.cr.playGame.hood.place.npcs[1],
            'prepostera': base.cr.playGame.hood.place.npcs[2]}
        self.track = Sequence()

    def enter(self):
        CutsceneBase.enter(self)
        aspect2d.hide()
        flippy = self.actors['flippy']
        flippy.initializeBodyCollisions('toon')
        self.track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(8, 8, flippy.getHeight() - 0.5), hpr=Vec3(120, 0, 0), other=flippy, blendType='easeInOut'))
        self.track.append(Func(self.doDialog, 0, 0))

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
        smtrack.append(Func(flippy.setLocalPageChat, self.dialog[len(self.dialog) - 1], 1))
        smtrack.append(Func(flippy.acceptOnce, flippy.uniqueName('doneChatPage'), self.sceneFinish))
        smtrack.append(Func(aspect2d.show))
        smtrack.start()

    def byeFlippy(self):
        if self.actors.get('flippy'):
            actor = self.actors['flippy']
            actor.delete()
            del actor

    def sceneFinish(self, elapsedTime):
        base.localAvatar.removeQuest(1004)
        base.localAvatar.addQuestHistory(1004)
        base.localAvatar.addQuest(1005)
        mtrack = Sequence()
        mtrack.append(Func(base.transitions.fadeOut, 1.0))
        mtrack.append(Wait(1.0))
        mtrack.append(Func(self.byeFlippy))
        mtrack.append(Func(messenger.send, 'cutscene-done'))
        mtrack.append(Func(base.transitions.fadeIn, 1.0))
        mtrack.start()

    def doDialog(self, index, elapsedTime):
        extra = None
        dialog = self.dialog[index]
        print(dialog)
        print(type(dialog))
        if isinstance(dialog, list):
            extra = dialog[1:]
            dialog = dialog[0]
        dimm = self.actors['dimm']
        flippy = self.actors['flippy']
        surlee = self.actors['surlee']
        prepostera = self.actors['prepostera']
        actor = None
        if index == 0:
            actor = flippy
            actor.setLocalPageChat(dialog, None)
            actor.acceptOnce(actor.uniqueName('doneChatPage'), self.doDialog, [index + 1])
        elif index == 1:
            actor = dimm
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=2.0, pos=Point3(-10, 10, 4), hpr=Vec3(-135, 0, 0), other=actor, blendType='easeInOut'))
            mtrack.append(Func(actor.setLocalPageChat, dialog, None))
            mtrack.append(Func(actor.acceptOnce, actor.uniqueName('doneChatPage'), self.doDialog, [index + 1]))
            mtrack.start()
        elif index == 2:
            actor = surlee
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=1.0, pos=Point3(10, 10, 4), hpr=Vec3(135, 0, 0), other=actor, blendType='easeInOut'))
            mtrack.append(Func(actor.setLocalPageChat, dialog, None))
            mtrack.append(Func(actor.acceptOnce, actor.uniqueName('doneChatPage'), self.doDialog, [index + 1]))
            mtrack.start()
        elif index == 3:
            actor = prepostera
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=1.0, pos=Point3(0, 10, 4), hpr=Vec3(180, 0, 0), other=actor, blendType='easeInOut'))
            mtrack.append(Func(actor.setLocalPageChat, dialog, None))
            mtrack.append(Func(actor.acceptOnce, actor.uniqueName('doneChatPage'), self.sillyMeterScene))
            mtrack.start()
        if extra:
            self.doAnimate(actor, *extra)
