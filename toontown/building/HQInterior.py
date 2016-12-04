from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from Interior import Interior
import ToonInteriorColors
import InteriorStorage
import random

class HQInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)
        self.interiorFile = 'phase_3.5/models/modules/HQ_interior'

    def load(self):
        Interior.load(self)
        self.interior.find('**/cream').hide()
        self.interior.find('**/crashed_piano').hide()
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.colors = ToonInteriorColors.colors[FunnyFarmGlobals.FunnyFarm]
        for doorOrigin in render.findAllMatches('**/door_origin*'):
            doorOrigin.setScale(0.8, 0.8, 0.8)
            doorOrigin.setPos(doorOrigin, 0, -0.1, 0)

        doorColor = 0
        if self.zoneId in InteriorStorage.ZoneStyles:
            doorColor = InteriorStorage.ZoneStyles[self.zoneId].get('TI_door', 0)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin_0')
        self.door.setColor(self.colors['TI_door'][doorColor])
        self.door.find('**/door_double_round_ur_trigger').setName('door_0_trigger')
        self.door2 = self.setupDoor('door_double_round_ur', 'door_origin_1')
        self.door2.setColor(self.colors['TI_door'][doorColor])
        self.door2.find('**/door_double_round_ur_trigger').setName('door_1_trigger')
        del self.colors
        self.interior.flattenMedium()
        self.acceptOnce('avatarExitDone', self.startActive)

    def unload(self):
        Interior.unload(self)
