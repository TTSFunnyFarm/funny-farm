from toontown.cutscenes.CutsceneBase import CutsceneBase
from direct.interval.IntervalGlobal import *
from toontown.cutscenes.CutscenesGlobals import *
from panda3d.core import *

class MeterAlertScene(CutsceneBase):
    id = 1003

    def __init__(self):
        CutsceneBase.__init__(self, self.id)
        self.door = base.cr.playGame.hood.place.labDoor
        doorOrigin = self.door.getParent()
        self.doorSfx = base.loader.loadSfx('phase_3.5/audio/sfx/Door_Open_1.ogg')
        track = Sequence()
        track.append(Parallel(SoundInterval(self.doorSfx, node=self.door), LerpHprInterval(self.door.find('**/door_double_round_ur_left'), duration=0.5, hpr=Vec3(-100, 0, 0), startHpr=Vec3(0, 0, 0), other=doorOrigin, blendType='easeInOut')))
        track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(15, 20, 5), hpr=Vec3(-150, 0, 0), blendType='easeInOut'))
        track.append(Func(self.doDialog, 0, 0))
        self.track = track
        self.actors = {'flippy': base.cr.playGame.hood.place.npcs[0],
         'dimm': [TOON, [25, 0, 0.5, 20, 0, 0], 1013, base.cr.playGame.hood.place.interior]}

    def delete(self):
        CutsceneBase.delete(self)
        del self.door
        del self.doorSfx

    def enter(self):
        CutsceneBase.enter(self)
        base.hideUI()

    def exit(self):
        CutsceneBase.exit(self)
        self.door.find('**/door_double_round_ur_left').setHpr(0, 0, 0)
        base.showUI()

    def sceneFinish(self, elapsedTime):
        if self.actors.get('dimm'):
            actor = self.actors['dimm']
            actor.removeActive()
            actor.delete()
            del actor
        messenger.send('cutscene-done')

    def doDialog(self, index, elapsedTime):
        dialog = self.dialog[index]
        dimm = self.actors['dimm']
        flippy = self.actors['flippy']
        if index == 0:
            dimm.setLocalPageChat(dialog, 1)
            dimm.acceptOnce(dimm.uniqueName('doneChatPage'), self.doDialog, [index + 1])
        else:
            track = Sequence()
            track.append(camera.posHprInterval(1.5, Point3(-5, 9, flippy.getHeight() - 0.5), Vec3(210, -2, 0), other=flippy, blendType='easeInOut'))
            track.append(Func(flippy.setLocalPageChat, dialog, 1))
            track.append(Func(flippy.acceptOnce, flippy.uniqueName('doneChatPage'), self.sceneFinish))
            track.start()
