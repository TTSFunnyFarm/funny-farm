from toontown.hood.HoodAI import HoodAI
from toontown.safezone import ButterflyGlobals
from toontown.safezone.FFTreasurePlannerAI import FFTreasurePlannerAI
from toontown.toonbase import FunnyFarmGlobals


class FFHoodAI(HoodAI):

    def __init__(self, air):
        HoodAI.__init__(self, air, FunnyFarmGlobals.FunnyFarm)
        self.createButterflies(ButterflyGlobals.FF)

    def createTreasurePlanner(self):
        treasurePlanner = FFTreasurePlannerAI(self.air, self.zoneId)
        self.air.treasurePlanners[self.zoneId] = treasurePlanner
        treasurePlanner.start()
