from toontown.toon import LocalToon, Toon, ToonDNA, ToonHead, LaffMeter
from toontown.suit import BattleSuit, SuitDNA
from . import BattleManager
from direct.showbase.DirectObject import DirectObject
from direct.directnotify import DirectNotifyGlobal
import random

class ProtoGame(DirectObject):
    notify = directNotify.newCategory('ProtoGame')
    notify.setInfo(True)

    def __init__(self):
        self.preload()
        dna = ToonDNA.ToonDNA()
        dna.newToonRandom()
        music = base.loader.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.ogg')
        musicMgr.playMusic(music, looping=1)
        self.geom = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_crg_penthouse')
        self.geom.reparentTo(render)
        self.toon = LocalToon.LocalToon()
        self.toon.setDNA(dna)
        self.toon.useLOD(1000)
        self.toon.startBlink()
        self.toon.reparentTo(render)
        self.toon.loop('neutral')
        self.toon.setPos(0, -5, 0.025)
        self.laffMeter = LaffMeter.LaffMeter(self.toon.style, self.toon.hp, self.toon.maxHp)
        self.laffMeter.setAvatar(self.toon)
        self.laffMeter.setScale(0.075)
        self.laffMeter.reparentTo(base.a2dBottomLeft)
        if self.toon.style.getAnimal() == 'monkey':
            self.laffMeter.setPos(0.153, 0.0, 0.13)
        else:
            self.laffMeter.setPos(0.133, 0.0, 0.13)
        self.laffMeter.start()
        self.suit = BattleSuit.BattleSuit()
        dna = SuitDNA.SuitDNA()
        type = random.randint(1, 3)
        tier = type
        type += 8 * random.randint(0, 3)
        type -= 1
        name = SuitDNA.suitHeadTypes[type]
        dna.newSuit(name)
        self.suit.setDNA(dna)
        self.suit.setLevel(random.randint(0, 3))
        self.suit.reparentTo(render)
        self.suit.loop('neutral')
        self.suit.setPos(0, 5, 0.025)
        self.suit.setH(180)
        self.suit.initializeBodyCollisions('suit')
        self.suit.addActive()
        self.battleMgr = BattleManager.BattleManager([self.toon], [self.suit])

    def preload(self):
        self.notify.info('Preloading things...')
        Toon.loadModels()
        Toon.compileGlobalAnimList()
        Toon.loadDialog()
        ToonHead.preloadToonHeads()
