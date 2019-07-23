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
        self.streets = {}
        self.fadeInDict = {}
        self.fadeOutDict = {}

    def enter(self):
        # Sets up listeners for when any avatar, local or suit, hits a new ground collision
        for street in self.streets.keys():
            if not street.find('**/street_*_collisions_*').isEmpty():
                self.accept('enter' + street.find('**/street_*_collisions_*').getName(), self.checkGroup, [self.streets.get(street)])
            elif not street.find('**/collision*floor*').isEmpty():
                self.accept('enter' + street.find('**/collision*floor*').getName(), self.checkGroup, [self.streets.get(street)])

    def exit(self):
        self.ignoreAll()

    def load(self):
        # Sets up all our lists and dictionaries
        a1 = Vec4(1, 1, 1, 1)
        a0 = Vec4(1, 1, 1, 0)
        self.visGroups = VisGroups.get(self.zoneId)
        for i in self.visGroups.keys():
            # Add all of the possible collision triggers (street parts) to a list
            for street in self.streetClass.geom.find('**/%d/streets' % i).getChildren():
                collision = street.find('**/street_*_collisions')
                if not collision.isEmpty():
                    collision.setName(collision.getName() + '_%d' % i)
                    self.streets[street] = i
                else:
                    # Probably a pond
                    collision = street.find('**/collision*floor*')
                    if not collision.isEmpty():
                        self.streets[street] = i
            # Add the visgroup to a dictionary of visgroups!
            groupNode = self.streetClass.geom.find('**/%d' % i)
            self.groups[i] = groupNode
            fadeDuration = 0.5
            self.fadeOutDict[groupNode] = Sequence(Func(groupNode.setTransparency, 1), LerpColorScaleInterval(groupNode, fadeDuration, a0, startColorScale=a1), Func(groupNode.clearColorScale), Func(groupNode.clearTransparency), Func(groupNode.hide), name='fadeZone-' + str(i), autoPause=1)
            self.fadeInDict[groupNode] = Sequence(Func(groupNode.show), Func(groupNode.setTransparency, 1), LerpColorScaleInterval(groupNode, fadeDuration, a1, startColorScale=a0), Func(groupNode.clearColorScale), Func(groupNode.clearTransparency), name='fadeZone-' + str(i), autoPause=1)

    def unload(self):
        del self.visGroups
        del self.groups
        del self.streets

    def setZoneId(self, zoneId):
        self.zoneId = zoneId

    def setCurrentGroup(self, currGroup):
        self.currGroup = currGroup
        self.update()

    def checkGroup(self, group, entry):
        # Triggered when either the player or a suit enters a new ground collision
        fromNP = entry.getFromNodePath().getParent()
        if fromNP == base.localAvatar.getGeomNode().getParent():
            # Local avatar entered a group.
            # First we want to update the building nametags with every new collision entry;
            # this is our workaround to a really expensive Task updating them every frame.
            self.updateNametags()
            if group == self.currGroup:
                # No point in updating anything else if we're still in the same group
                return
            # Otherwise, update our new location
            self.setCurrentGroup(group)
        else:
            # A suit entered a group
            self.updateSuit(group, entry)

    def update(self):
        # Updates the visgroups and the visibility of objects within the groups
        if not self.currGroup:
            return
        # Update the visible groups for the local avatar
        for i in self.visGroups.keys():
            group = self.groups[i]
            if i not in self.visGroups[self.currGroup]:
                if not group.isHidden():
                    self.fadeOutDict[group].start()
            else:
                if group.isHidden():
                    self.fadeInDict[group].start()
        # Update visible npcs
        for npc in self.streetClass.npcs:
            group = int(npc.origin.getParent().getName())
            if group != self.currGroup and self.currGroup not in [1106, 1110]:
                npc.hide()
                npc.removeActive()
            else:
                npc.show()
                npc.addActive()
        # Update visible suits
        for suit in self.streetClass.sp.activeSuits.values():
            # As of now, the only accurate way I know how to do this is by receiving the suit's "again" collision event pattern.
            # But since we don't know what street they're colliding with, we have to set up a listener on every street collision.
            # This takes a bit of processing, but it shouldn't cause any additional lag because the events are immediately ignored in the next method.
            for street in self.streets.keys():
                if not street.find('**/street_*_collisions_*').isEmpty():
                    self.accept('%d-again' % suit.doId + street.find('**/street_*_collisions_*').getName(), self.updateSuit, [self.streets.get(street)])
        # If shaders are enabled, trigger a shader update to fix potentially broken shaders
        if settings.get('waterShader', True):
            messenger.send('update-shader-settings')

    def updateSuit(self, group, entry):
        # Updates the visibility of a suit (from a collEntry), based on the avatar's location
        fromNP = entry.getFromNodePath().getParent()
        suit = None
        # Find the suit who triggered it
        for s in self.streetClass.sp.activeSuits.values():
            if fromNP == s.getGeomNode().getParent():
                suit = s
        # Update his visibility
        if suit != None:
            if group not in self.visGroups[self.currGroup]:
                suit.hide()
                suit.removeActive()
            else:
                suit.show()
                suit.addActive()
            # Ignore all the events we set up for the street collisions, if necessary
            for street in self.streets.keys():
                if not street.find('**/street_*_collisions_*').isEmpty():
                    self.ignore('%d-again' % suit.doId + street.find('**/street_*_collisions_*').getName())

    def updateNametags(self):
        # Updates the visibility of building nametags, based on the avatar's location
        for bldg in self.streetClass.buildings:
            if bldg.getBuildingNodePath().isEmpty():
                continue
            if bldg.getBuildingNodePath().isHidden():
                bldg.clearNametag()
                continue
            origin = bldg.getBuildingNodePath().find('**/*door_origin*')
            dist = (base.localAvatar.getPos(self.streetClass.geom) - origin.getPos(self.streetClass.geom)).length()
            if dist <= 80:
                bldg.setupNametag()
            else:
                bldg.clearNametag()
