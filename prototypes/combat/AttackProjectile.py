from panda3d.core import *
from toontown.battle import BattleParticles, SuitBattleGlobals, BattleProps
from toontown.toonbase import ToontownGlobals

class AttackProjectile(NodePath):
    def __init__(self, propName):
        NodePath.__init__(self)
        self.assign(BattleProps.globalPropPool.getProp(propName))
        self.collNode = CollisionNode('AttackProjectile')
        bounds = self.getBounds()
        center = bounds.getCenter()
        sphere = CollisionSphere(center.getPos(), bounds.getRadius())
        sphere.setTangible(0)
        self.collNode.addSolid(sphere)
        self.collNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.attachNewNode(self.collNode)

    def setDamage(self, dmg):
        self.collNode.setTag('damage', str(dmg))
