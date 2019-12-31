from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from toontown.leveleditor import ExternalPanel
import libpandadna as LPD
import wx
loadPrcFile("config/level_editor.prc")

vfs = VirtualFileSystem.getGlobalPtr()
dna_path = config.GetString('dna-path')
mounts = ConfigVariableList('vfs-mount')
print(mounts)
for mount in mounts:
    mountfile, mountpoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountfile), Filename(mountpoint), 0)

base = ShowBase()
base.dna_storage = LPD.DNAStorage()
storage_files = ['storage_TT_sz.dna', 'storage_TT.dna', 'storage.dna', 'storage_town.dna', 'storage_TT_town.dna', 'storage_OZ_sz.dna', 'storage_DG.dna', 'storage_DG_town.dna', 'storage_FF.dna']
for storage in storage_files:
    LPD.loadDNAFile(base.dna_storage, dna_path + storage)
dna = LPD.loadDNAFile(base.dna_storage, dna_path + 'funny_farm_1100.dna')
test = NodePath(dna)
test.reparentTo(render)
base.oobe()
base.setFrameRateMeter(True)
base.camera.setPos(0, -50, 0)
app = wx.App()
base.panel = ExternalPanel.ExternalPanel(None, title='hi')
base.panel.daemon = True
base.panel.start()
#base.panel.show()
render.analyze()
base.run()
