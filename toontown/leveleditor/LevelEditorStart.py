from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
#from toontown.leveleditor.DNAParser import DNAParser
#from libtoontown import *
import libpandadna as LPD
print(dir(LPD))
dna_storage = LPD.DNAStorage()
path = 'resources/phase_14/dna/'

loadPrcFile("config/level_editor.prc")

vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
print(mounts)
for mount in mounts:
    mountfile, mountpoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountfile), Filename(mountpoint), 0)

base = ShowBase()
LPD.loadDNAFile(dna_storage, path + 'storage_TT_sz.dna')
LPD.loadDNAFile(dna_storage, path + 'storage_TT.dna')
LPD.loadDNAFile(dna_storage, path + 'storage.dna')
LPD.loadDNAFile(dna_storage, path + 'storage_town.dna')
LPD.loadDNAFile(dna_storage, path + 'storage_TT_town.dna')
dna = LPD.loadDNAFile(dna_storage, path + 'toontown_central_2100.dna')
print(dir(dna))
test = NodePath(dna)
for child in test.getChildren():
    print(child)
#test.attachNewNode(dna)
test.reparentTo(render)
#test.flattenMedium()
def fortnite(node):
    for n in node.getChildren():
        fortnite(n)
        print(n)
fortnite(test)
base.oobe()
base.setFrameRateMeter(True)
render.analyze()
base.run()
