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
        cogPos = point[0] # h = point[1]
        toonPoint = toonPoints[0][0]
        toonPos = point[0]
        cogHeight = cog.getHeight()
        cogName = cog.getStyleName()
        cogOffsetPnt = Point3(0, 0, cogHeight)
        taunt = SuitBattleGlobals.getFaceoffTaunt(cogName, cog.doId)

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
        camTrack = Sequence(LerpPosInterval(camera, 2, Point3(camera.getX(), camera.getY() + 20, camera.getZ()), blendType='easeIn'))
        faceoffTrack = Sequence(ActorInterval(cog, random.choice(SuitBattleGlobals.SuitFaceoffAnims[SuitDNA.getSuitBodyType(cogName)])),
                            Func(camTrack.start),
                            Wait(camTrack.getDuration()))
        faceoffTrack.start()
