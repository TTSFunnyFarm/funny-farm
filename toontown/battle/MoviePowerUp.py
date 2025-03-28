from direct.interval.IntervalGlobal import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.battle import MovieCamera
from toontown.battle import MovieUtil

def doPowerUp(powerUp):
    if len(powerUp) == 0:
        return (None, None)
    track = Sequence()
    for p in powerUp:
        ival = __doPowerUpLevel(p)
        if ival:
            track.append(ival)
    camDuration = track.getDuration()
    camTrack = MovieCamera.chooseHealShot(powerUp, camDuration)
    return (track, camTrack)

def __doPowerUpLevel(powerUp):
    level = powerUp['level']
    if level == 0 or level == 4:
        return __toonUp(powerUp)
    elif level == 1 or level == 5:
        return __damageUp(powerUp)
    elif level == 2 or level == 6:
        return #__defenseUp(powerUp)
    elif level == 3:
        return #__accuracyUp(powerUp)
    return None

def __toonUp(powerUp):
    toon = powerUp['toon']
    level = powerUp['level']
    hp = powerUp['target']['hp']
    sfx = base.loader.loadSfx('phase_4/audio/sfx/MG_pairing_all_matched.ogg')
    sfx2 = base.loader.loadSfx('phase_5/audio/sfx/AA_squirt_glasswater.ogg')
    tracks = Sequence()
    spitTracks = Parallel()
    spitAct = ActorInterval(toon, 'spit', startFrame=0, endFrame=67)
    glass = globalPropPool.getProp('soda_can')
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    glassTrack = Sequence(Func(MovieUtil.showProp, glass, hand_jointpath0, Point3(0.05, 0, 0.25), Point3(20, -80, 0)),
     Wait(spitAct.getDuration()),
     Func(toon.loop, 'neutral'),
     Func(hand_jointpath1.removeNode),
     Func(hand_jointpath0.removeNode),
     Func(MovieUtil.removeProp, glass))
    soundTrack = Sequence(Wait(1),
     SoundInterval(sfx2, node=toon, duration=0.8, volume=1.0))
    toonUpTrack = Sequence(ActorInterval(toon, 'jump', loop=0, startTime=0.2),
     Func(toon.setHealth, toon.hp + hp, toon.maxHp, showText=1),
     Func(sfx.play),
     Wait(toon.getDuration('jump')))
    spitTracks.append(glassTrack)
    spitTracks.append(spitAct)
    spitTracks.append(soundTrack)
    tracks.append(spitTracks)
    tracks.append(toonUpTrack)
    return tracks

def __damageUp(powerUp):
    # TODO: FINISH
    toon = powerUp['toon']
    level = powerUp['level']
    dmg = powerUp['target']['hp']
    sfx = base.loader.loadSfx('phase_4/audio/sfx/MG_pairing_all_matched.ogg')
    tracks = Parallel()
    tracks.append(ActorInterval(toon, 'spit', startFrame=0, endFrame=67))
    glass = globalPropPool.getProp('glass-dmg')
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    glassTrack = Sequence(Func(MovieUtil.showProp, glass, hand_jointpath0),
     ActorInterval(glass, 'glass-dmg', startFrame=0, endFrame=67),
     Func(toon.loop, 'neutral'),
     Func(hand_jointpath1.removeNode),
     Func(hand_jointpath0.removeNode),
     Func(MovieUtil.removeProp, glass))
    damageUpTrack = Sequence(ActorInterval(toon, 'jump', loop=0, startTime=0.2),
     Func(toon.setDamageEffect, dmg),
     Func(sfx.play),
     Wait(toon.getDuration('jump')))
    glassTrack.append(damageUpTrack)
    tracks.append(glassTrack)
    return tracks
