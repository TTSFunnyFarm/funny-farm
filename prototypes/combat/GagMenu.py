from direct.gui.DirectGui import *
from panda3d.egg import *
from panda3d.core import *
from toontown.toonbase import ToontownBattleGlobals, TTLocalizer, FunnyFarmGlobals
import math

def CreateCircle(scale = 0.5, color = Vec4(*ToontownBattleGlobals.TrackColors[1], 0.9), angleDegrees = 360, numSteps = 128):
    data = EggData()

    vp = EggVertexPool('fan')
    data.addChild(vp)

    poly = EggPolygon()
    poly.setColor(color)
    data.addChild(poly)

    v = EggVertex()
    v.setPos(Point3D(0, 0, 0))
    poly.addVertex(vp.addVertex(v))

    angleRadians = deg2Rad(angleDegrees)

    for i in range(numSteps + 1):
        a = angleRadians * i / numSteps
        y = math.sin(a) * scale
        x = math.cos(a) * scale

        v = EggVertex()
        v.setPos(Point3D(x, 0, y))
        poly.addVertex(vp.addVertex(v))
    node = loadEggData(data)
    return NodePath(node)

class GagMenu(DirectFrame):
    def __init__(self):
        DirectFrame.__init__(self, relief=None)
        bg = CreateCircle()
        self.bg = bg
        self.bg.reparentTo(self)
        self.trackLabel = DirectLabel(parent=self, relief=None, pos=(0, 0, 0), text='', text_scale=0.12, text_fg=Vec4(1, 1, 1, 1), text_align=TextNode.ACenter, text_font=FunnyFarmGlobals.getMinnieFont(), text_shadow=(0, 0, 0, 1))
        invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        self.invModels = []
        for gagTrack in range(len(ToontownBattleGlobals.AvPropsNew)):
            itemList = []
            for item in range(len(ToontownBattleGlobals.AvPropsNew[gagTrack])):
                itemList.append(invModel.find('**/' + ToontownBattleGlobals.AvPropsNew[gagTrack][item]))

            self.invModels.append(itemList)
        invModel.removeNode()
        self.setTrack(1)

    def setTrack(self, track):
        self.track = track
        rads = deg2Rad(360)
        trackLen = len(ToontownBattleGlobals.AvPropsNew[track])
        for i in range(trackLen):
            gagModel = self.invModels[track][i]
            gagModel.reparentTo(self)
            gagModel.setScale(1)
            a = rads * i / trackLen - 1
            y = math.sin(a) * 0.4
            x = math.cos(a) * 0.4
            gagModel.setPos(x, 0, y)
        self.bg.setColor(Vec4(*ToontownBattleGlobals.TrackColors[1], 0.9))
        self.trackLabel['text'] = TTLocalizer.BattleGlobalTracks[track]
