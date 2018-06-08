from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from panda3d.direct import *

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
        self.fly = 1
        self.av = None
        self.doId = 0

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

    def setDoId(self, doId):
        self.doId = doId

    def getDoId(self):
        return self.doId

    def getParentNodePath(self):
        return render

    def handleEnterSphere(self, _=None):
        if not self.fly:
            self.handleGrab()
        self.requestGrab()

    def handleGrab(self):
        self.collNodePath.stash()
        if base.localAvatar:
            av = base.localAvatar
            self.av = av
        else:
            self.nodePath.detachNode()
            return
        if self.av == base.localAvatar:
            base.playSfx(self.grabSound, node=self.nodePath)
        if not self.fly:
            self.nodePath.detachNode()
            return
        self.nodePath.wrtReparentTo(av)
        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None
        flytime = 1.0
        track = Sequence(LerpPosInterval(self.nodePath, flytime, pos=Point3(0, 0, 3), startPos=self.nodePath.getPos(),
                                         blendType='easeInOut'), Func(self.nodePath.detachNode))
        if self.shadow:
            self.treasureFlyTrack = Sequence(HideInterval(self.dropShadow), track, ShowInterval(self.dropShadow),
                                             name=self.uniqueName('treasureFlyTrack'))
        else:
            self.treasureFlyTrack = Sequence(track, name=self.uniqueName('treasureFlyTrack'))
        self.treasureFlyTrack.start()

    def requestGrab(self):
        if not hasattr(base.cr.playGame.hood, 'treasurePlanner'):
            return

        treasurePlanner = base.cr.playGame.hood.treasurePlanner
        if not treasurePlanner:
            return

        treasurePlannerAI = base.air.treasurePlanners.get(treasurePlanner.zoneId)
        if not treasurePlannerAI:
            return

        treasurePlannerAI.grabAttempt(self.getDoId())

    def setReject(self):
        if self.treasureFlyTrack:
            self.treasureFlyTrack.finish()
            self.treasureFlyTrack = None
        base.playSfx(self.rejectSound, node=self.nodePath)
        self.treasureFlyTrack = Sequence(LerpColorScaleInterval(self.nodePath, 0.8, colorScale=VBase4(0, 0, 0, 0),
                                                                startColorScale=VBase4(1, 1, 1, 1), blendType='easeIn'),
                                         LerpColorScaleInterval(self.nodePath, 0.2, colorScale=VBase4(1, 1, 1, 1),
                                                                startColorScale=VBase4(0, 0, 0, 0),
                                                                blendType='easeOut'),
                                         name=self.uniqueName('treasureFlyTrack'))
        self.treasureFlyTrack.start()

    def setGrab(self):
        if not base.localAvatar:
            return

        if self.fly or self.av != base.localAvatar:
            self.handleGrab()

    def startAnimation(self):
        pass

    def uniqueName(self, idString):
        return '%s-%s' % (idString, str(id(self)))
