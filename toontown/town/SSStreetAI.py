from toontown.toonbase import FunnyFarmGlobals
from StreetAI import StreetAI

class SSStreetAI(StreetAI):

    def __init__(self, air):
        StreetAI.__init__(self, air, FunnyFarmGlobals.RicketyRoad)
        self.createZone()