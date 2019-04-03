from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
import string
from toontown.toon import LaffMeter
from toontown.battle import BattleBase
from toontown.battle import BattleProps
from direct.task.Task import Task
from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toonbase import TTLocalizer

class TownBattleCogPanel(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattleCogPanel')
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

    def __init__(self, id):
        gui = loader.loadModel('phase_3.5/models/gui/battle_gui')
        DirectFrame.__init__(self, relief=None, image=gui.find('**/ToonBtl_Status_BG'), image_color=Vec4(0.7, 0.7, 0.7, 0.8))
        self.setScale(0.8)
        self.initialiseoptions(TownBattleCogPanel)
        self.hidden = False
        self.cog = None
        self.levelText = DirectLabel(parent=self, text='', pos=(0.1, 0, -0.06), text_scale=0.045)
        self.healthText = DirectLabel(parent=self, text='', pos=(-0.06, 0, -0.06), text_scale=0.05)
        healthGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = healthGui.find('**/minnieCircle')
        button.setScale(0.5)
        button.setH(180)
        button.setColor(Vec4(0, 1, 0, 1))
        self.accept('inventory-levels', self.__handleToggle)
        self.healthNode = self.attachNewNode('health')
        self.healthNode.setPos(-0.06, 0, 0.05)
        button.reparentTo(self.healthNode)
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.reparentTo(button)
        glow.setScale(0.28)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(Vec4(0.25, 1, 0.25, 0.5))
        self.button = button
        self.glow = glow
        self.head = None
        self.blinkTask = None
        self.hide()
        healthGui.removeNode()
        gui.removeNode()
        return

    def setCogInformation(self, cog):
        self.cog = cog
        self.updateHealthBar()
        if self.head:
            self.head.removeNode()
        self.head = self.attachNewNode('head')
        for part in cog.headParts:
            copyPart = part.copyTo(self.head)
            copyPart.setDepthTest(1)
            copyPart.setDepthWrite(1)

        p1, p2 = Point3(), Point3()
        self.head.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[1], d[2])
        s = 0.1 / biggest
        self.head.setPosHprScale(0.1, 0, 0.01, 180, 0, 0, s, s, s)
        self.setLevelText(cog.getActualLevel(), cog.getSkeleRevives(), cog.isElite)

    def setLevelText(self, hp, revives=0, elite=0):
        self.levelText['text'] = TTLocalizer.DisguisePageCogLevel % str(hp)
        if elite:
            self.levelText['text'] = self.levelText['text'] + '\n' + TTLocalizer.EliteCogName
            self.levelText.setZ(-0.045)
        else:
            self.levelText.setZ(-0.06)
        if revives > 0:
            self.levelText['text'] = self.levelText['text'] + TTLocalizer.SkeleRevivePostFix
        if self.cog.currHP >= 100 and self.cog.getActualLevel() >= 10 or self.cog.getActualLevel() == 12:
            self.levelText.setX(0.12)
        else:
            self.levelText.setX(0.1)
        self.healthText['text'] = '%d/%d' % (self.cog.currHP, self.cog.maxHP)

    def updateHealthBar(self):
        condition = self.cog.healthCondition
        if condition == 4:
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.uniqueName('blink-task'))
        elif condition == 5:
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.uniqueName('blink-task'))
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            self.button.setColor(self.healthColors[condition], 1)
            self.glow.setColor(self.healthGlowColors[condition], 1)

    def show(self):
        if self.cog:
            self.updateHealthBar()
        self.hidden = False
        DirectFrame.show(self)

    def __handleToggle(self):
        if self.cog:
            if self.hidden:
                self.show()
            else:
                self.hide()

    def __blinkRed(self, task):
        self.button.setColor(self.healthColors[3], 1)
        self.glow.setColor(self.healthGlowColors[3], 1)
        return Task.done

    def __blinkGray(self, task):
        self.button.setColor(self.healthColors[4], 1)
        self.glow.setColor(self.healthGlowColors[4], 1)
        return Task.done

    def hide(self):
        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None
        self.hidden = True
        DirectFrame.hide(self)
        return

    def cleanup(self):
        self.ignoreAll()
        if self.head:
            self.head.removeNode()
            del self.head
        taskMgr.remove(self.uniqueName('blink-task'))
        del self.blinkTask
        self.button.removeNode()
        self.glow.removeNode()
        DirectFrame.destroy(self)
