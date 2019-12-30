from panda3d.core import *

cm = CardMaker('screenFader')
cm.setFrame(-1,1,-1,1)
node = NodePath('screenFader')
screenFader = node.attachNewNode(cm.generate())
screenFader.reparentTo(camera)
nearPlaneDist = base.camLens.getNear()
screenFader.setY(nearPlaneDist * 1.05)
screenFader.setColor(0,0,0,0.25)
screenFader.setTransparency(1)
screenFader.hide()

def FadeScreen(val):
    screenFader.show()
    screenFader.setColor(0,0,0,val)

def UnfadeScreen():
    screenFader.hide()

def GetExtra(dialog):
    if isinstance(dialog, list):
        return dialog[0], list(dialog[1:])
    else:
        return dialog
