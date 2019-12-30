from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.suit.BattleSuit import BattleSuit
from toontown.suit.SuitDNA import SuitDNA
from toontown.toon import NPCToons

def getCutscene(questId):
    scene = globals().get('scene%d' % questId)
    return scene()

def scene1001():
    track = Sequence()
    track.append(Func(camera.wrtReparentTo, render))
    track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(20, -20, 7), hpr=Vec3(22.5, -10, 0), blendType='easeInOut'))
    track.append(Func(base.localAvatar.showInfoBubble, 1001, 'cutscene-done'))
    base.localAvatar.removeQuest(1001)
    base.localAvatar.addQuest(1002)
    return track

def scene1002():
    bgm = base.loader.loadMusic('phase_12/audio/bgm/Bossbot_Entry_v1.ogg')
    suit = base.cr.playGame.hood.suit
    flippy = base.cr.playGame.hood.flippy
    track = Sequence()
    track.append(Func(musicMgr.stopMusic))
    track.append(Func(musicMgr.playMusic, bgm, 1))
    track.append(Func(aspect2d.hide))
    track.append(Func(camera.wrtReparentTo, render))
    track.append(LerpPosHprInterval(camera, duration=3.0, pos=Point3(-47, -40, 9), hpr=Vec3(30, -10, 0), blendType='easeInOut'))

    sceneDialog = TTLocalizer.CutsceneDialogDict[1002]

    def cleanup():
        bgm.stop()
        musicMgr.playCurrentZoneMusic()
        aspect2d.show()

    def questDone():
        flippy.setAllowedToTalk(0)
        flippy.enterTeleportOut(callback=base.cr.playGame.hood.unloadQuestChanges)

    def sceneDone(elapsedTime):
        mtrack = Sequence()
        mtrack.append(suit.beginSupaFlyMove(suit.getPos(), 0, 'toSky'))
        mtrack.append(Func(base.transitions.fadeOut, 1.0))
        mtrack.append(Wait(1.0))
        mtrack.append(Func(base.localAvatar.enable))
        mtrack.append(Func(suit.removeActive))
        mtrack.append(Func(flippy.setHpr, 195, 0, 0))
        mtrack.append(Func(flippy.setMainQuest, 1002))
        mtrack.append(Func(base.transitions.fadeIn, 1.0))
        mtrack.append(Wait(1.0))
        mtrack.append(Func(cleanup))
        mtrack.append(Func(flippy.acceptOnce, 'cutscene-done', questDone))
        mtrack.start()

    def doDialog(index, elapsedTime):
        dialog = sceneDialog[index]
        if index >= (len(sceneDialog) - 1):
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

def scene1003():
    doorSfx = base.loader.loadSfx('phase_3.5/audio/sfx/Door_Open_1.ogg')
    flippy = base.cr.playGame.hood.place.npcs[0]
    dimm = NPCToons.createLocalNPC(1013)
    dimm.reparentTo(base.cr.playGame.hood.place.interior)
    dimm.setPosHpr(25, 0, 0.5, 20, 0, 0)
    dimm.addActive()

    track = Sequence()
    door = base.cr.playGame.hood.place.labDoor
    doorOrigin = door.getParent()
    track.append(Parallel(SoundInterval(doorSfx, node=door), LerpHprInterval(door.find('**/door_double_round_ur_left'), duration=0.5, hpr=Vec3(-100, 0, 0), startHpr=Vec3(0, 0, 0), other=doorOrigin, blendType='easeInOut')))
    track.append(Func(aspect2d.hide))
    track.append(Func(camera.wrtReparentTo, render))
    track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(15, 20, 5), hpr=Vec3(-150, 0, 0), blendType='easeInOut'))

    sceneDialog = TTLocalizer.CutsceneDialogDict[1004]

    def cleanup(elapsedTime):
        dimm.delete()
        door.find('**/door_double_round_ur_left').setHpr(0, 0, 0)
        aspect2d.show()
        messenger.send('cutscene-done')

    def doDialog(index, elapsedTime):
        dialog = sceneDialog[index]
        if index == 0:
            dimm.setLocalPageChat(dialog, 1)
            dimm.acceptOnce(dimm.uniqueName('doneChatPage'), doDialog, [index + 1])
        elif index == 1:
            mtrack = Sequence()
            mtrack.append(camera.posHprInterval(1.5, Point3(-5, 9, flippy.getHeight() - 0.5), Vec3(210, -2, 0), other=flippy, blendType='easeInOut'))
            mtrack.append(Func(flippy.setLocalPageChat, dialog, 1))
            mtrack.append(Func(flippy.acceptOnce, flippy.uniqueName('doneChatPage'), cleanup))
            mtrack.start()

    track.append(Func(doDialog, 0, 0))
    return track

def scene1004():
    flippy = base.cr.playGame.hood.place.flippy
    dimm = base.cr.playGame.hood.place.npcs[0]
    surlee = base.cr.playGame.hood.place.npcs[1]
    prepostera = base.cr.playGame.hood.place.npcs[2]

    track = Sequence()
    track.append(Func(aspect2d.hide))
    track.append(Func(camera.wrtReparentTo, render))
    track.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(8, 8, flippy.getHeight() - 0.5), hpr=Vec3(120, 0, 0), other=flippy, blendType='easeInOut'))

    sceneDialog = TTLocalizer.CutsceneDialogDict[1005]

    def sceneDone(elapsedTime):
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

    def sillyMeterScene(elapsedTime):
        smtrack = Sequence()
        smtrack.append(Func(base.transitions.fadeOut, 1.0))
        smtrack.append(Wait(1.0))
        smtrack.append(Func(camera.setPosHpr, 18, -29, 14, 30, -5, 0))
        smtrack.append(Func(base.transitions.fadeIn, 1.0))
        smtrack.append(Wait(1.0))
        smtrack.append(Func(messenger.send, 'SillyMeterPhase', ['4To5']))
        smtrack.append(Wait(7.0))
        smtrack.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(12, 10, 5), hpr=Vec3(120, -5, 0), other=flippy, blendType='easeInOut'))
        smtrack.append(Func(flippy.setLocalPageChat, sceneDialog[1], 1))
        smtrack.append(Func(flippy.acceptOnce, flippy.uniqueName('doneChatPage'), sceneDone))
        smtrack.append(Func(aspect2d.show))
        smtrack.start()

    def doDialog(index, elapsedTime):
        dialog = sceneDialog[0][index]
        if index == 0:
            flippy.setLocalPageChat(dialog, None)
            flippy.acceptOnce(flippy.uniqueName('doneChatPage'), doDialog, [index + 1])
        elif index == 1:
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=2.0, pos=Point3(-10, 10, 4), hpr=Vec3(-135, 0, 0), other=dimm, blendType='easeInOut'))
            mtrack.append(Func(dimm.setLocalPageChat, dialog, None))
            mtrack.append(Func(dimm.acceptOnce, dimm.uniqueName('doneChatPage'), doDialog, [index + 1]))
            mtrack.start()
        elif index == 2:
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=1.0, pos=Point3(10, 10, 4), hpr=Vec3(135, 0, 0), other=surlee, blendType='easeInOut'))
            mtrack.append(Func(surlee.setLocalPageChat, dialog, None))
            mtrack.append(Func(surlee.acceptOnce, surlee.uniqueName('doneChatPage'), doDialog, [index + 1]))
            mtrack.start()
        elif index == 3:
            mtrack = Sequence()
            mtrack.append(LerpPosHprInterval(camera, duration=1.0, pos=Point3(0, 10, 4), hpr=Vec3(180, 0, 0), other=prepostera, blendType='easeInOut'))
            mtrack.append(Func(prepostera.setLocalPageChat, dialog, None))
            mtrack.append(Func(prepostera.acceptOnce, prepostera.uniqueName('doneChatPage'), sillyMeterScene))
            mtrack.start()

    track.append(Func(doDialog, 0, 0))
    return track

def scene1007():
    camTrack1 = Sequence()
    camTrack2 = Sequence()

    camTrack1.append(Func(camera.wrtReparentTo, render))
    camTrack1.append(Func(base.localAvatar.acceptOnce, 'nextInfoPage', camTrack2.start))
    camTrack1.append(LerpPosHprInterval(camera, duration=3.0, pos=Point3(-25, 25, 9), hpr=Vec3(0, -2, 0), blendType='easeInOut'))

    camTrack2.append(Func(camTrack1.pause))
    camTrack2.append(LerpPosHprInterval(camera, duration=1.5, pos=Point3(30, 20, 9), hpr=Vec3(-15, -2, 0), blendType='easeInOut'))

    track = Sequence()
    track.append(Func(base.localAvatar.showInfoBubble, 1, 'cutscene-done'))
    track.append(Func(base.localAvatar.acceptOnce, 'nextInfoPage', camTrack1.start))
    # All info bubbles will be added to quest history so that they only happen once.
    track.append(Func(base.localAvatar.acceptOnce, 'cutscene-done', base.localAvatar.addQuestHistory, [1]))
    return track

def scene1014():
    for building in base.cr.playGame.getActiveZone().buildings:
        if 'toon_landmark_hq' in building.getBuildingNodePath().getName():
            toonHq = building
    if not toonHq.getQuestOffer():
        toonHq.setQuestOffer(4, hq=1)
    camTrack = Sequence()
    camTrack.append(Func(base.localAvatar.questPage.hideQuestsOnscreen))
    camTrack.append(Func(camera.wrtReparentTo, render))
    camTrack.append(LerpPosHprInterval(camera, duration=3.0, pos=Point3(-27, -10, 8), hpr=Vec3(-45, 0, 0), blendType='easeInOut'))

    track = Sequence()
    track.append(Func(base.localAvatar.questPage.showQuestsOnscreen))
    track.append(Func(base.localAvatar.showInfoBubble, 4, 'cutscene-done'))
    track.append(Func(base.localAvatar.acceptOnce, 'nextInfoPage', base.localAvatar.acceptOnce, ['nextInfoPage', camTrack.start]))

    def sceneDone():
        if toonHq.getQuestOffer() == 4:
            toonHq.clearQuestOffer()
        base.localAvatar.addQuestHistory(4)

    track.append(Func(base.localAvatar.acceptOnce, 'cutscene-done', sceneDone))
    return track

def scene1028():
    interior = base.cr.playGame.street.place.interior
    street = base.cr.playGame.street.geom
    sky = base.cr.playGame.street.sky

    def loadStreet():
        interior.reparentTo(hidden)
        interior.stash()
        street.unstash()
        street.reparentTo(render)
        sky.unstash()
        sky.reparentTo(render)
        base.cr.playGame.street.setupLandmarkBuildings()
        aspect2d.hide()
        camera.wrtReparentTo(render)
        camera.setPosHpr(55, 163, 12, 39, 0, 0)
        base.transitions.fadeIn(1.0)

    def loadInterior():
        street.reparentTo(hidden)
        street.stash()
        sky.reparentTo(hidden)
        sky.stash()
        base.cr.playGame.street.destroyLandmarkBuildings()
        interior.unstash()
        interior.reparentTo(render)
        aspect2d.show()
        base.localAvatar.enable()
        base.localAvatar.disable()
        base.localAvatar.setAnimState('neutral')
        base.transitions.fadeIn(1.0)

    track = Sequence()
    track.append(Func(base.transitions.fadeOut, 1.0))
    track.append(Wait(1.0))
    track.append(Func(loadStreet))
    track.append(Wait(1.0))
    track.append(Func(messenger.send, 'spawnBuilding-1100', [18]))
    track.append(Wait(10.0))
    track.append(Func(base.transitions.fadeOut, 1.0))
    track.append(Wait(1.0))
    track.append(Func(loadInterior))
    track.append(Wait(1.0))
    track.append(Func(base.localAvatar.showInfoBubble, 1028, 'cutscene-done', 1001))
    track.append(Func(base.localAvatar.addQuestHistory, 1028))
    return track
