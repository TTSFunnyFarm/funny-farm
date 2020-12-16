from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.town.VisGroups import VisGroups

class TownLoader(DirectObject):

    def __init__(self, streetClass):
        self.streetClass = streetClass
        self.zoneId = None
        self.visGroups = None
        self.currGroup = None
        self.groups = {}
        self.fadeInDict = {}
        self.fadeOutDict = {}

    def enter(self):
        # Sets up listeners for when any avatar, local or suit, hits a new ground collision
        for i in self.visGroups.keys():
            streetGroup = self.streetClass.geom.find('**/%d/streets;+s' % i)
            for street in streetGroup.getChildren():
                if not street.find('**/street_*_collisions_*').isEmpty():
                    self.accept('enter' + street.find('**/street_*_collisions_*').getName(), self.checkGroup, [i])
                elif not street.find('**/collision*floor*').isEmpty():
                    self.accept('enter' + street.find('**/collision*floor*').getName(), self.checkGroup, [i])

    def exit(self):
        self.ignoreAll()

    def load(self):
        # Sets up all our lists and dictionaries
        a1 = Vec4(1, 1, 1, 1)
        a0 = Vec4(1, 1, 1, 0)
        self.visGroups = VisGroups.get(self.zoneId)
        for i in self.visGroups.keys():
            # Update collision names (TODO check if this is even necessary)
            for street in self.streetClass.geom.find('**/%d/streets' % i).getChildren():
                collision = street.find('**/street_*_collisions')
                if collision.isEmpty():
                    collision = street.find('**/collision*floor*')
                if not collision.isEmpty():
                    collision.setName(collision.getName() + '_%d' % i)
            # Add the visgroup to a dictionary of visgroups!
            groupNode = self.streetClass.geom.find('**/%d' % i)
            self.groups[i] = groupNode
            fadeDuration = 0.5
            self.fadeOutDict[groupNode] = Sequence(Func(groupNode.setTransparency, 1), LerpColorScaleInterval(groupNode, fadeDuration, a0, startColorScale=a1), Func(groupNode.clearColorScale), Func(groupNode.clearTransparency), Func(groupNode.stash), name='fadeZone-' + str(i), autoPause=1)
            self.fadeInDict[groupNode] = Sequence(Func(groupNode.unstash), Func(groupNode.setTransparency, 1), LerpColorScaleInterval(groupNode, fadeDuration, a1, startColorScale=a0), Func(groupNode.clearColorScale), Func(groupNode.clearTransparency), name='fadeZone-' + str(i), autoPause=1)

    def unload(self):
        del self.visGroups
        del self.groups
        del self.fadeInDict
        del self.fadeOutDict

    def setZoneId(self, zoneId):
        self.zoneId = zoneId

    def setCurrentGroup(self, currGroup):
        self.currGroup = currGroup
        self.update()

    def checkGroup(self, group, entry):
        fromNP = entry.getFromNodePath().getParent()
        if fromNP == base.localAvatar.getGeomNode().getParent():
            # Local avatar entered a group. Update everything.
            self.updateBuildings()
            for suit in self.streetClass.sp.activeSuits.values():
                self.updateSuit(suit)
            if group == self.currGroup:
                return
            self.setCurrentGroup(group)
        else:
            # A suit entered a group. Update his nametag.
            suit = None
            for s in self.streetClass.sp.activeSuits.values():
                if fromNP == s.getGeomNode().getParent():
                    suit = s
                    break
            self.updateSuit(suit)

    def update(self):
        if not self.currGroup:
            return
        # Update visible groups for the local avatar.
        for i in self.visGroups.keys():
            group = self.groups[i]
            if i not in self.visGroups[self.currGroup]:
                if not group.isStashed():
                    self.fadeOutDict[group].start()
            else:
                if group.isStashed():
                    self.fadeInDict[group].start()
        # Update npc nametags.
        self.updateNPCs()
        # If shaders are enabled, trigger a shader update to fix potentially broken shaders
        if settings.get('waterShader', True):
            messenger.send('update-shader-settings')
    
    def updateNPCs(self):
        for npc in self.streetClass.npcs:
            group = int(npc.origin.getParent().getName())
            if group in self.visGroups[self.currGroup]:
                npc.addActive()
            else:
                npc.removeActive()

    def updateBuildings(self):
        for bldg in self.streetClass.buildings:
            if bldg.getBuildingNodePath().isEmpty():
                continue
            if bldg.getBuildingNodePath().isStashed():
                bldg.clearNametag()
                continue
            origin = bldg.getBuildingNodePath().find('**/*door_origin*')
            dist = (base.localAvatar.getPos(self.streetClass.geom) - origin.getPos(self.streetClass.geom)).length()
            if dist <= 80:
                bldg.setupNametag()
            else:
                bldg.clearNametag()
    
    def updateSuit(self, suit):
        if suit.isStashed():
            return
        dist = (base.localAvatar.getPos(self.streetClass.geom) - suit.getPos(self.streetClass.geom)).length()
        if dist <= 200:
            suit.addActive()
        else:
            suit.removeActive()
