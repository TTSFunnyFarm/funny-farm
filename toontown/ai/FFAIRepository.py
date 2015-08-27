from direct.showbase.DirectObject import DirectObject
from toontown.toon import Toon
from toontown.hood import FFHoodAI
from toontown.hood import FCHoodAI
from toontown.hood import SSHoodAI
from toontown.town import SSStreetAI

class FFAIRepository(DirectObject):
    notify = directNotify.newCategory('AIRepository')
    notify.setInfo(True)

    def __init__(self):
        self.preloaded = []
        self.hoods = []
        self.streets = []
        self.cogHeadquarters = []
        self.jellybeanPlanners = {}
        self.suitPlanners = {}
        self.buildingPlanners = {}

    def createSafeZones(self):
        self.notify.info('Creating safe zones...')
        self.hoods.append(FFHoodAI.FFHoodAI(self))
        self.hoods.append(FCHoodAI.FCHoodAI(self))
        self.hoods.append(SSHoodAI.SSHoodAI(self))
        self.hoods.append(SSStreetAI.SSStreetAI(self))
        self.notify.info('Done.')

    def preloadAvatars(self):
        self.notify.info('Preloading avatars...')
        Toon.loadModels()
        Toon.compileGlobalAnimList()
        Toon.loadDialog()
        self.notify.info('Done.')