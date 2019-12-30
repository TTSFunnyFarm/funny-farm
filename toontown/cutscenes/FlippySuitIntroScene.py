from toontown.cutscenes.CutsceneBase import CutsceneBase
from toontown.cutscenes import CutsceneUtil
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class FlippySuitIntroScene(CutsceneBase):
    id = 1002
    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        self.bgm = base.loader.loadMusic('phase_12/audio/bgm/Bossbot_Entry_v1.ogg')
        self.suit = base.cr.playGame.hood.actors['suit']
        self.flippy = base.cr.playGame.hood.actors['flippy']
        track = Sequence()
        track.append(LerpPosHprInterval(camera, duration=3.0, pos=Point3(-47, -40, 9), hpr=Vec3(30, -10, 0), blendType='easeInOut'))
        track.append(Func(self.doDialog, 0, 0))
        self.track = track

    def enter(self):
        CutsceneBase.enter(self)
        aspect2d.hide()
        taskMgr.remove('FF-birds')
        CutsceneUtil.FadeScreen(0.25)
        if not base.air.holidayMgr.isHalloween() and not base.air.holidayMgr.isWinter():
            base.cr.playGame.hood.startSpookySky()

    def exit(self):
        CutsceneBase.exit(self)
        aspect2d.show()
        CutsceneUtil.UnfadeScreen()
        if not base.air.holidayMgr.isHalloween() and not base.air.holidayMgr.isWinter():
            base.cr.playGame.hood.endSpookySky()

    def questDone(self):
        self.flippy.setAllowedToTalk(0)
        self.flippy.enterTeleportOut(callback=base.cr.playGame.hood.unloadQuestChanges)

    def sceneFinish(self, elapsedTime):
        mtrack = Sequence()
        mtrack.append(self.suit.beginSupaFlyMove(self.suit.getPos(), 0, 'toSky'))
        mtrack.append(Func(base.transitions.fadeOut, 1.0))
        mtrack.append(Wait(1.0))
        mtrack.append(Func(base.localAvatar.enable))
        mtrack.append(Func(self.suit.removeActive))
        mtrack.append(Func(self.flippy.setHpr, 195, 0, 0))
        mtrack.append(Func(self.flippy.setMainQuest, 1002))
        mtrack.append(Func(base.transitions.fadeIn, 1.0))
        mtrack.append(Wait(1.0))
        mtrack.append(Func(self.exit))
        mtrack.append(Func(self.flippy.acceptOnce, 'cutscene-done', self.questDone))
        mtrack.append(Func(taskMgr.doMethodLater, 1, base.cr.playGame.hood.doBirds, 'FF-birds'))
        mtrack.start()

    def doDialog(self, index, elapsedTime):
        dialog = self.dialog[index]
        if index >= (len(self.dialog) - 1):
            self.suit.setLocalPageChat(dialog, 1)
            self.suit.acceptOnce(self.suit.uniqueName('doneChatPage'), self.sceneFinish)
        elif (index % 2) == 0:
            self.suit.setLocalPageChat(dialog, None)
            self.suit.acceptOnce(self.suit.uniqueName('doneChatPage'), self.doDialog, [index + 1])
        else:
            self.flippy.setLocalPageChat(dialog, None)
            self.flippy.acceptOnce(self.flippy.uniqueName('doneChatPage'), self.doDialog, [index + 1])
