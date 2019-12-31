from panda3d.core import *
import libpandadna as LPD
from direct.showbase.DirectObject import DirectObject
import wx
class LevelEditor(DirectObject):
    def __init__(self):
        self.dna_path = config.GetString('dna-path')
        base.geom = None
        storage_files = ['storage_TT_sz.dna', 'storage_TT.dna', 'storage.dna', 'storage_town.dna', 'storage_TT_town.dna', 'storage_OZ_sz.dna', 'storage_DG.dna', 'storage_DG_town.dna', 'storage_FF.dna']
        for storage in storage_files:
            LPD.loadDNAFile(base.dna_storage, self.dna_path + storage)
        self.accept('load-dna', self.loadDNA)

    def loadDNA(self, file):
        if base.geom:
            base.geom.removeNode()
        dna = LPD.loadDNAFile(base.dna_storage, Filename.fromOsSpecific(file))
        print(dna)
        base.geom = NodePath(dna)
        base.geom.reparentTo(render)
        return base.geom
