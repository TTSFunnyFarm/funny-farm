from toontown.toon import Toon, ToonDNA, ToonHead
from direct.showbase.DirectObject import DirectObject
from direct.directnotify import DirectNotifyGlobal

class ProtoGame(DirectObject):
    notify = directNotify.newCategory('ProtoGame')
    notify.setInfo(True)

    def __init__(self):
        self.preload()
        dna = ToonDNA.ToonDNA()
        dna.newToonRandom()
        self.toon = Toon.Toon()
        self.toon.setDNA(dna)
        self.toon.useLOD(1000)
        self.toon.startBlink()
        self.toon.startLookAround()
        self.toon.reparentTo(render)
        self.toon.loop('neutral')

    def preload(self):
        self.notify.info('Preloading things...')
        Toon.loadModels()
        Toon.compileGlobalAnimList()
        Toon.loadDialog()
        ToonHead.preloadToonHeads()
