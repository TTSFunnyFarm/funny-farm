from panda3d.core import *
import libpandadna as LPD
from direct.showbase.DirectObject import DirectObject
from toontown.leveleditor import ExternalPanel
from direct.gui.OnscreenText import OnscreenText
from toontown.toonbase import TTLocalizer
import wx
print(dir(LPD))
class LevelEditor(DirectObject):
    def __init__(self):
        ImpressBT = loader.loadFont(TTLocalizer.ToonFont)
        self.dna_path = config.GetString('dna-path')
        base.geom = None
        self.selected = None
        self.hpr = False
        self.DNAData = None
        self.info = OnscreenText(text = '', pos = (-1, -0.7), scale = 0.06, bg = (1,1,1,1), font = ImpressBT)
        app = wx.App()
        pnl = ExternalPanel.ExternalPanel()
        pnl.createPanel()
        pnl.Show()
        #app.MainLoop()
        storage_files = ['storage_TT_sz.dna', 'storage_TT.dna', 'storage.dna', 'storage_town.dna', 'storage_TT_town.dna', 'storage_OZ_sz.dna', 'storage_DG.dna', 'storage_DG_town.dna', 'storage_FF.dna']
        for storage in storage_files:
            LPD.loadDNAFile(base.dna_storage, self.dna_path + storage)
        self.accept('load-dna', self.loadDNA)
        self.accept('save-dna', self.saveDNA)
        self.accept('arrow_left', self.moveObj, [-0.5, 0, 0])
        self.accept('arrow_right', self.moveObj, [0.5, 0, 0])
        self.accept('arrow_up', self.moveObj, [0, 0.5, 0])
        self.accept('arrow_down', self.moveObj, [0, -0.5, 0])
        self.accept('arrow_left-repeat', self.moveObj, [-3, 0, 0])
        self.accept('arrow_right-repeat', self.moveObj, [3, 0, 0])
        self.accept('arrow_up-repeat', self.moveObj, [0, 3, 0])
        self.accept('arrow_down-repeat', self.moveObj, [0, -3, 0])
        self.accept('w', self.moveObj, [0, 0, 0.5])
        self.accept('w-repeat', self.moveObj, [0, 0, 3])
        self.accept('s', self.moveObj, [0, 0, -0.5])
        self.accept('s-repeat', self.moveObj, [0, 0, -3])
        self.accept('mouse2', self.toggleHpr)
        #self.accept('oobe-down', self.printt)

    def moveObj(self, x, y, z):
        obj = self.selected
        if obj and not self.hpr:
            obj.setX(obj.getX() + x)
            obj.setY(obj.getY() + y)
            obj.setZ(obj.getZ() + z)
        elif obj:
            obj.setH(obj.getH() + x)
            obj.setP(obj.getP() + y )
        self.updateText()

    def findDNANode(self, nodePath):
        if nodePath and base.dna_storage:
            return base.dna_storage.findNode('node')
        else:
            return None

    def loadDNA(self, file):
        if base.geom:
            base.geom.removeNode()
        dna = LPD.loadDNAFile(base.dna_storage, Filename.fromOsSpecific(file))
        if dna:
            base.root = LPD.loadDNAFileAI(base.dna_storage, Filename.fromOsSpecific(file))
            #print(base.root.traverse())
            base.geom = NodePath(dna)
            base.geom.reparentTo(render)
            node = self.findDNANode(base.geom)
            self.DNAData = LPD.DNAData('DNAData')
            self.DNAData.add(base.root)
            print(dir(base.root.getParent()), type(base.root))
            messenger.send('graph-refresh')
        return base.geom

    def saveDNA(self, file):
        if self.DNAData and base.geom:
            strm = MultiplexStream()
            strm.addFile(Filename(file))
            self.DNAData.writeDna(strm, True, 0)

    def updateText(self):
        if not self.selected:
            self.info.setText('Selected: None')
            return
        node = self.selected
        self.info.setText('Selected: %s\nX: %s Y: %s Z: %s\nH: %s P: %s R: %s \nHPR: %s' % (node.getName(), str(node.getX()), str(node.getY()), str(node.getZ()), str(node.getH()), str(node.getP()), str(node.getR()), str(self.hpr)))

    def selectItem(self, node):
        self.selected = node
        self.updateText()

    def toggleHpr(self):
        self.hpr = not self.hpr
        self.updateText()
