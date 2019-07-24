from toontown.suit import SuitDNA
from toontown.suit import SuitTimings
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import *
from panda3d.core import *
from panda3d.core import Point3
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import TTLocalizer
from otp.avatar.Avatar import Avatar

TIME_BUFFER_PER_WPT = 0.25
TIME_DIVISOR = 100
DISTRIBUTE_TASK_CREATION = 0

class SuitBase:
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitBase')

    def __init__(self):
        self.dna = None
        self.level = 0
        self.maxHP = 10
        self.currHP = 10
        self.isSkelecog = 0
        self.isWaiter = 0
        self.isElite = 0
        return

    def delete(self):
        if hasattr(self, 'legList'):
            del self.legList

    def getStyleName(self):
        if hasattr(self, 'dna') and self.dna:
            return self.dna.name
        else:
            self.notify.error('called getStyleName() before dna was set!')
            return 'unknown'

    def getStyleDept(self):
        if hasattr(self, 'dna') and self.dna:
            return SuitDNA.getDeptFullname(self.dna.dept)
        else:
            self.notify.error('called getStyleDept() before dna was set!')
            return 'unknown'

    def getLevel(self):
        return self.level

    def setLevel(self, level):
        self.level = level
        if isinstance(self, Avatar):
            nameWLevel = TTLocalizer.SuitBaseNameWithLevel % {'name': self._name,
             'dept': self.getStyleDept(),
             'level': self.getActualLevel()}
            self.setDisplayName(nameWLevel)
        attributes = SuitBattleGlobals.SuitAttributes[self.dna.name]
        self.maxHP = attributes['hp'][self.level]
        self.currHP = self.maxHP

    def getSkelecog(self):
        return self.isSkelecog

    def setSkelecog(self, flag):
        self.isSkelecog = flag

    def setWaiter(self, flag):
        self.isWaiter = flag

    def setElite(self, flag):
        self.isElite = flag

    def getActualLevel(self):
        if hasattr(self, 'dna'):
            return SuitBattleGlobals.getActualFromRelativeLevel(self.getStyleName(), self.level) + 1
        else:
            self.notify.warning('called getActualLevel with no DNA, returning 1 for level')
            return 1
