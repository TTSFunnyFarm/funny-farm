from direct.gui.DirectGui import *
from . import CMenu
CMENU = 0
class CMenuContainer(DirectFrame):
    def __init__(self):
        DirectFrame.__init__(self, relief=None)
        self.__nodes = [CMenu.CMenu()]
        self.currentNode = None
        self.showNode(CMENU)

    def showNode(self, menu):
        if self.currentNode:
            self.currentNode.reparentTo(hidden)
        self.__nodes[menu].reparentTo(aspect2d)
