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
        self.allZones = [FunnyFarmGlobals.FunnyFarm]
        self.cloudScaleList = ((0.55, 0.0, 0.35),
         (-0.6, 0.0, 0.4),
         (0.65, 0.0, 0.4),
         (0.65, 0.0, 0.35),
         (0.5, 0.0, 0.35),
         (0.65, 0.0, 0.35),
         (0.65, 0.0, 0.4),
         (0.5, 0.0, 0.35),
         (0.65, 0.0, 0.35),
         (0.5, 0.0, 0.32),
         (0.5, 0.0, 0.4),
         (0.5, 0.0, 0.4),
         (-0.5, 0.0, 0.32),
         (0.65, 0.0, 0.35))
        self.cloudPosList = ((0.48, 0.0, -0.4),
         (-0.5, 0.0, -0.4),
         (-0.5, 0.0, -0.15),
         (0.0, 0.0, 0.1),
         (0.2, 0.0, -0.02),
         (0.54, 0.0, 0.08),
         (0.5, 0.0, -0.15),
         (-0.2, 0.0, -0.02),
         (-0.54, 0.0, 0.08),
         (-0.25, 0.0, 0.28),
         (0.59, 0.0, 0.4),
         (-0.59, 0.0, 0.4),
         (0.25, 0.0, 0.28),
         (0.0, 0.0, 0.47))
        self.labelPosList = ((0.0, 0.0, -0.4),)
        self.labels = []
        self.clouds = []
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        buttonLoc = (0.45, 0, -0.74)
        # if base.housingEnabled:
            # buttonLoc = (0.55, 0, -0.74)
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
            pos=(0.15, 0, -.74),
            text=TTLocalizer.MapPageGoHome,
            text_scale=TTLocalizer.MPgoHomeButton,
            text_pos=(0, -0.02),
            textMayChange=0)
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
        for hood in self.allZones:
            fullname = FunnyFarmGlobals.hoodNameMap[hood]
            hoodIndex = self.allZones.index(hood)
            label = DirectButton(
                parent=self.map,
                relief=None,
                pos=self.labelPosList[hoodIndex],
                pad=(0.2, 0.16),
                text=('', fullname, fullname),
                text_bg=Vec4(1, 1, 1, 0.4),
                text_scale=0.055,
                text_wordwrap=8,
                rolloverSound=None,
                clickSound=None,
                pressEffect=0,
                command=self.__buttonCallback,
                extraArgs=[hood],
                sortOrder=1)
            label.resetFrameSize()
            self.labels.append(label)
        cloudModel = loader.loadModel('phase_3.5/models/gui/cloud')
        cloudImage = cloudModel.find('**/cloud')
        for i in xrange(len(self.cloudScaleList)):
            cloudScale = self.cloudScaleList[i]
            cloudPos = self.cloudPosList[i]
            cloud = DirectFrame(
                parent=self.map,
                relief=None,
                state=DGG.DISABLED,
                image=cloudImage,
                scale=(cloudScale[0], cloudScale[1], cloudScale[2]),
                pos=(cloudPos[0], cloudPos[1], cloudPos[2]))
            # cloud.hide()
            self.clouds.append(cloud)
        cloudModel.removeNode()
        self.resetFrameSize()

    def unload(self):
        for labelButton in self.labels:
            labelButton.destroy()
        del self.labels
        del self.clouds
        self.safeZoneButton.destroy()
        self.goHomeButton.destroy()
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        if base.cr.playGame.hood:
            if base.cr.playGame.hood.place:
                self.safeZoneButton.show()
            else:
                self.safeZoneButton.hide()
        else:
            self.safeZoneButton.show()
        zoneId = base.localAvatar.getZoneId()
        hoodName = FunnyFarmGlobals.hoodNameMap.get(FunnyFarmGlobals.getHoodId(zoneId), '')
        streetName = FunnyFarmGlobals.StreetNames.get(zoneId, '')
        self.hoodLabel.show()
        self.hoodLabel['text'] = TTLocalizer.MapPageYouAreHere % (hoodName, streetName)
        safeZonesVisited = base.localAvatar.hoodsVisited
        hoodTeleportList = base.localAvatar.getTeleportAccess()
        for hood in self.allZones:
            label = self.labels[self.allZones.index(hood)]
            # clouds = self.clouds[self.allZones.index(hood)]
            if hood in safeZonesVisited:
                label['text_fg'] = (0, 0, 0, 1)
                label.show()
                # for cloud in clouds:
                #     cloud.hide()

                fullname = FunnyFarmGlobals.hoodNameMap[hood]
                if hood in hoodTeleportList:
                    text = TTLocalizer.MapPageGoTo % fullname
                    label['text'] = ('', text, text)
                else:
                    label['text'] = ('', fullname, fullname)
            else:
                label.hide()
                # for cloud in clouds:
                #     cloud.show()
        self.accept('safeZoneTeleport', self.book.teleportTo)

    def exit(self):
        ShtikerPage.ShtikerPage.exit(self)

    def backToSafeZone(self):
        zoneId = base.localAvatar.getZoneId()
        hoodId = FunnyFarmGlobals.getHoodId(zoneId)
        messenger.send('safeZoneTeleport', [hoodId])

    def goHome(self):
        pass

    def __buttonCallback(self, hood):
        if hood in base.localAvatar.getTeleportAccess():
            messenger.send('safeZoneTeleport', [hood])
