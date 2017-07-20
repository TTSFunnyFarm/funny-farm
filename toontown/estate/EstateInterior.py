import random
from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.building.Interior import Interior
from toontown.building import ToonInteriorColors
from toontown.building import InteriorStorage

class EstateInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)
        self.interiorFile = 'phase_5.5/models/estate/tt_m_ara_int_estateHouseA'

    def load(self):
        Interior.load(self)
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.colors = ToonInteriorColors.colors[FunnyFarmGlobals.FunnyFarm]

        doorOrigin = self.interior.find('**/door_origin')
        doorOrigin.setHpr(180, 0, 0)
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        doorColor = 0
        if self.zoneId in InteriorStorage.ZoneStyles:
            doorColor = InteriorStorage.ZoneStyles[self.zoneId].get('TI_door', 0)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        self.door.setColor(self.colors['TI_door'][doorColor])
        del self.colors
        self.interior.flattenMedium()
        self.acceptOnce('avatarExitDone', self.startActive)

    def unload(self):
        Interior.unload(self)
