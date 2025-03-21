from panda3d.core import *
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toon import NPCToonBase

class NPCScientist(NPCToonBase.NPCToonBase):

    def __init__(self):
        NPCToonBase.NPCToonBase.__init__(self)
        self.show()

    def sillyMeterIsRunning(self, isRunning):
        if isRunning:
            self.show()
        else:
            self.hide()

    def getCollSphereRadius(self):
        return 2.5

    def initPos(self):
        self.setHpr(180, 0, 0)
        self.setScale(1.0)

    def handleCollisionSphereEnter(self, collEntry):
        pass
        # self.nametag3d.setDepthTest(0)
        # self.nametag3d.setBin('fixed', 0)

    def setChat(self, topic, partPos, partId, progress, flags):
        msg = TTLocalizer.toontownDialogues[topic][partPos, partId][progress]
        self.setChatMuted(msg, flags)

    def generateToon(self):
        self.setLODs()
        self.generateToonLegs()
        self.generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.rightHands = []
        self.leftHands = []
        self.headParts = []
        self.hipsParts = []
        self.torsoParts = []
        self.legsParts = []
        self.__bookActors = []
        self.__holeActors = []
        self.setupToonNodes()
        if config.GetBool('smooth-animations', True):
            self.setBlend(frameBlend=True)
        if self.style.getTorsoSize() == 'short' and self.style.getAnimal() == 'duck':
            sillyReader = loader.loadModel('phase_4/models/props/tt_m_prp_acs_sillyReader')
            for rHand in self.getRightHands():
                placeholder = rHand.attachNewNode('SillyReader')
                sillyReader.instanceTo(placeholder)
                placeholder.setH(180)
                placeholder.setScale(render, 1.0)
                placeholder.setPos(0, 0, 0.1)

        elif self.style.getTorsoSize() == 'long' and self.style.getAnimal() == 'monkey' or self.style.getTorsoSize() == 'medium' and self.style.getAnimal() == 'horse':
            clipBoard = loader.loadModel('phase_4/models/props/tt_m_prp_acs_clipboard')
            for rHand in self.getRightHands():
                placeholder = rHand.attachNewNode('ClipBoard')
                clipBoard.instanceTo(placeholder)
                placeholder.setH(180)
                placeholder.setScale(render, 1.0)
                placeholder.setPos(0, 0, 0.1)

    def startLookAround(self):
        pass

    def scientistPlay(self):
        if self.style.getTorsoSize() == 'short' and self.style.getAnimal() == 'duck':
            sillyReaders = self.findAllMatches('**/SillyReader')
            for sillyReader in sillyReaders:
                if not sillyReader.isEmpty():
                    sillyReader.stash()
                sillyReader = None

        elif self.style.getTorsoSize() == 'long' and self.style.getAnimal() == 'monkey':
            clipBoards = self.findAllMatches('**/ClipBoard')
            for clipBoard in clipBoards:
                if not clipBoard.isEmpty():
                    clipBoard.stash()
                clipBoard = None
        return

    def showScientistProp(self):
        if self.style.getTorsoSize() == 'short' and self.style.getAnimal() == 'duck':
            sillyReaders = self.findAllMatches('**/SillyReader;+s')
            for sillyReader in sillyReaders:
                if not sillyReader.isEmpty():
                    sillyReader.unstash()
                sillyReader = None

        elif self.style.getTorsoSize() == 'long' and self.style.getAnimal() == 'monkey':
            clipBoards = self.findAllMatches('**/ClipBoard;+s')
            for clipBoard in clipBoards:
                if not clipBoard.isEmpty():
                    clipBoard.unstash()
                clipBoard = None
        return
