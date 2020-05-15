from panda3d.core import *
from direct.gui.DirectGui import *
from direct.task.Task import Task
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.battle import BattleProps

class TownBattleCogPanel(DirectFrame):
    notify = directNotify.newCategory('TownBattleCogPanel')
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
    medallionColors = {'c': Vec4(0.863, 0.676, 0.619, 0.8),
     's': Vec4(0.843, 0.645, 0.645, 0.8),
     'l': Vec4(0.599, 0.676, 0.824, 0.8),
     'm': Vec4(0.649, 0.769, 0.649, 0.8)}

    def __init__(self, id):
        gui = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        DirectFrame.__init__(self, relief=None, image=gui.find('**/InventoryButtonFlat'), image_color=Vec4(0.8, 0.8, 0.8, 0.8), scale=1.8)
        self.initialiseoptions(TownBattleCogPanel)
        self.avatar = None
        model = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = model.find('**/minnieCircle')
        button.reparentTo(self)
        button.setPos(-0.085, 0, 0)
        button.setH(180.0)
        button.setScale(0.225)
        button.setColor(self.healthColors[0])
        self.healthBar = button
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.reparentTo(self.healthBar)
        glow.setScale(0.25)
        glow.setPos(-0.01, 0.01, 0.017)
        glow.setColor(self.healthGlowColors[0])
        button.flattenLight()
        self.healthBarGlow = glow
        self.healthCondition = 0
        self.cogName = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, pos=(-0.05, 0, 0.02), scale=0.019)
        self.healthText = DirectLabel(parent=self, relief=None, text='', text_align=TextNode.ALeft, pos=(-0.05, 0, -0.025), scale=0.025)
        self.hide()
        gui.removeNode()

    def cleanup(self):
        self.ignoreAll()
        self.removeHealthBar()
        DirectFrame.destroy(self)

    def setAvatar(self, avatar):
        self.avatar = avatar
        self.setCogName(avatar.nametag.getName(), avatar.getLevel(), avatar.isElite)
        self.setHealth(avatar.currHP, avatar.maxHP)
        # self['image_color'] = self.medallionColors[avatar.style.dept]

    def setCogName(self, name, level, elite = 0):
        level = TTLocalizer.DisguisePageCogLevel % str(level)
        if elite:
            self.cogName['text'] = '%s\n%s %s' % (name, level, TTLocalizer.EliteCogName)
        else:
            self.cogName['text'] = '%s\n%s' % (name, level)
        if len(name) > 14:
            self.cogName.setScale(0.0165)
        else:
            self.cogName.setScale(0.019)

    def setHealth(self, hp, maxHp):
        self.healthText['text'] = '%d/%d' % (hp, maxHp)
        self.updateHealthBar(hp)

    def updateHealthBar(self, hp, forceUpdate = 0):
        if hp > self.avatar.currHP:
            hp = self.avatar.currHP
        health = float(self.avatar.currHP) / float(self.avatar.maxHP)
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
        return Task.done

    def __blinkGray(self, task):
        self.healthBar.setColor(self.healthColors[4], 1)
        self.healthBarGlow.setColor(self.healthGlowColors[4], 1)
        return Task.done

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.removeNode()
            self.healthBar = None
        taskMgr.remove(self.uniqueName('blink-task'))
        self.healthCondition = 0
