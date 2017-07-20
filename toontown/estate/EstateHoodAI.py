from toontown.toonbase import FunnyFarmGlobals
from toontown.hood.HoodAI import HoodAI

class EstateHoodAI(HoodAI):

    def __init__(self, air):
        HoodAI.__init__(self, air, FunnyFarmGlobals.Estate)
