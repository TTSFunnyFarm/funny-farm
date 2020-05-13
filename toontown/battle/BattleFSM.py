from direct.fsm.FSM import FSM
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from libotp import *
from toontown.battle import *
from toontown.battle.BattleGlobals import *
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
        point = cogPoints[0][0]
        cog = battle.topCog
        cogPos = point[0]
        cogHpr = VBase3(point[1], 0.0, 0.0)
        cogHeight = cog.getHeight()
        cogOffsetPnt = Point3(0, 0, cogHeight)
        cogName = cog.getStyleName()
        taunt = SuitBattleGlobals.getFaceoffTaunt(cogName, cog.doId)
        toon = base.localAvatar
        MidTauntCamZ = cogHeight * 0.66
        MidTauntCamZLim = cogHeight - 1.8
        if MidTauntCamZ < MidTauntCamZLim:
            MidTauntCamZ = MidTauntCamZLim
        TauntCamX = random.choice((-5, 5))
        TauntCamY = 16
        TauntCamZ = random.choice((MidTauntCamZ, 1, 11))
        cog.setState('Battle')
        cog.headsUp(toon)
        cog.setChatAbsolute(taunt, CFSpeech | CFTimeout)
        toon.setShadowHeight(0)
        toon.stopLookAround()
        toon.headsUp(cog)
        toon.loop('neutral')
        camera.wrtReparentTo(cog)
        camera.setPos(TauntCamX, TauntCamY, TauntCamZ)
        camera.lookAt(cog, cogOffsetPnt)
        cogTrack = Sequence(ActorInterval(cog, random.choice(SuitBattleGlobals.SuitFaceoffAnims[SuitDNA.getSuitBodyType(cogName)])))
        cogTrack.start()
