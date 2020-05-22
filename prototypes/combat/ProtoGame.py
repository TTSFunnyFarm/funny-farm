from toontown.toon import LocalToon, Toon, ToonDNA, ToonHead, LaffMeter
from direct.showbase.DirectObject import DirectObject
from direct.directnotify import DirectNotifyGlobal

class ProtoGame(DirectObject):
    notify = directNotify.newCategory('ProtoGame')
    notify.setInfo(True)

    def __init__(self):
        self.preload()
        dna = ToonDNA.ToonDNA()
        dna.newToonRandom()
        self.geom = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_crg_penthouse')
        self.geom.reparentTo(render)
        self.toon = LocalToon.LocalToon()
        self.toon.setDNA(dna)
        self.toon.useLOD(1000)
        self.toon.startBlink()
        self.toon.startLookAround()
        self.toon.reparentTo(render)
        self.toon.loop('neutral')
        self.laffMeter = LaffMeter.LaffMeter(self.toon.style, self.toon.hp, self.toon.maxHp)
        self.laffMeter.setAvatar(self.toon)
        self.laffMeter.setScale(0.075)
        self.laffMeter.reparentTo(base.a2dBottomLeft)
        if self.toon.style.getAnimal() == 'monkey':
            self.laffMeter.setPos(0.153, 0.0, 0.13)
        else:
            self.laffMeter.setPos(0.133, 0.0, 0.13)
        self.laffMeter.start()

    def preload(self):
        self.notify.info('Preloading things...')
        Toon.loadModels()
        Toon.compileGlobalAnimList()
        Toon.loadDialog()
        ToonHead.preloadToonHeads()
