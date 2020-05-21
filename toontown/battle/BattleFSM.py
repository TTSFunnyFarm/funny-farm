from direct.fsm.FSM import FSM
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from libotp import *
from toontown.battle import *
from toontown.battle.BattleGlobals import *
from toontown.battle import BattleUtil
from toontown.suit import SuitDNA
import random

class BattleFSM(FSM):
    def __init__(self, battle):
        self.battle = battle
        FSM.__init__(self, 'BattleFSM')

    def enterFaceOff(self):
        delay = FACEOFF_TAUNT_T
        battle = self.battle
        battle.update()

        cogPoint = cogPoints[0][0]
        cog = battle.topCog
        toon = base.localAvatar
        cogPos = cogPoint[0] # h = point[1]
        toonPoint = toonPoints[0][0]
        toonPos = toonPoint[0]
        cogHeight = cog.getHeight()
        cogName = cog.getStyleName()
        cogOffsetPnt = Point3(0, 0, cogHeight)
        taunt = SuitBattleGlobals.getFaceoffTaunt(cogName, cog.doId)

        cogMoveTime = BattleUtil.calcSuitMoveTime(cog.getPos(self.battle), cogPos)
        toonMoveTime = BattleUtil.calcToonMoveTime(toon.getPos(self.battle), toonPos)

        MidTauntCamZ = cogHeight * 0.66
        MidTauntCamZLim = cogHeight - 1.8
        MidTauntCamZ = min((MidTauntCamZ, MidTauntCamZLim))

        cog.setState('Battle')
        BattleUtil.toonFaceCog(toon, cog)
        cog.setChatAbsolute(taunt, CFSpeech | CFTimeout)
        toon.loop('neutral')
        toon.lerpLookAt(cog.getPos(toon) + cogOffsetPnt, time=0.5)
        camera.wrtReparentTo(cog)
        camera.setPos(random.choice((-5, 5)), 16, random.uniform(MidTauntCamZ, 11))
        camera.lookAt(cog, cogOffsetPnt)
        duelingTrack = Parallel(Sequence(LerpPosInterval(cog, cogMoveTime, cogPos, other=self.battle),
            LerpHprInterval(cog, 1, Point3(cogPoint[1], 0, 0), other=self.battle)),
            Sequence(LerpPosInterval(toon, toonMoveTime, toonPos, other=self.battle),
            LerpHprInterval(toon, 1, Point3(toonPoint[1], 0, 0), other=self.battle)))
        camTrack = Sequence(LerpPosInterval(camera, duelingTrack.getDuration(), Point3(camera.getX() + 10, camera.getY() + 10, camera.getZ() + 5), blendType='easeIn'))
        duelingTrack = Parallel(camTrack, duelingTrack)
        faceoffTrack = Sequence(ActorInterval(cog, random.choice(SuitBattleGlobals.SuitFaceoffAnims[SuitDNA.getSuitBodyType(cogName)])),
                            Func(cog.headsUp, self.battle, cogPos),
                            Func(toon.headsUp, self.battle, toonPos),
                            duelingTrack,
                            Wait(camTrack.getDuration()))
        faceoffTrack.start()
