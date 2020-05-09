from toontown.cutscenes.CutsceneBase import CutsceneBase
from toontown.cutscenes import CutsceneUtil
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class FlippySuitIntroScene(CutsceneBase):
    id = 1002

    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        self.bgm = base.loader.loadMusic('phase_12/audio/bgm/Bossbot_Entry_v1.ogg')
        self.actors = base.cr.playGame.hood.actors
        if not self.actors.get('suit') or not self.actors.get('flippy'): # this really should not happen
            base.cr.playGame.hood.loadQuestChanges()
        track = Sequence()
        track.append(LerpPosHprInterval(camera, duration=3.0, pos=Point3(-47, -40, 9), hpr=Vec3(30, -10, 0), blendType='easeInOut'))
        track.append(Func(self.doDialog, 0, 0))
        self.track = track

    def enter(self):
        CutsceneBase.enter(self)
        base.hideUi()
        taskMgr.remove('FF-birds')

    def exit(self):
        CutsceneBase.exit(self)
        base.localAvatar.enable()
        base.showUI()
        CutsceneUtil.UnfadeScreen()
        if not base.air.holidayMgr.isHalloween() and not base.air.holidayMgr.isWinter():
            base.cr.playGame.hood.endSpookySky()
        base.cr.cutsceneMgr.ignore('cutscene-done')

    def questDone(self):
        flippy = self.actors['flippy']
        flippy.setAllowedToTalk(0)
        flippy.enterTeleportOut(callback=base.cr.playGame.hood.unloadQuestChanges)
        self.delete()

    def sceneFinish(self, elapsedTime):
        suit = self.actors['suit']
        flippy = self.actors['flippy']
        track = Sequence()
        track.append(suit.beginSupaFlyMove(suit.getPos(), 0, 'toSky'))
        track.append(Func(base.transitions.fadeOut, 1.0))
        track.append(Wait(1.0))
        track.append(Func(suit.removeActive))
        track.append(Func(flippy.setHpr, 195, 0, 0))
        track.append(Func(flippy.setMainQuest, 1002))
        track.append(Func(self.exit))
        track.append(Func(base.transitions.fadeIn, 1.0))
        track.append(Wait(1.0))
        track.append(Func(flippy.acceptOnce, 'cutscene-done', self.questDone))
        track.append(Func(taskMgr.doMethodLater, 1, base.cr.playGame.hood.doBirds, 'FF-birds'))
        track.start()

    def doDialog(self, index, elapsedTime):
        dialog = self.dialog[index]
        extra = CutsceneUtil.GetExtra(dialog)
        if extra:
            dialog = dialog[0]
        suit = self.actors['suit']
        flippy = self.actors['flippy']
        actor = None
        if index >= (len(self.dialog) - 1):
            actor = suit
            suit.setLocalPageChat(dialog, 1)
            suit.acceptOnce(suit.uniqueName('doneChatPage'), self.sceneFinish)
        elif (index % 2) == 0:
            actor = suit
            suit.setLocalPageChat(dialog, None)
            suit.acceptOnce(suit.uniqueName('doneChatPage'), self.doDialog, [index + 1])
        else:
            actor = flippy
            flippy.setLocalPageChat(dialog, None)
            flippy.acceptOnce(flippy.uniqueName('doneChatPage'), self.doDialog, [index + 1])
        if extra:
            self.doAnimate(actor, *extra)
