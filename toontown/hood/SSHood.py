from pandac.PandaModules import *
from direct.actor.Actor import Actor
from ToonHood import ToonHood
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.building import Door
from toontown.trolley import Trolley

class SSHood(ToonHood):

    def __init__(self):
        ToonHood.__init__(self)
        self.zoneId = FunnyFarmGlobals.SillySprings
        self.TTZoneId = ToontownGlobals.DaisyGardens
        self.hoodFile = 'phase_14/models/neighborhoods/silly_springs'
        self.spookyHoodFile = 'phase_14/models/neighborhoods/silly_springs_halloween'
        self.winterHoodFile = 'phase_14/models/neighborhoods/silly_springs_winter'
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleText = FunnyFarmGlobals.SSHoodText
        self.titleColor = (0.8, 0.6, 1.0, 1.0)

    def enter(self, shop=None, tunnel=None, init=False):
        musicMgr.startSSNbrhood()
        ToonHood.enter(self, shop=shop, tunnel=tunnel, init=init)
        if shop:
            if shop == 'ps':
                doorNP = self.geom.find('**/PetShopDoor')
            elif shop == 'gs':
                doorNP = self.geom.find('**/GagShopDoor')
            elif shop == 'hq0':
                doorNP = self.geom.find('**/door_0')
            elif shop == 'hq1':
                doorNP = self.geom.find('**/door_1')
            door = Door.Door(doorNP, shop, self.zoneId)
            door.avatarExit(base.localAvatar)
            self.acceptOnce('avatarExitDone', self.startActive)
            return
        if tunnel:
            tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
            base.localAvatar.tunnelIn(tunnelOrigin)
        self.startActive()

    def exit(self):
        musicMgr.stopSSNbrhood()
        ToonHood.exit(self)

    def load(self):
        ToonHood.load(self)
        self.sky.setScale(1.2)
        self.fish = Actor('phase_4/models/props/exteriorfish-zero', {'chan': 'phase_4/models/props/exteriorfish-swim'})
        self.fish.reparentTo(self.geom.find('**/fish_origin'))
        self.fish.loop('chan')
        self.trolley = Trolley.Trolley()
        self.trolley.setup()
        if not base.air.holidayMgr.isWinter() and not base.air.holidayMgr.isHalloween():
            self.startSkyTrack()

    def unload(self):
        if not base.air.holidayMgr.isWinter() and not base.air.holidayMgr.isHalloween():
            self.stopSkyTrack()
        ToonHood.unload(self)
        self.fish.stop()
        self.fish.cleanup()
        self.fish.removeNode()
        self.trolley.removeActive()
        self.trolley.delete()
        del self.fish
        del self.trolley

    def startActive(self):
        self.acceptOnce('enterRRTunnel_trigger', self.__handleRRTunnel)
        self.acceptOnce('enterPetShopDoorTrigger', self.__handlePetShop)
        self.acceptOnce('enterGagShopDoorTrigger', self.__handleGagShop)
        self.acceptOnce('enterdoor_trigger_0', self.__handleHQ, ['hq0'])
        self.acceptOnce('enterdoor_trigger_1', self.__handleHQ, ['hq1'])
        self.trolley.addActive()

    def __handlePetShop(self, entry):
        petDoor = self.geom.find('**/PetShopDoor')
        door = Door.Door(petDoor, 'ps', self.zoneId)
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.__handleEnterPetShop)

    def __handleEnterPetShop(self):
        base.cr.playGame.exitHood()
        base.cr.playGame.enterPetShop(self.zoneId)

    def __handleGagShop(self, entry):
        gagDoor = self.geom.find('**/GagShopDoor')
        door = Door.Door(gagDoor, 'gs', self.zoneId)
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.__handleEnterGagShop)

    def __handleEnterGagShop(self):
        base.cr.playGame.exitHood()
        base.cr.playGame.enterGagShop(self.zoneId)

    def __handleHQ(self, code, entry):
        if code == 'hq0':
            hqDoor = self.geom.find('**/door_0')
        else:
            hqDoor = self.geom.find('**/door_1')
        door = Door.Door(hqDoor, code, self.zoneId)
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.__handleEnterHQ, [code])

    def __handleEnterHQ(self, code):
        base.cr.playGame.exitHood()
        if code == 'hq0':
            base.cr.playGame.enterHQDoor0(self.zoneId)
        else:
            base.cr.playGame.enterHQDoor1(self.zoneId)

    def __handleRRTunnel(self, entry):
        tunnelOrigin = self.geom.find('**/RRTunnel').find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.__handleEnterRR)

    def __handleEnterRR(self):
        base.cr.playGame.exitHood()
        base.cr.playGame.enterRRStreet(tunnel='ss')
