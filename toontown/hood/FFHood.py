from panda3d.core import *
from direct.interval.IntervalGlobal import *
from otp.nametag.NametagConstants import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toon import NPCToons
from toontown.toon import TTEmote
from ToonHood import ToonHood
import SkyUtil

class FFHood(ToonHood):

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.FunnyFarm
        self.TTZoneId = ToontownGlobals.ToontownCentral
        self.hoodFile = 'phase_14/models/neighborhoods/funny_farm'
        self.spookyHoodFile = 'phase_14/models/neighborhoods/funny_farm_halloween'
        self.winterHoodFile = 'phase_14/models/neighborhoods/funny_farm_winter'
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (1.0, 0.5, 0.4, 1.0)

    def enter(self, shop=None, tunnel=None, init=0):
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)
        self.worker0Interval.loop()
        self.worker1Interval.loop()
        self.worker2Interval.loop()
        self.directorSpeech.loop()

    def exit(self):
        ToonHood.exit(self)
        self.worker0Interval.pause()
        self.worker1Interval.pause()
        self.worker2Interval.pause()
        self.directorSpeech.pause()

    def load(self):
        ToonHood.load(self)
        # This whole section is pretty messy but whatever
        self.npcs.append(NPCToons.createLocalNPC(1013))
        self.npcs.append(NPCToons.createLocalNPC(1014))
        self.npcs.append(NPCToons.createLocalNPC(1015))
        for npc in self.npcs:
            npc.reparentTo(self.geom)
            npc.initializeBodyCollisions('toon')
        for npc in self.npcs[3:5]:
            clipBoard = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
            placeholder = npc.rightHand.attachNewNode('ClipBoard')
            clipBoard.instanceTo(placeholder)
            placeholder.setH(180)
            placeholder.setScale(render, 1.0)
            placeholder.setPos(0, 0, 0.1)
        shovel = loader.loadModel('phase_5.5/models/estate/shovels').find('**/shovelC')
        shovel.setH(-90)
        shovel.setP(232)
        shovel.setX(0.2)
        shovel.reparentTo(self.npcs[2].rightHand)
        
        self.npcs[0].setPosHpr(-35, -55, 0, 180, 0, 0)
        self.npcs[1].setPosHpr(-4, -82, 13.1, 35, 0, 0)
        self.npcs[2].setPosHpr(3, -80, 0.25, 270, 0, 0)
        self.npcs[3].setPosHpr(-37, -57, 0, 230, 0, 0)
        self.npcs[4].setPosHpr(-2, -50, 0, 0, 0, 0)
        self.npcs[5].setPosHpr(50.3, -61.3, 0, 0, 0, 0)
        self.npcs[6].setPosHpr(53, -60, 0, 45, 0, 0)
        self.npcs[7].setPosHpr(55, -68, 0, 25, 0, 0)

        self.npcs[3].pingpong('scientistWork', fromFrame=0, toFrame=195)
        self.npcs[4].loop('scientistEmcee')
        self.npcs[5].loop('scientistGame')
        self.npcs[6].loop('scientistGame')

        self.worker0Interval = Sequence(
            Wait(8.16),
            Func(TTEmote.doYes, self.npcs[0]),
            Wait(8.16)
        )
        self.worker1Interval = Sequence(
            Wait(10),
            Func(self.npcs[1].loop, 'walk'),
            LerpHprInterval(self.npcs[1], 2, (215, 0, 0)),
            LerpPosInterval(self.npcs[1], 5, (5, -96, 11.5)),
            Func(self.npcs[1].loop, 'neutral'),
            Wait(10),
            Func(self.npcs[1].loop, 'walk'),
            LerpHprInterval(self.npcs[1], 2, (35, 0, 0)),
            LerpPosInterval(self.npcs[1], 5, (-4, -82, 13.1)),
            Func(self.npcs[1].loop, 'neutral')
        )
        self.worker2Interval = Sequence(
            Func(self.npcs[2].setPlayRate, 1.0, 'start-dig'),
            Func(self.npcs[2].play, 'start-dig'),
            Wait(self.npcs[2].getDuration('start-dig')),
            Func(self.npcs[2].loop, 'loop-dig'),
            Wait(self.npcs[2].getDuration('loop-dig') * 10),
            Func(self.npcs[2].setPlayRate, -0.5, 'start-dig'),
            Func(self.npcs[2].play, 'start-dig'),
            Wait(self.npcs[2].getDuration('start-dig')),
            Func(self.npcs[2].loop, 'neutral'),
            Wait(10)
        )
        self.directorSpeech = Sequence(
            Wait(8),
            Func(self.npcs[4].clearChat),
            Wait(4),
            Func(self.npcs[4].setChatAbsolute, 'Oh, Hello! I\'m Dudley, the director of operations around here.', CFSpeech|CFTimeout),
            Wait(6),
            Func(self.npcs[4].setChatAbsolute, 'You may have noticed the playground looks a little different. We\'re making some big changes to this town!', CFSpeech|CFTimeout),
            Wait(8),
            Func(self.npcs[4].setChatAbsolute, 'Not only are we building a new Toon Hall, we\'re also going to rebuild the whole playground!', CFSpeech|CFTimeout),
            Wait(8),
            Func(self.npcs[4].setChatAbsolute, 'That\'s right! Funny Farm will finally look like... a farm! Isn\'t that exciting?', CFSpeech|CFTimeout),
            Wait(8),
            Func(self.npcs[4].setChatAbsolute, 'For the next several weeks we will be hard at work...', CFSpeech|CFTimeout),
            Wait(5),
            Func(self.npcs[4].setChatAbsolute, '...Well, most of the time, anyway. You know how construction goes.', CFSpeech|CFTimeout),
            Wait(6),
            Func(self.npcs[4].setChatAbsolute, 'In the meantime, I hope you can bear with us as the project continues!', CFSpeech|CFTimeout),
            Wait(8),
            Func(self.npcs[4].setChatAbsolute, 'Hmm, I\'m running out of things to say. I guess I\'ll start over.', CFSpeech|CFTimeout)
        )

    def unload(self):
        ToonHood.unload(self)
        del self.worker0Interval
        del self.worker1Interval
        del self.worker2Interval
        del self.directorSpeech

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.notify.debug('The sky is: %s' % self.sky)
        if not self.sky.getTag('sky') == 'Regular':
            self.endSpookySky()
        SkyUtil.startCloudSky(self)
