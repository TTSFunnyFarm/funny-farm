from panda3d.core import *
from toontown.toonbase import TTLocalizer
from toontown.cutscenes.CutscenesGlobals import *
from toontown.toon import NPCToons
from direct.directnotify import DirectNotifyGlobal

class CutsceneBase:
    notify = DirectNotifyGlobal.directNotify.newCategory('CutsceneBase')

    def __init__(self, id):
        self.id = id
        self.track = None # A track is always needed cause hint hint, it's a cutscene.
        self.bgm = None # If this is set CutsceneBase will automatically play it.
        self.dialog = None # Touch this and you die.
        self.actors = None # ^
        if TTLocalizer.CutsceneDialogDict.get(id): # This automatically grabs the dialog for the associated ID.
            self.dialog = TTLocalizer.CutsceneDialogDict[id]

    def getId(self):
        return self.id

    def getTrack(self):
        return self.track

    def enter(self):
        self.notify.info('Entering %s!' % self.__class__.__name__)
        if self.bgm:
            musicMgr.stopMusic()
            musicMgr.playMusic(self.bgm)
        base.localAvatar.disable()
        base.localAvatar.setAnimState('neutral')
        camera.wrtReparentTo(render)
        if self.actors:
            for key, value in self.actors.items():
                if not isinstance(value, list):
                    continue
                if len(value) == 4:
                    if value[0] == TOON:
                        if len(value[1]) == 6 and type(value[2]) == int:
                            toon = NPCToons.createLocalNPC(value[2])
                            toon.reparentTo(value[3])
                            toon.setPosHpr(*value[1])
                            toon.addActive()
                            self.actors[key] = toon

    def doAnimate(self, actor, emote, anim=None):
        if emote and actor:
            if emote < 3:
                if emote == SAD_EYES:
                    actor.sadEyes()
                elif emote == ANGRY_EYES:
                    actor.angryEyes()
                else:
                    actor.normalEyes()
                actor.blinkEyes()
    def exit(self):
        self.notify.info('Exiting %s!' % self.__class__.__name__)
        base.localAvatar.enable()
        if self.bgm:
            self.bgm.stop()
            musicMgr.stopMusic()
            musicMgr.playCurrentZoneMusic()
