from panda3d.core import *
import libpandadna as LPD
from direct.showbase.DirectObject import DirectObject
from toontown.leveleditor import ExternalPanel
from direct.gui.OnscreenText import OnscreenText
from toontown.toonbase import TTLocalizer
import wx
class LevelEditor(DirectObject):
    def __init__(self):
        ImpressBT = loader.loadFont(TTLocalizer.ToonFont)
        self.dna_path = config.GetString('dna-path')
        base.geom = None
        self.selected = None
        self.info = OnscreenText(text = '', pos = (-1, -0.8), scale = 0.06, bg = (1,1,1,1), font = ImpressBT)
        app = wx.App()
        pnl = ExternalPanel.ExternalPanel()
        pnl.createPanel()
        pnl.Show()
        #app.MainLoop()
        storage_files = ['storage_TT_sz.dna', 'storage_TT.dna', 'storage.dna', 'storage_town.dna', 'storage_TT_town.dna', 'storage_OZ_sz.dna', 'storage_DG.dna', 'storage_DG_town.dna', 'storage_FF.dna']
        for storage in storage_files:
            LPD.loadDNAFile(base.dna_storage, self.dna_path + storage)
        self.accept('load-dna', self.loadDNA)

    def loadDNA(self, file):
        if base.geom:
            base.geom.removeNode()
        dna = LPD.loadDNAFile(base.dna_storage, Filename.fromOsSpecific(file))
        if dna:
            base.geom = NodePath(dna)
            base.geom.reparentTo(render)
            messenger.send('graph-refresh')
        return base.geom

    def selectItem(self, node):
        self.selected = node
        self.info.setText('Selected: %s\nX: %s Y: %s Z: %s\nH: %s P: %s R: %s' % (node.getName(), str(node.getX()), str(node.getY()), str(node.getZ()), str(node.getH()), str(node.getP()), str(node.getR())))
