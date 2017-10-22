from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.suit.BattleSuit import BattleSuit
from toontown.suit.SuitDNA import SuitDNA
from toontown.toon import NPCToons

def getCutscene(questId):
    if questId == 1001:
        return scene1001()
    elif questId == 1002:
        return scene1002()

def scene1001():
    track = Sequence()
    track.append(Func(camera.wrtReparentTo, render))
    track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(20, -20, 7), hpr=Vec3(22.5, -10, 0), blendType='easeInOut'))
    track.append(Func(base.localAvatar.showInfoBubble, 1001, 'cutscene-done'))
    base.localAvatar.removeQuest(1001)
    base.localAvatar.addQuest(1002)
    return track

def scene1002():
    bgm = base.loader.loadSfx('phase_12/audio/bgm/Bossbot_Entry_v1.ogg')
    suit = base.cr.playGame.hood.suit
    flippy = base.cr.playGame.hood.flippy
    track = Sequence()
    track.append(Func(musicMgr.stopMusic))
    track.append(Func(base.playMusic, bgm, 1))
    track.append(Func(aspect2d.hide))
    track.append(Func(camera.wrtReparentTo, render))
    track.append(LerpPosHprInterval(camera, duration=3.0, pos=Point3(-67, -40, 9), hpr=Vec3(30, -10, 0), blendType='easeInOut'))

    sceneDialog = TTLocalizer.CutsceneDialogDict[1002]

    def cleanup():
        base.cr.playGame.hood.unloadQuestChanges()
        base.localAvatar.removeQuest(1002)
        base.localAvatar.addQuest(1003)
        bgm.stop()
        musicMgr.playCurrentZoneMusic()
        aspect2d.show()
        messenger.send('cutscene-done')

    def handleDone(elapsedTime):
        flippy.enterTeleportOut(callback=cleanup)

    def sceneDone(elapsedTime):
        mtrack = Sequence()
        mtrack.append(suit.beginSupaFlyMove(suit.getPos(), 0, 'toSky'))
        mtrack.append(Func(flippy.loop, 'walk'))
        mtrack.append(Parallel(LerpPosHprInterval(camera, duration=1.5, pos=(-66, -35, 4), hpr=(15, 0, 0), blendType='easeInOut'), LerpHprInterval(flippy, duration=1.5, hpr=Vec3(195, 0, 0))))
        mtrack.append(Func(flippy.loop, 'neutral'))
        mtrack.append(Func(flippy.setLocalPageChat, sceneDialog[1] % base.localAvatar.getName(), 1))
        mtrack.append(Func(flippy.acceptOnce, flippy.uniqueName('doneChatPage'), handleDone))
        mtrack.start()

    def doDialog(index, elapsedTime):
        dialog = sceneDialog[0][index]
        if index >= (len(sceneDialog[0]) - 1):
            suit.setLocalPageChat(dialog, 1)
            suit.acceptOnce(suit.uniqueName('doneChatPage'), sceneDone)
        elif (index % 2) == 0:
            suit.setLocalPageChat(dialog, None)
            suit.acceptOnce(suit.uniqueName('doneChatPage'), doDialog, [index + 1])
        else:
            flippy.setLocalPageChat(dialog, None)
            flippy.acceptOnce(flippy.uniqueName('doneChatPage'), doDialog, [index + 1])

    track.append(Func(doDialog, 0, 0))
    return track
