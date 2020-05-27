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

class GagWheel(DirectFrame):
    def __init__(self):
        DirectFrame.__init__(self, relief=None)
        bg = CreateCircle()
        matGui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        self.bg = bg
        self.bg.reparentTo(self)
        self.trackLabel = DirectLabel(parent=self, relief=None, pos=(0, 0, 0), text='', text_scale=0.12, text_fg=Vec4(1, 1, 1, 1), text_align=TextNode.ACenter, text_font=FunnyFarmGlobals.getMinnieFont(), text_shadow=(0, 0, 0, 1))
        self.rightArrow = DirectButton(parent=self, relief=None, image=(matGui.find('**/tt_t_gui_mat_nextUp'), matGui.find('**/tt_t_gui_mat_nextDown'), matGui.find('**/tt_t_gui_mat_nextUp'), matGui.find('**/tt_t_gui_mat_nextDisabled')), pos=(-0.05, 0, 0.025), image_scale=(0.18, 0.18, 0.18), image1_scale=(0.21, 0.21, 0.21), image2_scale=(0.21, 0.21, 0.21), image3_scale=(0.18, 0.18, 0.18), command=self.__changeTrack, extraArgs=[1])
        self.leftArrow = DirectButton(parent=self, relief=None, image=(matGui.find('**/tt_t_gui_mat_nextUp'), matGui.find('**/tt_t_gui_mat_nextDown'), matGui.find('**/tt_t_gui_mat_nextUp'), matGui.find('**/tt_t_gui_mat_nextDisabled')), pos=(0.05, 0, 0.025), image_scale=(-0.18, 0.18, 0.18), image1_scale=(-0.21, 0.21, 0.21), image2_scale=(-0.21, 0.21, 0.21), image3_scale=(-0.18, 0.18, 0.18), command=self.__changeTrack, extraArgs= [-1])
        invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        self.invModels = []
        self.gagButtons = []
        for gagTrack in range(len(ToontownBattleGlobals.AvPropsNew)):
            itemList = []
            for item in range(len(ToontownBattleGlobals.AvPropsNew[gagTrack])):
                itemList.append(invModel.find('**/' + ToontownBattleGlobals.AvPropsNew[gagTrack][item]))

            self.invModels.append(itemList)
        invModel.removeNode()
        self.setTrack(1)

    def __changeTrack(self, delta):
        self.setTrack((self.track + delta) % 7)

    def setTrack(self, track):
        for button in self.gagButtons:
            button.removeNode()
            del button
        self.track = track
        rads = deg2Rad(360)
        trackLen = len(ToontownBattleGlobals.AvPropsNew[track])
        for i in range(trackLen + 1):
            gagModel = self.invModels[track][i - 1]
            a = rads * i / trackLen + 1
            y = math.sin(a) * 0.4
            x = math.cos(a) * 0.4
            button = DirectButton(parent=self, relief=None, image_pos=(x,0,y), image=gagModel, image_scale=(1,1,1))
            button.id = i
            self.gagButtons.append(button)
        self.bg.setColor(Vec4(*ToontownBattleGlobals.TrackColors[track], 0.9))
        self.trackLabel['text'] = TTLocalizer.BattleGlobalTracks[track]
        self.leftArrow.setX(-0.5)
        self.rightArrow.setX(0.5)
