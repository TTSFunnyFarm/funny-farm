from direct.gui.DirectGui import *
from panda3d.egg import *
from panda3d.core import *
import math

def CreateCircle(scale = 0.5, color = Point3(1.0, 0.0, 0.0), angleDegrees = 360, numSteps = 128):
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
