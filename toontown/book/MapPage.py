from panda3d.core import *
from direct.gui.DirectGui import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
import ShtikerPage

class MapPage(ShtikerPage.ShtikerPage):

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        mapModel = loader.loadModel('phase_3.5/models/gui/toontown_map')
        self.map = DirectFrame(parent=self, relief=None, image=mapModel.find('**/toontown_map'), image_scale=(1.8, 1, 1.35), scale=0.97, pos=(0, 0, 0.0775))
        mapModel.removeNode()

        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        buttonLoc = (0.45, 0, -0.74)
        #if base.housingEnabled:
                #buttonLoc = (0.55, 0, -0.74)
        self.safeZoneButton = DirectButton(
                parent=self.map,
                relief=None,
                image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')),
                image_scale=(1.3, 1.1, 1.1),
                pos=buttonLoc,
                text=TTLocalizer.MapPageBackToPlayground,
                text_scale=TTLocalizer.MPsafeZoneButton,
                text_pos=(0, -0.02),
                textMayChange=0,
                command=self.backToSafeZone)
        self.goHomeButton = DirectButton(
                parent=self.map,
                relief=None,
                image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')),
                image_scale=(0.66, 1.1, 1.1),
                pos=(0.075, 0, -.74),
                text=TTLocalizer.MapPageGoHome,
                text_scale=TTLocalizer.MPgoHomeButton,
                text_pos=(0, -0.02),
                textMayChange=0,
                command=self.goHome)
        self.goHomeButton.hide()
        guiButton.removeNode()
        self.hoodLabel = DirectLabel(
                parent=self.map,
                relief=None,
                pos=(-0.43, 0, -0.726),
                text='',
                text_scale=TTLocalizer.MPhoodLabel,
                text_pos=(0, 0),
                text_wordwrap=TTLocalizer.MPhoodLabelWordwrap)
        self.hoodLabel.hide()

    def unload(self):
        self.safeZoneButton.destroy()
        self.goHomeButton.destroy()
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        if base.cr.playGame.hood:
            if base.cr.playGame.hood.place:
                self.safeZoneButton.show()
                self.goHomeButton.show()
            elif base.cr.playGame.hood.zoneId == FunnyFarmGlobals.Estate:
                self.safeZoneButton.show()
                self.goHomeButton.hide()
            else:
                self.safeZoneButton.hide()
                self.goHomeButton.show()
        else:
            self.safeZoneButton.show()
            self.goHomeButton.show()
        zoneId = base.localAvatar.getZoneId()
        hoodName = FunnyFarmGlobals.hoodNameMap.get(FunnyFarmGlobals.getHoodId(zoneId), '')
        streetName = FunnyFarmGlobals.StreetNames.get(zoneId, '')
        self.hoodLabel.show()
        self.hoodLabel['text'] = TTLocalizer.MapPageYouAreHere % (hoodName, streetName)
        self.accept('safeZoneTeleport', self.book.teleportTo)

    def exit(self):
        ShtikerPage.ShtikerPage.exit(self)

    def backToSafeZone(self):
        zoneId = base.localAvatar.getZoneId()
        hoodId = FunnyFarmGlobals.getHoodId(zoneId)
        if hoodId == FunnyFarmGlobals.Estate: # That's not it...
            hoodId = base.avatarData.setLastHood # Go to the last hood they were in.
            if hoodId == FunnyFarmGlobals.Estate: # Huh?
                hoodId = FunnyFarmGlobals.FunnyFarm
        messenger.send('safeZoneTeleport', [hoodId])

    def goHome(self):
        messenger.send('safeZoneTeleport', [FunnyFarmGlobals.Estate])
