from toontown.toonbase import FunnyFarmGlobals
from HoodAI import HoodAI

class FCHoodAI(HoodAI):

    def __init__(self, air):
        HoodAI.__init__(self, air, FunnyFarmGlobals.FunnyFarmCentral)
