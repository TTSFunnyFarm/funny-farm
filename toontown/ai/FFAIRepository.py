from direct.showbase.DirectObject import DirectObject
from toontown.toon import Toon, ToonHead
from HolidayManagerAI import HolidayManagerAI
from toontown.hood import FFHoodAI
from toontown.hood import FCHoodAI
from toontown.hood import SSHoodAI

class FFAIRepository(DirectObject):
    notify = directNotify.newCategory('AIRepository')
    notify.setInfo(True)

    def __init__(self):
        self.hoods = []
        self.cogHeadquarters = []
        self.modelMap = {}
        self.suitPlanners = {}
        self.buildingManagers = {}
        self.isLoaded = 0

    def preloadAvatars(self):
        self.notify.info('Preloading avatars...')
        Toon.loadModels()
        Toon.compileGlobalAnimList()
        Toon.loadDialog()
        self.notify.info('Preloading Toon heads...')
        ToonHead.preloadToonHeads()

    def createManagers(self):
        self.notify.info('Creating managers...')
        self.holidayMgr = HolidayManagerAI()

    def createSafeZones(self):
        self.notify.info('Creating safe zones...')
        self.hoods.append(FFHoodAI.FFHoodAI(self))
        self.hoods.append(FCHoodAI.FCHoodAI(self))
        messenger.send('ai-done')
        self.notify.info('Done.')
        self.isLoaded = 1
