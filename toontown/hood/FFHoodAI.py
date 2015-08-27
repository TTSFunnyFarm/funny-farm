from toontown.toonbase import FunnyFarmGlobals
from HoodAI import HoodAI

class FFHoodAI(HoodAI):

    def __init__(self, air):
        HoodAI.__init__(self, air, FunnyFarmGlobals.FunnyFarm)
        self.createZone()