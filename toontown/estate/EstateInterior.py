import random
from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.building.Interior import Interior
from toontown.building import ToonInteriorColors
from toontown.building import InteriorStorage

WindowPlugNames = ('**/windowcut_a*', '**/windowcut_b*', '**/windowcut_c*', '**/windowcut_d*', '**/windowcut_e*', '**/windowcut_f*')
RoomNames = ('**/group2', '**/group1')
WallNames = ('ceiling*', 'wall_side_middle*', 'wall_front_middle*', 'windowcut_*')
MouldingNames = ('wall_side_top*', 'wall_front_top*')
FloorNames = ('floor*',)
WainscotingNames = ('wall_side_bottom*', 'wall_front_bottom*')
BorderNames = ('wall_side_middle*_border', 'wall_front_middle*_border', 'windowcut_*_border')
WallpaperPieceNames = (WallNames,
 MouldingNames,
 FloorNames,
 WainscotingNames,
 BorderNames)

class EstateInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)
        self.interiorFile = 'phase_5.5/models/estate/tt_m_ara_int_estateHouseA'

    def load(self):
        Interior.load(self)
        doorOrigin = self.interior.find('**/door_origin')
        doorOrigin.setHpr(180, 0, 0)
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        self.door.setColor(0.651, 0.376, 0.31)
        self.interior.flattenMedium()

        self.loadWallpaper()

        self.acceptOnce('avatarExitDone', self.startActive)

    def loadWallpaper(self):
        for wall in WallNames + WainscotingNames: # For now, just make the house unoccupied.
            nodes = self.interior.findAllMatches('**/%s' % wall)
            for node in nodes:
                node.setTextureOff(1)

    def unload(self):
        Interior.unload(self)
