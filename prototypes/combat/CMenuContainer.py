from direct.gui.DirectGui import *
from . import CMenu, GagWheel
from .CMenuGlobals import *
class CMenuContainer(DirectFrame):
    def __init__(self, battle):
        DirectFrame.__init__(self, parent=aspect2d, relief=None)
        self.__nodes = [CMenu.CMenu(self, battle), GagWheel.GagWheel(self)]
        self.currentNode = None
        self.showNode(CMENU)

    def showNode(self, menu):
        if self.currentNode:
            self.currentNode.reparentTo(hidden)
        menu = self.__nodes[menu]
        self.currentNode = menu
        menu.reparentTo(self)
