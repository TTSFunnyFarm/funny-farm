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
        self.accept('arrow_left', self.moveObj, [-0.5, 0, 0])
        self.accept('arrow_right', self.moveObj, [0.5, 0, 0])
        self.accept('arrow_up', self.moveObj, [0, 0.5, 0])
        self.accept('arrow_down', self.moveObj, [0, -0.5, 0])
        self.accept('arrow_left-repeat', self.moveObj, [-3, 0, 0])
        self.accept('arrow_right-repeat', self.moveObj, [3, 0, 0])
        self.accept('arrow_up-repeat', self.moveObj, [0, 3, 0])
        self.accept('arrow_down-repeat', self.moveObj, [0, -3, 0])
        #self.accept('oobe-down', self.printt)

    def moveObj(self, x, y, z):
        if self.selected:
            obj = self.selected
            obj.setX(obj.getX() + x)
            obj.setY(obj.getY() + y)
            obj.setZ(obj.getZ() + z)
            self.updateText()


    def loadDNA(self, file):
        if base.geom:
            base.geom.removeNode()
        dna = LPD.loadDNAFile(base.dna_storage, Filename.fromOsSpecific(file))
        if dna:
            base.geom = NodePath(dna)
            base.geom.reparentTo(render)
            messenger.send('graph-refresh')
        return base.geom

    def updateText(self):
        self.info.setText('Selected: %s\nX: %s Y: %s Z: %s\nH: %s P: %s R: %s' % (node.getName(), str(node.getX()), str(node.getY()), str(node.getZ()), str(node.getH()), str(node.getP()), str(node.getR())))

    def selectItem(self, node):
        self.selected = node
        self.updateText()
