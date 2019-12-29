from panda3d.core import *
from toontown.toonbase import TTLocalizer
from toontown.cutscenes.CutscenesGlobals import *
from toontown.toon import NPCToons

class CutsceneBase:
    def __init__(self, id):
        self.id = id
        self.track = None
        self.bgm = None
        self.dialog = None
        self.actors = None
        if TTLocalizer.CutsceneDialogDict.get(id):
            self.dialog = TTLocalizer.CutsceneDialogDict[id]
        #base.cr.cutsceneMgr.cutscenes[id] = self
        #print(base.cr.cutsceneMgr.cutscenes)

    def getId(self):
        return self.id

    def getTrack(self):
        return self.track

    def enter(self):
        print("entering!")
        if self.bgm:
            musicMgr.stopMusic()
            musicMgr.playMusic(self.bgm)
        base.localAvatar.disable()
        base.localAvatar.setAnimState('neutral')
        camera.wrtReparentTo(render)
        if self.actors:
            for key, value in self.actors:
                if value[0] == TOON:
                    if len(value) == 4:
                        if len(value[1]) == 6 and type(value[2]) == int:
                            toon = NPCToons.createLocalNPC(value[2])
                            toon.reparentTo(value[3])
                            toon.setPosHpr(*value[1])
                            toon.addActive()
                            self.actors[key] = toon



    def exit(self):
        print("exiting!")
        base.localAvatar.enable()
        if self.bgm:
            self.bgm.stop()
            musicMgr.stopMusic()
            musicMgr.playCurrentZoneMusic()
