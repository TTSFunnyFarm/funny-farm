from panda3d.core import *
import libpandadna as LPD
print(dir(LPD))
from direct.showbase.DirectObject import DirectObject
from toontown.leveleditor import ExternalPanel
from direct.gui.OnscreenText import OnscreenText
from direct.directtools.DirectGeometry import LineNodePath
from toontown.toonbase import TTLocalizer
import wx

# Colors used by all color menus
DEFAULT_COLORS = [
    Vec4(1, 1, 1, 1),
    Vec4(0.75, 0.75, 0.75, 1.0),
    Vec4(0.5, 0.5, 0.5, 1.0),
    Vec4(0.25, 0.25, 0.25, 1.0)
    ]

# The list of items with color attributes
COLOR_TYPES = ['wall_color', 'window_color', 'window_awning_color', 'sign_color',
                'door_color', 'door_awning_color', 'cornice_color', 'prop_color']

# The list of dna components maintained in the style attribute dictionary
DNA_TYPES = ['wall', 'window', 'sign', 'door_double', 'door_single', 'cornice', 'toon_landmark', 'prop', 'street']
BUILDING_TYPES = ['10_10', '20', '10_20', '20_10', '10_10_10',
                  '4_21', '3_22', '4_13_8', '3_13_9', '10',
                  '12_8', '13_9_8', '4_10_10',  '4_10', '4_20',
                  ]
BUILDING_HEIGHTS = [10, 14, 20, 24, 25, 30]
NUM_WALLS = [1, 2, 3]
LANDMARK_SPECIAL_TYPES = ['', 'hq', 'gagshop', 'clotheshop', 'petshop', 'kartshop']

OBJECT_SNAP_POINTS = {
    'street_5x20': [(Vec3(5.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_10x20': [(Vec3(10.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_20x20': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_30x20': [(Vec3(30.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_40x20': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_80x20': [(Vec3(80.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_5x40': [(Vec3(5.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_10x40': [(Vec3(10.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_20x40': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_20x40_15': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_30x40': [(Vec3(30.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_40x40': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_20x60': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_40x60': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_40x40_15': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_80x40': [(Vec3(80.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_angle_30': [(Vec3(0), Vec3(-30, 0, 0)), (Vec3(0), Vec3(0))],
    'street_angle_45': [(Vec3(0), Vec3(-45, 0, 0)), (Vec3(0), Vec3(0))],
    'street_angle_60': [(Vec3(0), Vec3(-60, 0, 0)), (Vec3(0), Vec3(0))],
    'street_inner_corner': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_outer_corner': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_full_corner': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_tight_corner': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_tight_corner_mirror': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_double_corner': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_curved_corner': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_curved_corner_15': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_t_intersection': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_y_intersection': [(Vec3(30.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_street_20x20': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_street_40x40': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_sidewalk_20x20': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_sidewalk_40x40': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_divided_transition': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_divided_40x70': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_divided_transition_15': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_divided_40x70_15': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_stairs_40x10x5': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_4way_intersection': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_incline_40x40x5': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_square_courtyard': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_courtyard_70': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_courtyard_70_exit': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_courtyard_90': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_courtyard_90_exit': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_courtyard_70_15': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_courtyard_70_15_exit': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_courtyard_90_15': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_courtyard_90_15_exit': [(Vec3(0.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_50_transition': [(Vec3(10.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_20x50': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_40x50': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_keyboard_10x40': [(Vec3(10.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_keyboard_20x40': [(Vec3(20.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_keyboard_40x40': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    'street_sunken_40x40': [(Vec3(40.0, 0, 0), Vec3(0)), (Vec3(0), Vec3(0))],
    }

def DNAGetClassType(dnaObject):
    return dnaObject.__class__.getClassType()

def DNAClassEqual(dnaObject, classType):
    return DNAGetClassType(dnaObject).eq(classType)

class LevelEditor(NodePath, DirectObject):

    def __init__(self):
        NodePath.__init__(self)
        # Become the new node path
        self.assign(hidden.attachNewNode('LevelEditor'))

        # Enable replaceSelected by default:
        self.replaceSelectedEnabled=1

        self.removeHookList=[self.landmarkBlockRemove]

        # Start block ID at 0 (it will be incremented before use (to 1)):
        self.landmarkBlock=0

        # Create ancillary objects
        # Style manager for keeping track of styles/colors
        #self.styleManager = LevelStyleManager(NEIGHBORHOODS, NEIGHBORHOOD_CODES)
        # Load neighborhood maps
        # self.createLevelMaps()
        # Marker for showing next insertion point
        self.createInsertionMarker()
        # Create level Editor Panel
        # self.panel = LevelEditorPanel(self)

        # Used to store whatever edges and points are loaded in the level
        self.edgeDict = {}
        self.np2EdgeDict = {}
        self.pointDict = {}
        self.point2edgeDict = {}
        self.cellDict = {}

        self.visitedPoints = []
        self.visitedEdges = []

        self.zoneLabels = []

        # Initialize LevelEditor variables DNAData, DNAToplevel, NPToplevel
        # DNAParent, NPParent, groupNum, lastAngle
        # Pass in the new toplevel group and don't clear out the old
        # toplevel group (since it doesn't exist yet)
        self.reset(fDeleteToplevel = 0, fCreateToplevel = 1)
        ImpressBT = loader.loadFont(TTLocalizer.ToonFont)
        self.dna_path = config.GetString('dna-path')
        base.geom = None
        self.selected = None
        self.hpr = False
        self.DNAData = None
        self.lsNode = None
        self.info = OnscreenText(text = '', pos = (-1, -0.7), scale = 0.06, bg = (1,1,1,1), font = ImpressBT)
        self.ls = LineSegs()
        self.ls.setThickness(2)
        self.ls.setColor(1, 1, 1)
        pnl = ExternalPanel.ExternalPanel()
        pnl.createPanel()
        pnl.Show()
        #app.MainLoop()
        #base.DNALoader = LPD.DNALoader()
        storage_files = ['storage_TT_sz.dna', 'storage_TT.dna', 'storage.dna', 'storage_town.dna', 'storage_TT_town.dna', 'storage_OZ_sz.dna', 'storage_DG.dna', 'storage_DG_town.dna', 'storage_FF.dna']
        for storage in storage_files:
            LPD.loadDNAFile(base.dna_storage, self.dna_path + storage)
        self.accept('load-dna', self.loadDNA)
        self.accept('save-dna', self.saveDNA)
        self.accept('arrow_left', self.moveObj, [-0.5, 0, 0])
        self.accept('arrow_right', self.moveObj, [0.5, 0, 0])
        self.accept('arrow_up', self.moveObj, [0, 0.5, 0])
        self.accept('arrow_down', self.moveObj, [0, -0.5, 0])
        self.accept('arrow_left-repeat', self.moveObj, [-3, 0, 0])
        self.accept('arrow_right-repeat', self.moveObj, [3, 0, 0])
        self.accept('arrow_up-repeat', self.moveObj, [0, 3, 0])
        self.accept('arrow_down-repeat', self.moveObj, [0, -3, 0])
        self.accept('w', self.moveObj, [0, 0, 0.5])
        self.accept('w-repeat', self.moveObj, [0, 0, 3])
        self.accept('s', self.moveObj, [0, 0, -0.5])
        self.accept('s-repeat', self.moveObj, [0, 0, -3])
        self.accept('mouse2', self.toggleHpr)
        #self.reset()
        #self.accept('oobe-down', self.printt)

    # DNA variables
    def getDNAData(self):
        return self.DNAData

    def getDNAToplevel(self):
        return self.DNAToplevel

    def getDNAParent(self):
        return self.DNAParent

    def getDNATarget(self):
        return self.DNATarget

    # Node Path variables
    def getNPToplevel(self):
        return self.NPToplevel

    def getNPParent(self):
        return self.NPParent

    # Count of groups added to level
    def setGroupNum(self, num):
        self.groupNum = num

    def getGroupNum(self):
        return self.groupNum

    # Angle of last object added to level
    def setLastAngle(self, angle):
        self.lastAngle = angle

    def getLastAngle(self):
        return self.lastAngle

    def createInsertionMarker(self):
        self.insertionMarker = LineNodePath(self)
        self.insertionMarker.lineNode.setName('insertionMarker')
        self.insertionMarker.setColor(VBase4(0.785, 0.785, 0.5, 1))
        self.insertionMarker.setThickness(1)
        self.insertionMarker.reset()
        self.insertionMarker.moveTo(-75, 0, 0)
        self.insertionMarker.drawTo(75, 0, 0)
        self.insertionMarker.moveTo(0, -75, 0)
        self.insertionMarker.drawTo(0, 75, 0)
        self.insertionMarker.moveTo(0, 0, -75)
        self.insertionMarker.drawTo(0, 0, 75)
        self.insertionMarker.create()

    def moveObj(self, x, y, z):
        obj = self.selected
        if obj and not self.hpr:
            obj.setX(obj.getX() + x)
            obj.setY(obj.getY() + y)
            obj.setZ(obj.getZ() + z)
        elif obj:
            obj.setH(obj.getH() + x)
            obj.setP(obj.getP() + y )
        self.updateLs()
        self.updateText()

    def refreshVisibility(self):
        # Get current visibility list for target
        targetInfo = self.visDict[self.target]
        visList = targetInfo[2]
        for key in self.visDict.keys():
            groupNP = self.visDict[key][0]
            if key in visList:
                groupNP.show()
                if key == self.target:
                    groupNP.setColor(0, 1, 0, 1)
                else:
                    groupNP.setColor(1, 0, 0, 1)
            else:
                if self.showMode.get() == 0:
                    groupNP.show()
                else:
                    groupNP.hide()
                groupNP.clearColor()

    def findDNANode(self, nodePath):
        if nodePath and base.dna_storage:
            return base.dna_storage.findNode(nodePath.getTag('DNACode'))
        else:
            return None

    def reset(self, fDeleteToplevel = 1, fCreateToplevel = 1,
              fUpdateExplorer = 1):
        """
        Reset level and re-initialize main class variables
        Pass in the new top level group
        """
        # Reset path markers
        self.resetPathMarkers()
        # Reset battle cell markers
        self.resetBattleCellMarkers()

        if fDeleteToplevel and self.DNAData:
            # First destroy existing scene-graph/DNA hierarchy
            self.deleteToplevel()

        # Clear DNASTORE
        base.dna_storage.resetDNAGroups()
        # Reset DNA VIS Groups
        base.dna_storage.resetDNAVisGroups()
        base.dna_storage.resetSuitPoints()
        base.dna_storage.resetBattleCells()

        # Create fresh DNA DATA
        self.DNAData = LPD.DNAData('level_data')
        print("AHH", self.DNAData)

        # Create new toplevel node path and DNA
        if fCreateToplevel:
            self.createToplevel(LPD.DNANode('level'))

        # Initialize variables
        # Reset grid
        #base.direct.grid.setPosHprScale(0, 0, 0, 0, 0, 0, 1, 1, 1)
        # The selected DNA Object/NodePath
        self.selectedDNARoot = None
        self.selectedNPRoot = None
        self.selectedSuitPoint = None
        self.lastLandmarkBuildingDNA = None
        self.showLandmarkBlockToggleGroup = None
        # Set active target (the subcomponent being modified)
        self.DNATarget = None
        self.DNATargetParent = None
        # Set count of groups added to level
        self.setGroupNum(0)
        # Heading angle of last object added to level
        self.setLastAngle(0.0)
        # Last wall and building modified using pie menus
        self.lastSign = None
        self.lastWall = None
        self.lastBuilding = None
        # Code of last selected object (for autopositionGrid)
        self.snapList = []
        # Last menu used
        self.activeMenu = None
        # For highlighting suit paths
        self.visitedPoints = []
        self.visitedEdges = []
        # Update scene graph explorer
        if fUpdateExplorer:
            messenger.send('graph-refresh')

    def deleteToplevel(self):
        # Destory old toplevel node path and DNA
        # First the toplevel DNA
        self.DNAData.remove(self.DNAToplevel)
        # Then the toplevel Node Path
        self.NPToplevel.removeNode()

    def createToplevel(self, dnaNode, nodePath = None):
        # When you create a new level, data is added to this node
        # When you load a DNA file, you replace this node with the new data
        self.DNAToplevel = dnaNode
        self.DNAData.add(self.DNAToplevel)
        if nodePath:
            # Node path given, use it
            self.NPToplevel = nodePath
            self.NPToplevel.reparentTo(self)
        else:
            # No node path given, traverse
            self.NPToplevel = self.DNAToplevel.traverse(self, base.dna_storage)
        # Update parent pointers
        self.DNAParent = self.DNAToplevel
        self.NPParent = self.NPToplevel
        self.VGParent = None
        # Add toplevel node path for suit points
        self.suitPointToplevel = self.NPToplevel.attachNewNode('suitPoints')

    def placeBattleCell(self):
        # Store the battle cell in the current vis group
        if not DNAClassEqual(self.DNAParent, DNA_VIS_GROUP):
            print('Error: DNAParent is not a dnaVisGroup. Did not add battle cell')
            return

        v = self.getGridSnapIntersectionPoint()
        mat = base.direct.grid.getMat(self.NPParent)
        absPos = Point3(mat.xformPoint(v))
        if (self.currentBattleCellType == '20w 20l'):
            cell = DNABattleCell(20, 20, absPos)
        elif (self.currentBattleCellType == '20w 30l'):
            cell = DNABattleCell(20, 30, absPos)
        elif (self.currentBattleCellType == '30w 20l'):
            cell = DNABattleCell(30, 20, absPos)
        elif (self.currentBattleCellType == '30w 30l'):
            cell = DNABattleCell(30, 30, absPos)
        # Store the battle cell in the storage
        base.dna_storage.storeBattleCell(cell)
        # Draw the battle cell
        marker = self.drawBattleCell(cell, self.NPParent)
        # Keep a handy dict of the visible markers
        self.cellDict[cell] = marker
        # Store the battle cell in the current vis group
        self.DNAParent.addBattleCell(cell)

    def createSuitPaths(self):
        # Points
        numPoints = base.dna_storage.getNumSuitPoints()
        for i in range(numPoints):
            point = base.dna_storage.getSuitPointAtIndex(i)
            marker = self.drawSuitPoint(point, point.getPos(), point.getPointType(), self.suitPointToplevel)
            self.pointDict[point] = marker

        # Edges
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        for visGroup in visGroups:
            np = visGroup[0]
            dnaVisGroup = visGroup[1]
            numSuitEdges = dnaVisGroup.getNumSuitEdges()
            for i in range(numSuitEdges):
                edge = dnaVisGroup.getSuitEdge(i)
                edgeLine = self.drawSuitEdge(edge, np)
                self.edgeDict[edge] = edgeLine
                self.np2EdgeDict[edgeLine.id()] = [edge, dnaVisGroup]
                # Store the edge on each point in case we move the point
                # we can update the edge
                for point in [edge.getStartPoint(), edge.getEndPoint()]:
                    if self.point2edgeDict.has_key(point):
                        self.point2edgeDict[point].append(edge)
                    else:
                        self.point2edgeDict[point] = [edge]

    def getSuitPointFromNodePath(self, nodePath):
        """
        Given a node path, attempt to find the point, nodePath pair
        in the pointDict. If it is there, return the point. If we
        cannot find it, return None.
        TODO: a reverse lookup pointDict would speed this up quite a bit
        """
        for point, marker in self.pointDict.items():
            if marker.eq(nodePath):
                return point
        return None

    def resetPathMarkers(self):
        for edge, edgeLine in self.edgeDict.items():
            if not edgeLine.isEmpty():
                edgeLine.reset()
                edgeLine.removeNode()
        self.edgeDict = {}
        self.np2EdgeDict = {}
        for point, marker in self.pointDict.items():
            if not marker.isEmpty():
                marker.removeNode()
        self.pointDict = {}

    def hideSuitPaths(self):
        for edge, edgeLine in self.edgeDict.items():
            edgeLine.hide()
        for point, marker in self.pointDict.items():
            marker.hide()

    def showSuitPaths(self):
        for edge, edgeLine in self.edgeDict.items():
            edgeLine.show()
        for point, marker in self.pointDict.items():
            marker.show()

    def createBattleCells(self):
        # Edges
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        for visGroup in visGroups:
            np = visGroup[0]
            dnaVisGroup = visGroup[1]
            numCells = dnaVisGroup.getNumBattleCells()
            for i in range(numCells):
                cell = dnaVisGroup.getBattleCell(i)
                marker = self.drawBattleCell(cell, np)
                self.cellDict[cell] = marker

    def resetBattleCellMarkers(self):
        for cell, marker in self.cellDict.items():
            if not marker.isEmpty():
                marker.remove()
        self.cellDict = {}

    def hideBattleCells(self):
        for cell, marker in self.cellDict.items():
            marker.hide()

    def showBattleCells(self):
        for cell, marker in self.cellDict.items():
            marker.show()

    def getBattleCellFromNodePath(self, nodePath):
        """
        Given a node path, attempt to find the battle cell, nodePath pair
        in the cellDict. If it is there, return the cell. If we
        cannot find it, return None.
        TODO: a reverse lookup cellDict would speed this up quite a bit
        """
        for cell, marker in self.cellDict.items():
            if marker.eq(nodePath):
                return cell
        return None

    def toggleZoneColors(self):
        if self.panel.zoneColor.get():
            self.colorZones()
        else:
            self.clearZoneColors()

    def colorZones(self):
        # Give each zone a random color to see them better
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        for visGroup in visGroups:
            np = visGroup[0]
            np.setColor(0.5 + random.random()/2.0,
                        0.5 + random.random()/2.0,
                        0.5 + random.random()/2.0)

    def clearZoneColors(self):
        # Clear random colors
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        for visGroup in visGroups:
            np = visGroup[0]
            np.clearColor()

    def labelZones(self):
        # Label each zone
        # First clear out old labels if any
        self.clearZoneLabels()
        visGroups = self.getDNAVisGroups(self.NPToplevel)
        from direct.gui import DirectGui
        for np, dna in visGroups:
            name = dna.getName()
            label = DirectGui.DirectLabel(text = name, parent = np.getParent(), relief = None, scale = 3)
            label.setBillboardPointEye(0)
            center = np.getBounds().getCenter()
            label.setPos(center[0], center[1], .1)
            self.zoneLabels.append(label)

    def clearZoneLabels(self):
        for label in self.zoneLabels:
            label.removeNode()
        self.zoneLabels = []

    def getBlockFromName(self, name):
        block = name[2:name.find(':')]
        return block

    def addToLandmarkBlock(self):
        dnaRoot = self.selectedDNARoot
        if dnaRoot and self.lastLandmarkBuildingDNA:
            if DNAClassEqual(dnaRoot, DNA_FLAT_BUILDING):
                n = dnaRoot.getName()
                n = n[n.find(':'):]
                block = self.lastLandmarkBuildingDNA.getName()
                block = block[2:block.find(':')]
                dnaRoot.setName('tb'+block+n)
                self.replaceSelected()
                # If we're highlighting the landmark blocks:
                if self.showLandmarkBlockToggleGroup:
                    # then highlight this one:
                    np = self.selectedNPRoot
                    self.showLandmarkBlockToggleGroup.append(np)
                    np.setColor(1, 0, 0, 1)
        elif self.selectedSuitPoint and self.lastLandmarkBuildingDNA:
            block = self.lastLandmarkBuildingDNA.getName()
            block = block[2:block.find(':')]
            print ("associate point with building: " + str(block))
            self.selectedSuitPoint.setLandmarkBuildingIndex(int(block))
            marker = self.pointDict[self.selectedSuitPoint]
            marker.setColor(1, 0, 0, 1)
            marker.setScale(1.0)

    def findHighestLandmarkBlock(self, dnaRoot, npRoot):
        npc = npRoot.findAllMatches("**/*:toon_landmark_*")
        highest = 0
        for i in range(npc.getNumPaths()):
            path = npc.getPath(i)
            block = path.getName()
            block = int(block[2:block.find(':')])
            if (block > highest):
                highest=block
        # Make a list of flat building names, outside of the
        # recursive function:
        self.flatNames = ['random'] + BUILDING_TYPES
        self.flatNames = map(lambda n: n + '_DNARoot', self.flatNames)
        # Search/recurse the dna:
        newHighest = self.convertToLandmarkBlocks(highest, dnaRoot)
        # Get rid of the list of flat building names:
        self.flatNames = None

        needToTraverse = highest != newHighest
        return (newHighest, needToTraverse)

    def convertToLandmarkBlocks(self, block, dnaRoot):
        """
        Find all the buildings without landmark blocks and
        assign them one.
        """
        if dnaRoot.isEmpty():
            return block
        for i in range(dnaRoot.getNumChildren()):
            child = dnaRoot.at(i)
            if DNAClassEqual(child, DNA_LANDMARK_BUILDING):
                # Landmark buildings:
                name = child.getName()
                if name.find('toon_landmark_') == 0:
                    block = block + 1
                    child.setName('tb'+str(block)+':'+name)
            elif DNAClassEqual(child, DNA_FLAT_BUILDING):
                # Flat buildings:
                name = child.getName()
                if (name in self.flatNames):
                    child.setName('tb0:'+name)
            else:
                block = self.convertToLandmarkBlocks(block, child)
        return block

    def revertLandmarkBlock(self, block):
        """
        un-block flat buildings (set them to block zero).
        """
        npc = self.NPToplevel.findAllMatches("**/tb"+block+":*_DNARoot")
        for i in range(npc.getNumPaths()):
            nodePath = npc.getPath(i)
            name = nodePath.getName()
            if name[name.find(':'):][:15] != ':toon_landmark_':
                name = 'tb0' + name[name.find(':'):]
                dna = self.findDNANode(nodePath)
                dna.setName(name)
                nodePath = self.replace(nodePath, dna)
                # If we're highlighting the landmark blocks:
                if self.showLandmarkBlockToggleGroup:
                    # then highlight this one:
                    self.showLandmarkBlockToggleGroup.append(nodePath)
                    nodePath.setColor(0, 1, 0, 1)

    def landmarkBlockRemove(self, dna, nodePath):
        if dna:
            name = dna.getName()
            # Get the underscore index within the name:
            usIndex = name.find(':')
            if name[usIndex:][:15] == ':toon_landmark_':
                block = name[2:usIndex]
                self.lastLandmarkBuildingDNA = None
                self.revertLandmarkBlock(block)

    def loadDNA(self, file):
        #if base.geom:
            #base.geom.removeNode()
        self.reset(fDeleteToplevel = 1, fCreateToplevel = 0, fUpdateExplorer = 0)
        node = LPD.loadDNAFile(base.dna_storage, Filename.fromOsSpecific(file))
        print(node)
        newNPToplevel = None
        if node.getNumParents() == 1:
            # If the node already has a parent arc when it's loaded, we must
            # be using the level editor and we want to preserve that arc.
            newNPToplevel = NodePath(node)
            newNPToplevel.reparentTo(hidden)
        else:
            # Otherwise, we should create a new arc for the node.
            newNPToplevel = hidden.attachNewNode(node)

        # Make sure the topmost file DNA object gets put under DNARoot
        newDNAToplevel = self.findDNANode(newNPToplevel)

        # reset the landmark block number:
        (self.landmarkBlock, needTraverse) = self.findHighestLandmarkBlock(newDNAToplevel, newNPToplevel)

        # Update toplevel variables
        if needTraverse:
            self.createToplevel(newDNAToplevel)
        else:
            self.createToplevel(newDNAToplevel, newNPToplevel)
        messenger.send('graph-refresh')
        self.refreshVisibility()

    def saveDNA(self, file):
        if self.DNAData and base.geom:
            strm = MultiplexStream()
            strm.addFile(Filename(file))
            self.DNAData.writeDna(strm, True, 0)

    def updateLs(self):
        if not self.selected:
            return
        self.ls.reset()
        if self.lsNode:
            self.lsNode.removeNode()
        min, max = self.selected.getTightBounds()
        self.ls.moveTo(min)
        self.ls.drawTo(min.x, min.y, max.z)
        self.ls.moveTo(min)
        self.ls.drawTo(max.x, min.y, min.z)
        self.ls.drawTo(max.x, min.y, max.z)
        self.ls.moveTo(max.x, min.y, min.z)
        self.ls.drawTo(max.x, max.y, min.z)
        self.ls.drawTo(max.x, max.y, max.z)
        self.ls.moveTo(max.x, max.y, min.z)
        self.ls.drawTo(min.x, max.y, min.z)
        self.ls.drawTo(min.x, max.y, max.z)
        self.ls.moveTo(min.x, max.y, min.z)
        self.ls.drawTo(min)
        self.ls.moveTo(min.x, min.y, max.z)
        self.ls.drawTo(max.x, min.y, max.z)
        self.ls.drawTo(max.x, max.y, max.z)
        self.ls.drawTo(min.x, max.y, max.z)
        self.ls.drawTo(min.x, min.y, max.z)
        self.lsNode = render.attachNewNode(self.ls.create(False))

    def updateText(self):
        if not self.selected:
            self.info.setText('Selected: None')
            return
        node = self.selected
        self.info.setText('Selected: %s\nX: %s Y: %s Z: %s\nH: %s P: %s R: %s \nHPR: %s' % (node.getName(), str(node.getX()), str(node.getY()), str(node.getZ()), str(node.getH()), str(node.getP()), str(node.getR()), str(self.hpr)))

    def selectItem(self, node):
        self.selected = node
        self.updateLs()
        self.updateText()

    def toggleHpr(self):
        self.hpr = not self.hpr
        self.updateText()
