import random
from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import *
from toontown.toonbase import TTLocalizer
from toontown.suit.SuitGlobals import *
import random
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from otp.avatar import AvatarDNA
notify = directNotify.newCategory('SuitDNA')
suitHeadTypes = ['f',
 'p',
 'ym',
 'mm',
 'ds',
 'hh',
 'cr',
 'tbc',
 'bf',
 'b',
 'dt',
 'ac',
 'bs',
 'sd',
 'le',
 'bw',
 'sc',
 'pp',
 'tw',
 'bc',
 'nc',
 'mb',
 'ls',
 'rb',
 'cc',
 'tm',
 'nd',
 'gh',
 'ms',
 'tf',
 'm',
 'mh']
suitATypes = ['ym',
 'hh',
 'tbc',
 'dt',
 'bs',
 'le',
 'bw',
 'pp',
 'nc',
 'rb',
 'nd',
 'tf',
 'm',
 'mh']
suitBTypes = ['p',
 'ds',
 'b',
 'ac',
 'sd',
 'bc',
 'ls',
 'tm',
 'ms']
suitCTypes = ['f',
 'mm',
 'cr',
 'bf',
 'sc',
 'tw',
 'mb',
 'cc',
 'gh']
corpPolyColor = VBase4(0.95, 0.75, 0.75, 1.0)
legalPolyColor = VBase4(0.75, 0.75, 0.95, 1.0)
moneyPolyColor = VBase4(0.65, 0.95, 0.85, 1.0)
salesPolyColor = VBase4(0.95, 0.75, 0.95, 1.0)
goonTypes = ['pg', 'sg']

aSize = 6.06
bSize = 5.29
cSize = 4.14

SuitLooks = {'f': (cSize, corpPolyColor, ['flunky', 'glasses'], 4.88),
             'p': (bSize, corpPolyColor, ['pencilpusher'], 5.0),
             'ym': (aSize, corpPolyColor, ['yesman'], 5.28),
             'mm': (cSize, corpPolyColor, ['micromanager'], 3.25),
             'ds': (bSize, corpPolyColor, ['beancounter'], 6.08),
             'hh': (aSize, corpPolyColor, ['headhunter'], 7.45),
             'cr': (cSize, VBase4(0.85, 0.55, 0.55, 1.0), ['flunky'], 8.23, ['corporate-raider.jpg']),
             'tbc': (aSize, VBase4(0.75, 0.95, 0.75, 1.0), ['bigcheese'], 9.34),
             'bf': (cSize, legalPolyColor, ['tightwad'], 4.81, ['bottom-feeder.jpg']),
             'b': (bSize, VBase4(0.95, 0.95, 1.0, 1.0), ['movershaker'], 6.17, ['blood-sucker.jpg']),
             'dt': (bSize, legalPolyColor, ['twoface'], 5.63, ['double-talker.jpg']),
             'ac': (bSize, legalPolyColor, ['ambulancechaser'], 6.39),
             'bs': (aSize, legalPolyColor, ['backstabber'], 6.71),
             'sd': (bSize, legalPolyColor, ['telemarketer'], 7.9, ['spin-doctor.jpg']),
             'le': (aSize, VBase4(0.25, 0.25, 0.5, 1.0), ['legaleagle'], 8.27),
             'bw': (aSize, legalPolyColor, ['bigwig'], 8.69),
             'sc': (cSize, moneyPolyColor, ['coldcaller'], 4.77),
             'pp': (aSize, VBase4(1.0, 0.5, 0.6, 1.0), ['pennypincher'], 5.26),
             'tw': (cSize, moneyPolyColor, ['tightwad'], 5.41),
             'bc': (bSize, moneyPolyColor, ['beancounter'], 5.95),
             'nc': (aSize, moneyPolyColor, ['numbercruncher'], 7.22),
             'mb': (cSize, moneyPolyColor, ['moneybags'], 6.97),
             'ls': (bSize, VBase4(0.5, 0.85, 0.75, 1.0), ['loanshark'], 8.58),
             'rb': (aSize, moneyPolyColor, ['yesman'], 8.95, ['robber-baron.jpg']),
             'cc': (cSize, VBase4(0.55, 0.65, 1.0, 1.0), ['coldcaller'], 4.63, None, [VBase4(0.25, 0.35, 1.0, 1.0)]),
             'tm': (bSize, salesPolyColor, ['telemarketer'], 5.24),
             'nd': (aSize, salesPolyColor, ['numbercruncher'], 5.98, ['name-dropper.jpg']),
             'gh': (cSize, salesPolyColor, ['gladhander'], 6.4),
             'ms': (bSize, salesPolyColor, ['movershaker'], 6.7),
             'tf': (aSize, salesPolyColor, ['twoface'], 6.95),
             'm': (aSize, salesPolyColor, ['twoface'], 7.61, ['mingler.jpg']),
             'mh': (aSize, salesPolyColor, ['yesman'], 8.95)}

def getSuitBodyType(name):
    if name in suitATypes:
        return 'a'
    elif name in suitBTypes:
        return 'b'
    elif name in suitCTypes:
        return 'c'
    else:
        print('Unknown body type for suit name: ', name)


def getSuitDept(name):
    index = suitHeadTypes.index(name)
    if index < suitsPerDept:
        return suitDepts[0]
    elif index < suitsPerDept * 2:
        return suitDepts[1]
    elif index < suitsPerDept * 3:
        return suitDepts[2]
    elif index < suitsPerDept * 4:
        return suitDepts[3]
    else:
        print('Unknown dept for suit name: ', name)
        return None
    return None

def getDeptFullname(dept):
    return suitDeptFullnames[dept]

def getDeptFullnameP(dept):
    return suitDeptFullnamesP[dept]

def getSuitDeptFullname(name):
    return suitDeptFullnames[getSuitDept(name)]


def getSuitType(name):
    index = suitHeadTypes.index(name)
    return index % suitsPerDept + 1

def getSuitName(type, dept):
    dept = suitDepts.index(dept)
    type += suitsPerDept * dept
    return suitHeadTypes[type - 1]

def getRandomSuitType(level, rng = random):
    return random.randint(max(level - 4, 1), min(level, 8))


def getRandomSuitByDept(dept):
    deptNumber = suitDepts.index(dept)
    return suitHeadTypes[suitsPerDept * deptNumber + random.randint(0, 7)]


class SuitDNA(AvatarDNA.AvatarDNA):

    def __init__(self, str = None, type = None):
        if str != None:
            self.makeFromNetString(str)
        elif type != None:
            if type == SUIT:
                self.newSuit()
        else:
            self.type = UNDEFINED
        return

    def __str__(self):
        if self.type == SUIT:
            return 'type = %s\nbody = %s, dept = %s, name = %s' % ('suit',
             self.body,
             self.dept,
             self.name)
        elif self.type == BOSS:
            return 'type = boss cog\ndept = %s' % self.dept
        elif self.type == GOON:
            return 'goon'
        else:
            return 'type undefined'

    def makeNetString(self):
        dg = PyDatagram()
        dg.addInt8(self.type)
        if self.type == SUIT:
            dg.addFixedString(self.name, 3)
            dg.addFixedString(self.dept, 1)
        elif self.type == BOSS:
            dg.addFixedString(self.dept, 1)
        elif self.type == 'u':
            notify.error('undefined avatar')
        else:
            notify.error('unknown avatar type: ', self.type)
        return dg.getMessage()

    def makeFromNetString(self, string):
        dg = PyDatagram(string)
        dgi = PyDatagramIterator(dg)
        self.type = dgi.getInt8()
        if self.type == SUIT:
            self.name = dgi.getFixedString(3)
            self.dept = dgi.getFixedString(1)
            self.body = getSuitBodyType(self.name)
        elif self.type == BOSS:
            self.dept = dgi.getFixedString(1)
        else:
            notify.error('unknown avatar type: ', self.type)
        return None

    def __defaultGoon(self):
        self.type = GOON
        self.name = goonTypes[0]

    def __defaultSuit(self):
        self.type = SUIT
        self.name = 'ds'
        self.dept = getSuitDept(self.name)
        self.body = getSuitBodyType(self.name)

    def newSuit(self, name = None):
        if name == None:
            self.__defaultSuit()
        else:
            self.type = SUIT
            self.name = name
            self.dept = getSuitDept(self.name)
            self.body = getSuitBodyType(self.name)
        return

    def newBossCog(self, dept):
        self.type = BOSS
        self.dept = dept

    def newSuitRandom(self, type = None, dept = None):
        self.type = SUIT
        if type == None:
            type = random.randint(1, suitsPerDept) - 1
        if dept == None:
            dept = random.choice(suitDepts)
        self.dept = dept
        self.name = getSuitName(type, dept)
        self.body = getSuitBodyType(self.name)
        return

    def newGoon(self, name = None):
        if type == None:
            self.__defaultGoon()
        else:
            self.type = GOON
            if name in goonTypes:
                self.name = name
            else:
                notify.error('unknown goon type: ', name)
        return

    def getType(self):
        if self.type == SUIT:
            type = 'suit'
        elif self.type == BOSS:
            type = 'boss'
        else:
            notify.error('Invalid DNA type: ', self.type)
        return type
