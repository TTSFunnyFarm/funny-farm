from direct.actor import Actor
from otp.avatar import Avatar
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from libotp import *
from toontown.battle import SuitBattleGlobals
from direct.task.Task import Task
from toontown.battle import BattleProps
from toontown.toonbase import TTLocalizer
from panda3d.core import VirtualFileMountHTTP, VirtualFileSystem, Filename, DSearchPath
import string
import os

SuitDialogArray = []
SkelSuitDialogArray = []

AllCogsAnims = [('walk', 'walk'),
 ('run', 'walk'),
 ('neutral', 'neutral'),
 ('victory', 'victory'),
 ('flail', 'flailing'),
 ('tug-o-war', 'tug-o-war'),
 ('slip-backward', 'slip-backward'),
 ('slip-forward', 'slip-forward'),
 ('lose', 'lose'),
 ('pie-small-react', 'pie-small'),
 ('squirt-small-react', 'squirt-small'),
 ('drop-react', 'anvil-drop'),
 ('flatten', 'drop'),
 ('sidestep-left', 'sidestep-left'),
 ('sidestep-right', 'sidestep-right'),
 ('squirt-large-react', 'squirt-large'),
 ('landing', 'landing'),
 ('reach', 'walknreach'),
 ('rake-react', 'rake'),
 ('hypnotized', 'hypnotize'),
 ('lured', 'lured'),
 ('soak', 'soak'),
 ('throw-paper', 'throw-paper'),
 ('magic1', 'magic1'),
 ('magic2', 'magic2'),
 ('soak', 'soak'),
 ('speak', 'speak'),
 ('phone', 'phone'),
 ('pickpocket', 'pickpocket'),
 ('pen-squirt', 'pen-squirt'),
 ('effort', 'effort')]

WaiterCogsAnims = [('leftsit-hungry', 'leftsit-hungry'),
 ('rightsit-hungry', 'rightsit-hungry'),
 ('sit', 'sit'),
 ('sit-angry', 'sit-angry'),
 ('sit-eat-in', 'sit-eat-in'),
 ('sit-eat-loop', 'sit-eat-loop'),
 ('sit-eat-out', 'sit-eat-out'),
 ('sit-lose', 'sit-lose'),
 ('tray-neutral', 'tray-neutral'),
 ('tray-walk', 'tray-walk')]

CogAnimsDict = {'a': [('cigar-smoke', 'cigar-smoke'),
 ('song-and-dance', 'song-and-dance'),
 ('pen-squirt', 'fountain-pen'),
 ('throw-object', 'throw-object'),
 ('smile', 'smile'),
 ('rubber-stamp', 'rubber-stamp'),
 ('roll-o-dex', 'roll-o-dex'),
 ('magic3', 'magic3'),
 ('golf-club-swing', 'golf-club-swing'),
 ('glower', 'glower'),
 ('finger-wag', 'finger-wag'),
 ('throw-object', 'throw-object')],
 'b': [('quick-jump', 'jump'),
 ('throw-object', 'throw-object'),
 ('stomp', 'stomp'),
 ('roll-o-dex', 'roll-o-dex'),
 ('pencil-sharpener', 'pencil-sharpener'),
 ('magic3', 'magic3'),
 ('hold-pencil', 'hold-pencil'),
 ('hold-eraser', 'hold-eraser')],
 'c': [('watercooler', 'watercooler'),
 ('glower', 'glower'),
 ('shredder', 'shredder')]}

ModelDict = {'a': '/models/char/suitA-',
 'b': '/models/char/suitB-',
 'c': '/models/char/suitC-'}

def loadTutorialSuit():
    loader.loadModel('phase_3.5/models/char/suitC-mod')
    loadDialog(1)


def loadSuits(level):
    loadSuitModelsAndAnims(level, flag=1)
    loadDialog(level)


def unloadSuits(level):
    loadSuitModelsAndAnims(level, flag=0)
    unloadDialog(level)


def loadSuitModelsAndAnims(level, flag = 0):
    for key in ModelDict.keys():
        model, phase = ModelDict[key]
        if not model or not phase:
            return
        headModel, headPhase = ModelDict[key]
        if flag:
            loader.loadModel('phase_3.5' + model + 'mod')
            loader.loadModel('phase_4' + headModel + 'heads')
        else:
            loader.unloadModel('phase_3.5' + model + 'mod')
            loader.unloadModel('phase_4' + headModel + 'heads')


def cogExists(filePrefix):
    searchPath = DSearchPath()
    searchPath.appendDirectory(Filename('resources/phase_3.5'))
    filePrefix = filePrefix.strip('/')
    pfile = Filename(filePrefix)
    found = vfs.resolveFilename(pfile, searchPath)
    return found

def loadDialog(level):
    global SuitDialogArray
    if len(SuitDialogArray) > 0:
        return
    else:
        loadPath = 'phase_3.5/audio/dial/'
        SuitDialogFiles = ['COG_VO_statement',
         'COG_VO_murmur',
         'COG_VO_statement',
         'COG_VO_question']
        for file in SuitDialogFiles:
            SuitDialogArray.append(base.loader.loadSfx(loadPath + file + '.ogg'))

        SuitDialogArray.append(SuitDialogArray[0])
        SuitDialogArray.append(SuitDialogArray[1])


def loadSkelDialog():
    global SkelSuitDialogArray
    if len(SkelSuitDialogArray) > 0:
        return
    else:
        grunt = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_grunt.ogg')
        murmur = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_murmur.ogg')
        statement = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_statement.ogg')
        question = loader.loadSfx('phase_5/audio/sfx/Skel_COG_VO_question.ogg')
        SkelSuitDialogArray = [grunt,
         murmur,
         statement,
         question,
         statement,
         statement]


def unloadDialog(level):
    global SuitDialogArray
    SuitDialogArray = []


def unloadSkelDialog():
    global SkelSuitDialogArray
    SkelSuitDialogArray = []


def attachSuitHead(node, suitName):
    suitIndex = SuitDNA.suitHeadTypes.index(suitName)
    suitDNA = SuitDNA.SuitDNA()
    suitDNA.newSuit(suitName)
    suit = Suit()
    suit.setDNA(suitDNA)
    headParts = suit.getHeadParts()
    head = node.attachNewNode('head')
    for part in headParts:
        copyPart = part.copyTo(head)
        copyPart.setDepthTest(1)
        copyPart.setDepthWrite(1)

    suit.delete()
    suit = None
    p1 = Point3()
    p2 = Point3()
    head.calcTightBounds(p1, p2)
    d = p2 - p1
    biggest = max(d[0], d[2])
    column = suitIndex % SuitDNA.suitsPerDept
    s = (0.2 + column / 100.0) / biggest
    pos = -0.14 + (SuitDNA.suitsPerDept - column - 1) / 135.0
    head.setPosHprScale(0, 0, pos, 180, 0, 0, s, s, s)
    return head


class Suit(Avatar.Avatar):
    healthColors = (Vec4(0, 1, 0, 1),
     Vec4(1, 1, 0, 1),
     Vec4(1, 0.5, 0, 1),
     Vec4(1, 0, 0, 1),
     Vec4(0.3, 0.3, 0.3, 1))
    healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
     Vec4(1, 1, 0.25, 0.5),
     Vec4(1, 0.5, 0.25, 0.5),
     Vec4(1, 0.25, 0.25, 0.5),
     Vec4(0.3, 0.3, 0.3, 0))
    medallionColors = {'c': Vec4(0.863, 0.776, 0.769, 1.0),
     's': Vec4(0.843, 0.745, 0.745, 1.0),
     'l': Vec4(0.749, 0.776, 0.824, 1.0),
     'm': Vec4(0.749, 0.769, 0.749, 1.0)}

    def __init__(self):
        try:
            self.Suit_initialized
            return
        except:
            self.Suit_initialized = 1

        Avatar.Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        self.setPickable(0)  # NOTE: Change 0 to 1 to make name tags clickable.
        self.leftHand = None
        self.rightHand = None
        self.shadowJoint = None
        self.nametagJoint = None
        self.headParts = []
        self.healthBar = None
        self.healthCondition = 0
        self.isDisguised = 0
        self.isWaiter = 0
        self.isRental = 0
        self.isElite = 0
        return

    def delete(self):
        try:
            self.Suit_deleted
        except:
            self.Suit_deleted = 1
            self.ignoreAll()
            if self.leftHand:
                self.leftHand.removeNode()
                self.leftHand = None
            if self.rightHand:
                self.rightHand.removeNode()
                self.rightHand = None
            if self.shadowJoint:
                self.shadowJoint.removeNode()
                self.shadowJoint = None
            if self.nametagJoint:
                self.nametagJoint.removeNode()
                self.nametagJoint = None
            for part in self.headParts:
                part.removeNode()

            self.headParts = []
            self.removeHealthBar()
            Avatar.Avatar.delete(self)

        return

    def setHeight(self, height):
        Avatar.Avatar.setHeight(self, height)
        self.nametag3d.setPos(0, 0, height + 1.0)

    def getRadius(self):
        return 2

    def setDNAString(self, dnaString):
        self.dna = SuitDNA.SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.setDNA(self.dna)

    def setDNA(self, dna):
        if self.style:
            pass
        else:
            self.style = dna
            self.generateSuit()
            self.initializeDropShadow()
            self.initializeNametag3d()

    def __loadSuitTexture(self, tex):
        tex = loader.loadTexture(tex)
        tex.setMinfilter(Texture.FTLinearMipmapLinear)
        tex.setMagfilter(Texture.FTLinear)
        return tex

    def generateSuit(self):
        dna = self.style
        self.headParts = []
        self.headColor = None
        self.headTexture = None
        self.loseActor = None
        self.isSkeleton = 0
        scale = SuitBattleGlobals.SuitSizes[dna.name]
        look = SuitDNA.SuitLooks[dna.name]
        self.scale = scale / look[0]
        self.handColor = look[1]
        self.generateBody()
        i = 0
        for head in look[2]:
            if len(look) > 4:
                if look[4]:
                    self.headTexture = look[4][i]
            if len(look) > 5:
                self.headColor = look[5][i]
            self.generateHead(head)
            i += 1
        self.setHeight(look[3])
        self.setName(SuitBattleGlobals.SuitAttributes[dna.name]['name'])
        self.getGeomNode().setScale(self.scale)
        self.generateHealthBar()
        self.generateMedallion()
        if config.GetBool('smooth-animations', True):
            self.setBlend(frameBlend=True)
        return

    def generateBody(self):
        animDict = self.generateAnimDict()
        bodyType = self.style.body.upper()
        self.loadModel('phase_3.5/models/char/suit{}-mod'.format(bodyType))
        self.loadAnims(animDict)
        self.setSuitClothes()

    def generateAnimDict(self):
        animDict = {}
        bodyType = self.style.body.upper()
        for anim in AllCogsAnims:
            animDict[anim[0]] = "phase_4/models/char/suit{}-{}".format(bodyType, anim[1])
        for anim in CogAnimsDict[self.style.body]:
            animDict[anim[0]] = "phase_5/models/char/suit{}-{}".format(bodyType, anim[1])
        return animDict

    def initializeBodyCollisions(self, collIdStr):
        Avatar.Avatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)

    def setSuitClothes(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self
        dept = self.style.dept
        phase = 3.5
        torsoTex = self.__loadSuitTexture('phase_%s/maps/%s_blazer.jpg' % (phase, dept))
        legTex = self.__loadSuitTexture('phase_%s/maps/%s_leg.jpg' % (phase, dept))
        armTex = self.__loadSuitTexture('phase_%s/maps/%s_sleeve.jpg' % (phase, dept))
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)
        modelRoot.find('**/hands').setColor(self.handColor)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagJoint = self.find('**/joint_nameTag')

    def makeWaiter(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self
        self.isWaiter = 1
        torsoTex = self.__loadSuitTexture('phase_3.5/maps/waiter_m_blazer.jpg')
        legTex = self.__loadSuitTexture('phase_3.5/maps/waiter_m_leg.jpg')
        armTex = self.__loadSuitTexture('phase_3.5/maps/waiter_m_sleeve.jpg')
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)

    def makeRentalSuit(self, suitType, modelRoot = None):
        if not modelRoot:
            modelRoot = self.getGeomNode()
        if suitType == 's':
            torsoTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_blazer.jpg')
            legTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_leg.jpg')
            armTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_sleeve.jpg')
            handTex = loader.loadTexture('phase_3.5/maps/tt_t_ene_sellbotRental_hand.jpg')
        else:
            self.notify.warning('No rental suit for cog type %s' % suitType)
            return
        self.isRental = 1
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)
        modelRoot.find('**/hands').setTexture(handTex, 1)

    def makeElite(self, modelRoot = None):
        if not modelRoot:
            modelRoot = self
        self.isElite = 1
        torsoTex = self.__loadSuitTexture('phase_3.5/maps/e_blazer.jpg')
        legTex = self.__loadSuitTexture('phase_3.5/maps/e_leg.jpg')
        armTex = self.__loadSuitTexture('phase_3.5/maps/e_sleeve.jpg')
        modelRoot.find('**/torso').setTexture(torsoTex, 1)
        modelRoot.find('**/arms').setTexture(armTex, 1)
        modelRoot.find('**/legs').setTexture(legTex, 1)

    def generateHead(self, headType):
        headModel = loader.loadModel('phase_4/models/char/suit{}-heads'.format(self.style.body.upper()))
        headReferences = headModel.findAllMatches('**/' + headType)
        for ref in headReferences:
            headPart = self.instance(ref, 'modelRoot', 'joint_head')
            if self.headTexture:
                headTex = self.__loadSuitTexture('phase_4/maps/{}'.format(self.headTexture))
                headPart.setTexture(headTex, 1)
            if self.headColor:
                headPart.setColor(self.headColor)
            self.headParts.append(headPart)

        headModel.removeNode()

    def generateTie(self, modelPath = None):
        if not modelPath:
            modelPath = self
        dept = self.style.dept
        tie = modelPath.find('**/tie')
        if tie.isEmpty():
            self.notify.warning('Skelecog has no tie model?!')
            return
        tieTex = self.__loadSuitTexture('phase_5/maps/cog_robot_tie_{}.jpg'.format(dept))
        tie.setTexture(tieTex, 1)

    def generateMedallion(self):
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.style.dept
        chestNull = self.find('**/joint_attachMeter')
        if dept == 'c':
            self.corpMedallion = icons.find('**/CorpIcon').copyTo(chestNull)
        elif dept == 's':
            self.corpMedallion = icons.find('**/SalesIcon').copyTo(chestNull)
        elif dept == 'l':
            self.corpMedallion = icons.find('**/LegalIcon').copyTo(chestNull)
        elif dept == 'm':
            self.corpMedallion = icons.find('**/MoneyIcon').copyTo(chestNull)
        self.corpMedallion.setPosHprScale(0.02, 0.05, 0.04, 180.0, 0.0, 0.0, 0.51, 0.51, 0.51)
        self.corpMedallion.setColor(self.medallionColors[dept])
        icons.removeNode()

    def generateHealthBar(self):
        self.removeHealthBar()
        model = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = model.find('**/minnieCircle')
        button.setScale(3.0)
        button.setH(180.0)
        button.setColor(self.healthColors[0])
        chestNull = self.find('**/joint_attachMeter')
        button.reparentTo(chestNull)
        self.healthBar = button
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(0.28)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(self.healthGlowColors[0])
        button.flattenLight()
        self.healthBarGlow = glow
        self.healthBar.hide()
        self.healthCondition = 0

    def reseatHealthBarForSkele(self):
        self.healthBar.setPos(0.0, 0.1, 0.0)

    def updateHealthBar(self, hp, forceUpdate = 0):
        if hp > self.currHP:
            hp = self.currHP
        health = float(self.currHP) / float(self.maxHP)
        if health > 0.95:
            condition = 0
        elif health > 0.7:
            condition = 1
        elif health > 0.3:
            condition = 2
        elif health > 0.05:
            condition = 3
        elif health > 0.0:
            condition = 4
        else:
            condition = 5
        if self.healthCondition != condition or forceUpdate:
            if condition == 4:
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            elif condition == 5:
                if self.healthCondition == 4:
                    taskMgr.remove(self.uniqueName('blink-task'))
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            else:
                self.healthBar.setColor(self.healthColors[condition], 1)
                self.healthBarGlow.setColor(self.healthGlowColors[condition], 1)
            self.healthCondition = condition

    def __blinkRed(self, task):
        self.healthBar.setColor(self.healthColors[3], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[3], 1)
        if self.healthCondition == 5:
            self.healthBar.setScale(1.17)
        return Task.done

    def __blinkGray(self, task):
        if not self.healthBar:
            return
        self.healthBar.setColor(self.healthColors[4], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[4], 1)
        if self.healthCondition == 5:
            self.healthBar.setScale(1.0)
        return Task.done

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.removeNode()
            self.healthBar = None
        if self.healthCondition > 3:
            taskMgr.remove(self.uniqueName('blink-task'))
        self.healthCondition = 0
        return

    def getLoseActor(self):
        bodyType = self.style.body.upper()
        if self.loseActor == None:
            if not self.isSkeleton:
                loseModel = 'phase_4/models/char/suit{}-lose-mod'.format(bodyType)
                loseAnim = 'phase_4/models/char/suit{}-lose'.format(bodyType)
                self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                loseNeck = self.loseActor.find('**/joint_head')
                for part in self.headParts:
                    part.instanceTo(loseNeck)

                if self.isWaiter:
                    self.makeWaiter(self.loseActor)
                elif self.isElite:
                    self.makeElite(self.loseActor)
                else:
                    self.setSuitClothes(self.loseActor)
            else:
                loseModel = 'phase_5/models/char/cog{}_robot-lose-mod'.format(bodyType)
                loseAnim = 'phase_4/models/char/suit{}-lose'.format(bodyType)
                self.loseActor = Actor.Actor(loseModel, {'lose': loseAnim})
                self.generateTie(self.loseActor)
        self.loseActor.setScale(self.scale)
        self.loseActor.setPos(self.getPos())
        self.loseActor.setHpr(self.getH(), 0, 0)
        if config.GetBool('smooth-animations', True):
            self.loseActor.setBlend(frameBlend=True)
        self.collTube = CollisionTube(0, 0, 0.5, 0, 0, 4, 2)
        self.collNode = CollisionNode('loseActor')
        self.collNode.addSolid(self.collTube)
        self.collNodePath = self.loseActor.attachNewNode(self.collNode)
        shadowJoint = self.loseActor.find('**/joint_shadow')
        dropShadow = loader.loadModel('phase_3/models/props/drop_shadow')
        dropShadow.setScale(0.45)
        dropShadow.setColor(0.0, 0.0, 0.0, 0.5)
        dropShadow.reparentTo(shadowJoint)
        return self.loseActor

    def cleanupLoseActor(self):
        self.notify.debug('cleanupLoseActor()')
        if self.loseActor != None:
            self.notify.debug('cleanupLoseActor() - got one')
            self.loseActor.cleanup()
        self.loseActor = None
        return

    def makeSkeleton(self):
        model = 'phase_5/models/char/cog' + self.style.body.upper() + '_robot-zero'
        anims = self.generateAnimDict()
        anim = self.getCurrentAnim()
        # Remove all of the previous cog except for a few necessary joints
        modelRoot = self.getGeomNode()
        modelRoot.find('**/torso').removeNode()
        modelRoot.find('**/arms').removeNode()
        modelRoot.find('**/hands').removeNode()
        modelRoot.find('**/legs').removeNode()
        modelRoot.find('**/').removeNode() # These are feet
        modelRoot.find('**/joint_head').removeNode()
        # Now, to load our skelecog
        self.loadModel(model)
        self.loadAnims(anims)
        self.getGeomNode().setScale(self.scale * 1.0173)
        self.generateHealthBar()
        self.generateTie()
        self.setHeight(self.height)
        parts = self.findAllMatches('**/pPlane*')
        for partNum in range(0, parts.getNumPaths()):
            bb = parts.getPath(partNum)
            bb.setTwoSided(1)

        self.setName(TTLocalizer.Skeleton)
        #nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.name,
         #'dept': self.getStyleDept(),
         #'level': self.getDisplayLevel()}
        #self.setDisplayName(nameInfo)
        self.leftHand = self.find('**/joint_Lhold')
        self.rightHand = self.find('**/joint_Rhold')
        self.shadowJoint = self.find('**/joint_shadow')
        self.nametagNull = self.find('**/joint_nameTag')
        self.loop(anim)
        self.isSkeleton = 1

    def getHeadParts(self):
        return self.headParts

    def getRightHand(self):
        return self.rightHand

    def getLeftHand(self):
        return self.leftHand

    def getShadowJoint(self):
        return self.shadowJoint

    def getNametagJoints(self):
        return []

    def getDialogueArray(self):
        if self.isSkeleton:
            loadSkelDialog()
            return SkelSuitDialogArray
        else:
            loadDialog(1)
            return SuitDialogArray
