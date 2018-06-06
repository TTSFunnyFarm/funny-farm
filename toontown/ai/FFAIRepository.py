from direct.showbase.DirectObject import DirectObject
from toontown.toon import Toon, ToonHead
from toontown.toon import NPCToons
from toontown.hood import FFHoodAI
from toontown.hood import SSHoodAI
from toontown.quest import Quests
from HolidayManagerAI import HolidayManagerAI

class FFAIRepository(DirectObject):
    notify = directNotify.newCategory('AIRepository')
    notify.setInfo(True)

    def __init__(self):
        self.hoods = []
        self.cogHeadquarters = []
        self.modelMap = {}
        self.treasurePlanners = {}
        self.suitPlanners = {}
        self.buildingManagers = {}
        self.isLoaded = 0
        self.currSuitIndex = 2000000

    def preloadAvatars(self):
        self.notify.info('Preloading avatars...')
        Toon.loadModels()
        Toon.compileGlobalAnimList()
        Toon.loadDialog()
        NPCToons.generateZone2NpcDict()
        ToonHead.preloadToonHeads()
        Quests.createQuestLists()

    def createManagers(self):
        self.notify.info('Creating managers...')
        self.holidayMgr = HolidayManagerAI()

    def createSafeZones(self):
        self.notify.info('Creating safe zones...')
        self.hoods.append(FFHoodAI.FFHoodAI(self))
        self.notify.info('Done.')
        self.isLoaded = 1
        messenger.send('ai-done')

    def getNextSuitIndex(self):
        self.currSuitIndex += 1
        return self.currSuitIndex
