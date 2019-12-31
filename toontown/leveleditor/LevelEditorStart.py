from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from toontown.leveleditor import LevelEditor
from toontown.leveleditor import ExternalPanel
import libpandadna as LPD
import wx
loadPrcFile("config/level_editor.prc")

vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
print(mounts)
for mount in mounts:
    mountfile, mountpoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountfile), Filename(mountpoint), 0)

base = ShowBase()
base.dna_storage = LPD.DNAStorage()
base.lvlEditor = LevelEditor.LevelEditor()
app = wx.App()
#base.panel.daemon = True
base.oobe()
base.setFrameRateMeter(True)
base.camera.setPos(0, -50, 0)
base.camLens.setNear(1.0)
base.camLens.setFar(3000)
#base.panel.show()
base.run()
