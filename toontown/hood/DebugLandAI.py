from toontown.hood.HoodAI import HoodAI
from toontown.toonbase import FunnyFarmGlobals

class DebugLandAI(HoodAI):

    def __init__(self, air):
        HoodAI.__init__(self, air, FunnyFarmGlobals.DebugLand)

    def createTreasurePlanner(self):
        return
