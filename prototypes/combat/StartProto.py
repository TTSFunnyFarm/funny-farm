from panda3d.core import *
loadPrcFile("config/proto.prc")
from . import ProtoBase
from direct.directnotify import DirectNotifyGlobal
import builtins
game = ProtoBase.ProtoBase()
game.run()
