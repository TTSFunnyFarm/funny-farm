from direct.showbase.DirectObject import DirectObject

from toontown.ai.HolidayManagerAI import HolidayManagerAI
from toontown.ai.CheesyEffectMgrAI import CheesyEffectMgrAI
from toontown.hood import FFHoodAI
if __debug__:
    from toontown.hood import DebugLandAI
from toontown.quest import Quests
from toontown.toon import NPCToons
from toontown.toon import Toon, ToonHead


class FFAIRepository(DirectObject):
    notify = directNotify.newCategory('AIRepository')
    notify.setInfo(True)

    def __init__(self):
        DirectObject.__init__(self)
        self.hoods = []
        self.cogHeadquarters = []
        self.modelMap = {}
        self.treasurePlanners = {}
        self.suitPlanners = {}
        self.buildingManagers = {}
        self.isLoaded = 0
        self.currSuitIndex = 2000000
        self.holidayMgr = None
        self.cheesyEffectMgr = None

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
        self.cheesyEffectMgr = CheesyEffectMgrAI()

    def createSafeZones(self):
        self.notify.info('Creating safe zones...')
        self.hoods.append(FFHoodAI.FFHoodAI(self))
        if __debug__:
            self.hoods.append(DebugLandAI.DebugLandAI(self))
        self.notify.info('Done.')
        self.isLoaded = 1
        messenger.send('ai-done')

    def getNextSuitIndex(self):
        self.currSuitIndex += 1
        return self.currSuitIndex
