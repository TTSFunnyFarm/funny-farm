from direct.interval.IntervalGlobal import *
from toontown.toonbase.ToontownBattleGlobals import *
from BattleBase import *
from BattleProps import *
from BattleSounds import *
import MovieCamera
import MovieUtil

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
        return #__damageUp(powerUp)
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
    tracks = Parallel()
    tracks.append(ActorInterval(toon, 'spit', startFrame=0, endFrame=67))
    glass = globalPropPool.getProp('glass-tu')
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    glassTrack = Sequence(Func(MovieUtil.showProp, glass, hand_jointpath0), ActorInterval(glass, 'glass-tu', startFrame=0, endFrame=67), Func(toon.loop, 'neutral'), Func(hand_jointpath1.removeNode), Func(hand_jointpath0.removeNode), Func(MovieUtil.removeProp, glass))
    toonUpTrack = Sequence(Wait(0.2), Func(toon.setAnimState, 'jump'), Func(toon.setHealth, toon.hp + hp, toon.maxHp, showText=1), Func(sfx.play), Wait(toon.getDuration('jump') + 1))
    glassTrack.append(toonUpTrack)
    tracks.append(glassTrack)
    return tracks

def __damageUp(powerUp):
    # in progress #
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
    glassTrack = Sequence(Func(MovieUtil.showProp, glass, hand_jointpath0), ActorInterval(glass, 'glass-dmg', startFrame=0, endFrame=67), Func(toon.loop, 'neutral'), Func(hand_jointpath1.removeNode), Func(hand_jointpath0.removeNode), Func(MovieUtil.removeProp, glass))
    damageUpTrack = Sequence(Wait(0.2), Func(toon.setAnimState, 'jump'), Func(toon.setDamageEffect, dmg), Func(sfx.play), Wait(toon.getDuration('jump') + 1))
    glassTrack.append(damageUpTrack)
    tracks.append(glassTrack)
