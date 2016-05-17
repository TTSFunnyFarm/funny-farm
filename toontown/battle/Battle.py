from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from otp.nametag import NametagGlobals
from otp.nametag.NametagConstants import *
from toontown.toonbase import ToontownBattleGlobals
from BattleBase import *
import SuitBattleGlobals
import random

class Battle(NodePath, BattleBase):
    notify = directNotify.newCategory('Battle')
    camPos = ToontownBattleGlobals.BattleCamDefaultPos
    camHpr = ToontownBattleGlobals.BattleCamDefaultHpr
    camFov = ToontownBattleGlobals.BattleCamDefaultFov
    camMenuFov = ToontownBattleGlobals.BattleCamMenuFov
    camJoinPos = ToontownBattleGlobals.BattleCamJoinPos
    camJoinHpr = ToontownBattleGlobals.BattleCamJoinHpr
    camFOFov = ToontownBattleGlobals.BattleCamFaceOffFov
    camFOPos = ToontownBattleGlobals.BattleCamFaceOffPos

    def __init__(self, toons=[], suits=[]):
        NodePath.__init__(self, 'Battle-%d' % id(self))
        BattleBase.__init__(self)
        self.toons = toons
        self.suits = suits

    def enter(self):
        base.localAvatar.inventory.setActivateMode('battle')
        self.enterFaceOff()

    def __faceOff(self, name, callback):
        if len(self.suits) == 0:
            self.notify.warning('__faceOff(): no suits.')
            return
        if len(self.toons) == 0:
            self.notify.warning('__faceOff(): no toons.')
            return
        suit = self.suits[0]
        point = self.suitPoints[0][0]
        suitPos = point[0]
        suitHpr = VBase3(point[1], 0.0, 0.0)
        toon = self.toons[0]
        point = self.toonPoints[0][0]
        toonPos = point[0]
        toonHpr = VBase3(point[1], 0.0, 0.0)
        p = toon.getPos(self)
        toon.setPos(self, p[0], p[1], 0.0)
        toon.setShadowHeight(0)
        suit.setState('Battle')
        suitTrack = Sequence()
        toonTrack = Sequence()
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTrack.append(Func(suit.headsUp, toon))
        taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
        suitTrack.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
        toonTrack.append(Func(toon.loop, 'neutral'))
        toonTrack.append(Func(toon.headsUp, suit))
        suitHeight = suit.getHeight()
        suitOffsetPnt = Point3(0, 0, suitHeight)
        faceoffTime = self.calcFaceoffTime(self.getPos(), self.initialSuitPos)
        faceoffTime = max(faceoffTime, BATTLE_SMALL_VALUE)
        delay = FACEOFF_TAUNT_T
        MidTauntCamHeight = suitHeight * 0.66
        MidTauntCamHeightLim = suitHeight - 1.8
        if MidTauntCamHeight < MidTauntCamHeightLim:
            MidTauntCamHeight = MidTauntCamHeightLim
        TauntCamY = 16
        TauntCamX = random.choice((-5, 5))
        TauntCamHeight = random.choice((MidTauntCamHeight, 1, 11))
        camTrack = Sequence()
        camTrack.append(Func(camera.wrtReparentTo, suit))
        camTrack.append(Func(base.camLens.setMinFov, self.camFOFov/(4./3.)))
        camTrack.append(Func(camera.setPos, TauntCamX, TauntCamY, TauntCamHeight))
        camTrack.append(Func(camera.lookAt, suit, suitOffsetPnt))
        camTrack.append(Wait(delay))
        camTrack.append(Func(base.camLens.setMinFov, self.camFov/(4./3.)))
        camTrack.append(Func(camera.wrtReparentTo, self))
        camTrack.append(Func(camera.setPos, self.camFOPos))
        camTrack.append(Func(camera.lookAt, suit.getPos(self)))
        camTrack.append(Wait(faceoffTime))
        suitTrack.append(Wait(delay))
        toonTrack.append(Wait(delay))
        suitTrack.append(Func(suit.headsUp, self, suitPos))
        suitTrack.append(Func(suit.clearChat))
        toonTrack.append(Func(toon.headsUp, self, toonPos))
        suitTrack.append(Func(suit.loop, 'walk'))
        suitTrack.append(LerpPosInterval(suit, faceoffTime, suitPos, other=self))
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTrack.append(Func(suit.setHpr, self, suitHpr))
        toonTrack.append(Func(toon.loop, 'run'))
        toonTrack.append(LerpPosInterval(toon, faceoffTime, toonPos, other=self))
        toonTrack.append(Func(toon.loop, 'neutral'))
        toonTrack.append(Func(toon.setHpr, self, toonHpr))
        if base.localAvatar == toon:
            soundTrack = Sequence(Wait(delay), SoundInterval(base.localAvatar.soundRun, loop=1, duration=faceoffTime, node=base.localAvatar))
        else:
            soundTrack = Wait(delay + faceoffTime)
        mtrack = Parallel(suitTrack, toonTrack, soundTrack)
        #NametagGlobals.setWant2dNametags(False)
        mtrack = Parallel(mtrack, camTrack)
        done = Func(callback)
        track = Sequence(mtrack, done, name=name)
        track.start()

    def enterFaceOff(self):
        self.notify.debug('enterFaceOff()')
        base.localAvatar.disable()
        self.__faceOff('faceoff-%d' % id(self), self.enterMenu)

    def enterMenu(self):
        camTrack = Parallel()
        camTrack.append(LerpFunctionInterval(base.camLens.setMinFov, duration=1.0, fromData=self.camFov/(4./3.), toData=self.camMenuFov/(4./3.), blendType='easeInOut'))
        camTrack.append(LerpPosInterval(camera, 1.0, self.camPos, blendType='easeInOut'))
        camTrack.append(LerpHprInterval(camera, 1.0, self.camHpr, blendType='easeInOut'))
        menuTrack = Sequence()
        menuTrack.append(Func(base.localAvatar.inventory.setColorScale, 1, 1, 1, 0))
        menuTrack.append(Func(base.localAvatar.inventory.show))
        menuTrack.append(base.localAvatar.inventory.colorScaleInterval(0.5, (1, 1, 1, 1)))
        track = Sequence(camTrack, menuTrack)
        track.start()
