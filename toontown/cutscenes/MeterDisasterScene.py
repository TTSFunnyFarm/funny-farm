from toontown.cutscenes.CutsceneBase import CutsceneBase
from toontown.cutscenes import CutsceneUtil
from toontown.cutscenes.CutscenesGlobals import *
from toontown.quest import Quests
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
        self.track = Sequence()

    def enter(self):
        CutsceneBase.enter(self)
        base.hideUi()
        flippy = self.actors['flippy']
        flippy.initializeBodyCollisions('toon')
        self.track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(8, 8, flippy.getHeight() - 0.5), hpr=Vec3(120, 0, 0), other=flippy, blendType='easeInOut'))
        self.track.append(Func(self.doDialog, 0, 0))

    def exit(self):
        CutsceneBase.exit(self)

    def sillyMeterScene(self, elapsedTime):
        flippy = self.actors['flippy']
        track = Sequence()
        track.append(Func(base.transitions.fadeOut, 1.0))
        track.append(Wait(1.0))
        track.append(Func(camera.setPosHpr, 18, -29, 14, 30, -5, 0))
        track.append(Func(base.transitions.fadeIn, 1.0))
        track.append(Wait(1.0))
        track.append(Func(messenger.send, 'SillyMeterPhase', ['4To5']))
        track.append(Wait(7.0))
        track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(12, 10, 5), hpr=Vec3(120, -5, 0), other=flippy, blendType='easeInOut'))
        track.append(Func(self.doDialog, len(self.dialog) - 1, 0))
        track.append(Func(base.showUI))
        track.start()

    def byeFlippy(self):
        if self.actors.get('flippy'):
            actor = self.actors['flippy']
            actor.removeActive()
            actor.delete()
            del actor

    def sceneFinish(self, elapsedTime):
        base.localAvatar.removeQuest(1004)
        base.localAvatar.addQuestHistory(1004)
        base.localAvatar.addQuest(1005)
        track = Sequence()
        track.append(Func(base.transitions.fadeOut, 1.0))
        track.append(Wait(1.0))
        track.append(Func(self.byeFlippy))
        track.append(Func(messenger.send, 'cutscene-done'))
        track.append(Func(base.transitions.fadeIn, 1.0))
        track.start()

    def doDialog(self, index, elapsedTime):
        dialog = self.dialog[index]
        extra = CutsceneUtil.GetExtra(dialog)
        if extra:
            dialog = dialog[0]
        flippy = self.actors['flippy']
        dimm = self.actors['dimm']
        surlee = self.actors['surlee']
        prepostera = self.actors['prepostera']
        actor = None
        if index == 0:
            actor = flippy
            actor.setLocalPageChat(dialog, None)
            actor.acceptOnce(actor.uniqueName('doneChatPage'), self.doDialog, [index + 1])
        elif index == 1:
            actor = dimm
            track = Sequence()
            track.append(LerpPosHprInterval(camera, duration=2.0, pos=Point3(-10, 10, 4), hpr=Vec3(-135, 0, 0), other=actor, blendType='easeInOut'))
            track.append(Func(actor.setLocalPageChat, dialog, None))
            track.append(Func(actor.acceptOnce, actor.uniqueName('doneChatPage'), self.doDialog, [index + 1]))
            track.start()
        elif index == 2:
            actor = surlee
            track = Sequence()
            track.append(LerpPosHprInterval(camera, duration=1.0, pos=Point3(10, 10, 4), hpr=Vec3(135, 0, 0), other=actor, blendType='easeInOut'))
            track.append(Func(actor.setLocalPageChat, dialog, None))
            track.append(Func(actor.acceptOnce, actor.uniqueName('doneChatPage'), self.doDialog, [index + 1]))
            track.start()
        elif index == 3:
            actor = prepostera
            track = Sequence()
            track.append(LerpPosHprInterval(camera, duration=1.0, pos=Point3(0, 10, 4), hpr=Vec3(180, 0, 0), other=actor, blendType='easeInOut'))
            track.append(Func(actor.setLocalPageChat, dialog, None))
            track.append(Func(actor.acceptOnce, actor.uniqueName('doneChatPage'), self.sillyMeterScene))
            track.start()
        elif index == len(self.dialog) - 1:
            actor = flippy
            dialog = Quests.fillInQuestNames(dialog, avName=base.avatarData.setName)
            actor.setLocalPageChat(dialog, 1)
            actor.acceptOnce(actor.uniqueName('doneChatPage'), self.sceneFinish)
        if extra:
            self.doAnimate(actor, *extra)
