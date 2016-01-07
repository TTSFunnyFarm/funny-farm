from toontown.toonbase import FunnyFarmGlobals
from StreetAI import StreetAI

class WWStreetAI(StreetAI):

    def __init__(self, air):
        StreetAI.__init__(self, air, FunnyFarmGlobals.WintryWay)
        self.createZone()
