from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

from toontown.toonbase.ToontownGlobals import WallBitmask


class Treasure(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('Treasure')

    def __init__(self):
        DirectObject.__init__(self)
        self.nodePath = None
        self.treasureFlyTrack = None
        self.modelPath = None
        self.modelFindString = None
        self.grabSoundPath = None
        self.rejectSoundPath = 'phase_4/audio/sfx/ring_miss.ogg'
        self.treasure = None
        self.scale = 1.0
        self.shadow = 1
        self.billboard = 0
        self.dropShadow = None
        self.collNodePath = None
        self.zOffset = 0.0

    def disable(self):
        self.ignoreAll()
        self.nodePath.detachNode()

    def delete(self):
        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None
        self.nodePath.removeNode()

    def announceGenerate(self):
        self.loadModel(self.modelPath, self.modelFindString)
        self.startAnimation()
        self.nodePath.wrtReparentTo(render)
        self.accept(self.uniqueName('entertreasureSphere'), self.handleEnterSphere)

    def loadModel(self, modelPath, modelFindString=None):
        self.grabSound = base.loadSfx(self.grabSoundPath)
        self.rejectSound = base.loadSfx(self.rejectSoundPath)
        if self.nodePath is None:
            self.makeNodePath()
        else:
            self.treasure.getChildren().detach()
        model = loader.loadModel(modelPath)
        if modelFindString is not None:
            model = model.find('**/' + modelFindString)
        model.instanceTo(self.treasure)

    def makeNodePath(self):
        self.nodePath = NodePath(self.uniqueName('treasure'))
        if self.billboard:
            self.nodePath.setBillboardPointEye()
        self.nodePath.setScale(0.9 * self.scale)
        self.treasure = self.nodePath.attachNewNode('treasure')
        if self.shadow:
            if not self.dropShadow:
                self.dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
                self.dropShadow.setColor(0, 0, 0, 0.5)
                self.dropShadow.setPos(0, 0, 0.025)
                self.dropShadow.setScale(0.4 * self.scale)
                self.dropShadow.flattenLight()
            self.dropShadow.reparentTo(self.nodePath)
        collSphere = CollisionSphere(0, 0, 0, self.getSphereRadius())
        collSphere.setTangible(0)
        collNode = CollisionNode(self.uniqueName('treasureSphere'))
        collNode.setIntoCollideMask(WallBitmask)
        collNode.addSolid(collSphere)
        self.collNodePath = self.nodePath.attachNewNode(collNode)
        self.collNodePath.stash()

    def getSphereRadius(self):
        return 2.0

    def setPosition(self, x, y, z):
        if not self.nodePath:
            self.makeNodePath()
        self.nodePath.reparentTo(self.getParentNodePath())
        self.nodePath.setPos(x, y, z + self.zOffset)
        self.collNodePath.unstash()

    def getParentNodePath(self):
        return render

    def handleEnterSphere(self, _=None):
        pass  # TODO

    def startAnimation(self):
        pass

    def uniqueName(self, idString):
        return '%s-%s' % (idString, str(id(self)))
