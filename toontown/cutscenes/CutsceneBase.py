from panda3d.core import *
from toontown.toonbase import TTLocalizer
from toontown.cutscenes.CutscenesGlobals import *
from toontown.toon import NPCToons, Toon
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *

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

    def delete(self):
        del self.id
        del self.track
        del self.dialog
        del self.bgm
        del self.actors

    def getId(self):
        return self.id

    def getTrack(self):
        return self.track

    def enter(self):
        self.notify.debug('Entering %s!' % self.__class__.__name__)
        if self.bgm:
            musicMgr.stopMusic()
            musicMgr.playMusic(self.bgm, looping=1)
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

    def exit(self):
        self.notify.debug('Exiting %s!' % self.__class__.__name__)
        base.localAvatar.enable()
        if self.bgm:
            self.bgm.stop()
            self.bgm = None
            musicMgr.stopMusic()
            musicMgr.playCurrentZoneMusic()

    def doAnimate(self, actor, anim, emote=None, muzzle=None):
        if not actor:
            return
        if emote and isinstance(actor, Toon.Toon):
            if emote < 4:
                if emote == SAD_EYES:
                    actor.sadEyes()
                elif emote == ANGRY_EYES:
                    actor.angryEyes()
                elif emote == SURPRISE_EYES:
                    actor.surpriseEyes()
                else:
                    actor.normalEyes()
                actor.blinkEyes()
        if muzzle and isinstance(actor, Toon.Toon):
            if muzzle < 6:
                if emote == SAD_MUZZLE:
                    actor.showSadMuzzle()
                elif emote == ANGRY_MUZZLE:
                    actor.showAngryMuzzle()
                elif emote == SMILE_MUZZLE:
                    actor.showSmileMuzzle()
                elif emote == LAUGH_MUZZLE:
                    actor.showLaughMuzzle()
                elif emote == SURPRISE_MUZZLE:
                    actor.showSurpriseMuzzle()
                else:
                    actor.showNormalMuzzle()
        if anim:
            seq = Sequence()
            anims = actor.getAnimNames()
            if anim in anims:
                animDuration = actor.getDuration(anim)
                seq.append(ActorInterval(actor, anim))
                seq.append(Wait(animDuration))

            if 'neutral' in anims:
                seq.append(Func(actor.loop, 'neutral'))

            seq.start()
