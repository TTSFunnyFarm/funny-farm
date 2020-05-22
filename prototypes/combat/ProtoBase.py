from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from toontown.misc import Injector

class ProtoBase(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        from prototypes.combat import ProtoGame
        CullBinManager.getGlobalPtr().addBin('shadow', CullBinManager.BTFixed, 15)
        CullBinManager.getGlobalPtr().addBin('ground', CullBinManager.BTFixed, 14)
        injector = Injector.Injector()
        injector.daemon = True
        injector.start()
        self.game = ProtoGame.ProtoGame()
        #self.game.start()
