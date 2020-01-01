from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from toontown.leveleditor import LevelEditor
from toontown.leveleditor import ExternalPanel
from toontown.leveleditor import SelectManager
import libpandadna as LPD
import wx
loadPrcFile("config/level_editor.prc")

vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
for mount in mounts:
    mountfile, mountpoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountfile), Filename(mountpoint), 0)

base = ShowBase()
app = wx.App()
base.dna_storage = LPD.DNAStorage()
base.lvlEditor = LevelEditor.LevelEditor()
base.selectMgr = SelectManager.SelectManager()
base.oobe()
bt = base.buttonThrowers[0].node() # reverse rdb's code :^
bt.setSpecificFlag(1)
bt.setButtonDownEvent('')
bt.setButtonRepeatEvent('')
bt.setButtonUpEvent('')
base.mouseInterfaceNode.clearButton(KeyboardButton.shift())
mat = Mat4(camera.getMat())
mat.invertInPlace()
camera = base.oobeTrackball
camera.node().setMat(mat)
#base.panel.daemon = True
base.setFrameRateMeter(True)
base.camera.setPos(0, -50, 0)
base.camLens.setNear(1.0)
base.camLens.setFar(3000)
base.run()
