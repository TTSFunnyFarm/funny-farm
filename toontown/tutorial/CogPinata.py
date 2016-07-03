from pandac.PandaModules import *
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals

class CogPinata(Actor):

    def __init__(self, parent, id):
        Actor.__init__(self)
        self.parent = parent
        self.id = id
        self.active = False
        path = 'phase_13/models/parties/cogPinata_'
        self.model = path + 'actor'
        self.animDict = {
                'idle': path + 'idle_anim',
                'down': path + 'down_anim',
                'up': path + 'up_anim',
                'bodyHitBack': path + 'bodyHitBack_anim',
                'bodyHitFront': path + 'bodyHitFront_anim',
                'headHitBack': path + 'headHitBack_anim',
                'headHitFront': path + 'headHitFront_anim'
        }
        self.load()

    def load(self):
        self.root = NodePath('CogPinata-%d' % self.id)
        self.root.reparentTo(self.parent)

        self.loadModel(self.model)
        self.loadAnims(self.animDict)
        self.reparentTo(self.root)
        self.setBlend(frameBlend=True)

        self.head_locator = self.attachNewNode('temphead')
        self.bodyColl = CollisionTube(0, 0, 1, 0, 0, 5.75, 0.75)
        self.bodyColl.setTangible(1)
        self.bodyCollNode = CollisionNode('CogPinata-%d-Body-Collision' % self.id)
        self.bodyCollNode.addSolid(self.bodyColl)
        self.bodyCollNodePath = self.attachNewNode(self.bodyCollNode)
        self.headColl = CollisionTube(0, 0, 3, 0, 0, 3.0, 1.5)
        self.headColl.setTangible(1)
        self.headCollNode = CollisionNode('CogPinata-%d-Head-Collision' % self.id)
        self.headCollNode.addSolid(self.headColl)
        self.headCollNodePath = self.attachNewNode(self.headCollNode)
        self.arm1Coll = CollisionSphere(1.65, 0, 3.95, 1.0)
        self.arm1Coll.setTangible(1)
        self.arm1CollNode = CollisionNode('CogPinata-%d-Arm1-Collision' % self.id)
        self.arm1CollNode.addSolid(self.arm1Coll)
        self.arm1CollNodePath = self.attachNewNode(self.arm1CollNode)
        self.arm2Coll = CollisionSphere(-1.65, 0, 3.45, 1.0)
        self.arm2Coll.setTangible(1)
        self.arm2CollNode = CollisionNode('CogPinata-%d-Arm2-Collision' % self.id)
        self.arm2CollNode.addSolid(self.arm2Coll)
        self.arm2CollNodePath = self.attachNewNode(self.arm2CollNode)

        self.collisions = [self.bodyCollNodePath, self.headCollNodePath, self.arm1CollNodePath, self.arm2CollNodePath]
        for coll in self.collisions:
            coll.setTag('pieCode', str(self.id))
            coll.stash()

        self.hole = loader.loadModel('phase_13/models/parties/cogPinataHole')
        self.hole.setTransparency(True)
        self.hole.setP(-90.0)
        self.hole.setScale(3)
        self.hole.setBin('ground', 3)
        self.hole.setDepthOffset(1)
        self.hole.reparentTo(self.parent)

    def unload(self):
        self.cleanup()
        self.removeNode()
        self.bodyCollNodePath.removeNode()
        self.headCollNodePath.removeNode()
        self.arm1CollNodePath.removeNode()
        self.arm2CollNodePath.removeNode()
        del self.bodyColl
        del self.bodyCollNode
        del self.bodyCollNodePath
        del self.headColl
        del self.headCollNode
        del self.headCollNodePath
        del self.arm1Coll
        del self.arm1CollNode
        del self.arm1CollNodePath
        del self.arm2Coll
        del self.arm2CollNode
        del self.arm2CollNodePath

    def startActive(self):
        if self.active:
            return
        self.active = True
        for coll in self.collisions:
            coll.unstash()

    def stopActive(self):
        if not self.active:
            return
        self.active = False
        for coll in self.collisions:
            coll.stash()
        self.ignore('pieSplat')

    def getActive(self):
        return self.active

    def __handlePieHit(self, pieCode):
        if pieCode == self.id:
            self.stopActive()
            self.idleTrack.finish()
            hitSeq = Sequence(
                Func(self.headHitFront),
                Wait(self.getDuration('headHitFront')),
                Func(self.down),
                Wait(self.getDuration('down')),
                Func(self.unload)
            )
            hitSeq.start()

    def idle(self):
        self.idleTrack = self.actorInterval('idle')
        self.idleTrack.loop()

    def intoIdle(self):
        Sequence(
            Func(self.up),
            Wait(self.getDuration('up')),
            Func(self.idle),
            Func(self.accept, 'pieSplat', self.__handlePieHit)
        ).start()

    def up(self):
        self.actorInterval('up').start()

    def down(self):
        self.actorInterval('down').start()

    def bodyHitFront(self):
        self.actorInterval('bodyHitFront').start()

    def bodyHitBack(self):
        self.actorInterval('bodyHitBack').start()

    def headHitFront(self):
        self.actorInterval('headHitFront').start()

    def headHitBack(self):
        self.actorInterval('headHitBack').start()
