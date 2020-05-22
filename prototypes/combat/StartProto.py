from . import ProtoBase
from direct.directnotify import DirectNotifyGlobal
import builtins
from panda3d.core import *
loadPrcFile("config/proto.prc")

game = ProtoBase.ProtoBase()
game.run()
