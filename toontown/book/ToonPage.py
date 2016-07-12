from panda3d.core import *
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toon import Toon
import ShtikerPage

GagIconPoints = [
    (-0.5, 0, 0),
    (-0.3, 0, 0),
    (-0.1, 0, 0),
    (0.1, 0, 0),
    (0.3, 0, 0),
    (0.5, 0, 0)
]
SuitIconPoints = [
    (-3.0, 0, 0),
    (-1.0, 0, 0),
    (1.0, 0, 0),
    (3.0, 0, 0)
]

class ToonPage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('ToonPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

    def load(self):
        ShtikerPage.ShtikerPage.load(self)

        invGui = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        self.gagIcons = [
            invGui.find('**/inventory_bannana_peel'), # goddammit disney you had 1 job
            invGui.find('**/inventory_1dollarbill'),
            invGui.find('**/inventory_bikehorn'),
            invGui.find('**/inventory_tart'),
            invGui.find('**/inventory_water_gun'),
            invGui.find('**/inventory_flower_pot')
        ]
        suitGui = loader.loadModel('phase_3/models/gui/cog_icons')
        self.suitIcons = [
            suitGui.find('**/SalesIcon'),
            suitGui.find('**/MoneyIcon'),
            suitGui.find('**/LegalIcon'),
            suitGui.find('**/CorpIcon')
        ]
        invGui.removeNode()
        suitGui.removeNode()
        panel = loader.loadModel('phase_4/models/gui/gag_shop_purchase_gui').find('**/Goofys_Sign')
        self.title = DirectFrame(
         parent=self, relief=None, image=panel, image_scale=0.8, text=base.localAvatar.getName(),
         text_scale=0.08, pos=(0, 0, 0.61), text_wordwrap=12)

        self.damagePanel = DirectFrame(parent=self, relief=None, image=panel, image_scale=(0.6, 1.0, 0.7),
         pos=(0.42, 0, 0.3), text=TTLocalizer.ToonPageDamage, text_scale=0.06, text_pos=(0, 0.11, 0))
        self.damageIcons = DirectFrame(parent=self.damagePanel, relief=None, scale=0.6, pos=(0, 0, 0.05))
        for x in self.gagIcons:
            geom = x.copyTo(self.damageIcons)
            geom.setPos(GagIconPoints[self.gagIcons.index(x)])

        self.defensePanel = DirectFrame(parent=self, relief=None, image=panel, image_scale=(0.6, 1.0, 0.7),
         pos=(0.42, 0, 0), text=TTLocalizer.ToonPageDefense, text_scale=0.06, text_pos=(0, 0.11, 0))
        self.defenseIcons = DirectFrame(parent=self.defensePanel, relief=None, scale=0.07, pos=(0, 0, 0.05))
        for x in self.suitIcons:
            geom = x.copyTo(self.defenseIcons)
            geom.setPos(SuitIconPoints[self.suitIcons.index(x)])

        self.accuracyPanel = DirectFrame(parent=self, relief=None, image=panel, image_scale=(0.6, 1.0, 0.7),
         pos=(0.42, 0, -0.3), text=TTLocalizer.ToonPageAccuracy, text_scale=0.06, text_pos=(0, 0.11, 0))
        self.accuracyIcons = DirectFrame(parent=self.accuracyPanel, relief=None, scale=0.6, pos=(0, 0, 0.05))
        for x in self.gagIcons:
            geom = x.copyTo(self.accuracyIcons)
            geom.setPos(GagIconPoints[self.gagIcons.index(x)])

        self.toonFrame = DirectFrame(parent=self, relief=None, image=loader.loadModel('phase_3.5/models/modules/trophy_frame'),
         pos=(-0.45, 0, 0.2), scale=0.25)
        self.toon = Toon.Toon()
        self.toon.setDNA(base.localAvatar.style)
        self.toon.reparentTo(self.toonFrame)
        height = self.toon.getHeight()
        if height <= 3.0:
            bodyScale = 0.4
            zzFactor = -0.22
        elif height > 3.0 and height <= 4.0:
            bodyScale = 0.36
            zzFactor = -0.19
        else:
            bodyScale = 0.3
            zzFactor = -0.16
        self.toon.setPos(0, 0, height * zzFactor)
        self.toon.setScale(bodyScale)
        self.toon.getGeomNode().setDepthWrite(1)
        self.toon.getGeomNode().setDepthTest(1)
        self.toon.loop('neutral')
        self.toon.startBlink()
        self.toon.hprInterval(10, (360, 0, 0)).loop()

        self.level = DirectLabel(parent=self, relief=None, text=(TTLocalizer.ToonPageLevel % base.localAvatar.getLevel()),
         pos=(-0.45, 0, -0.25), scale=0.08)
        # TODO: add exp wait bar

    def unload(self):
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        self.updateToonStats()

    def exit(self):
        ShtikerPage.ShtikerPage.exit(self)
        self.cleanupToonStats()

    def updateToonStats(self):
        for x in self.gagIcons:
            DirectLabel(parent=self.damageIcons.find('**/%s' % x.getName()), relief=None,
             text=str(base.localAvatar.damage[self.gagIcons.index(x)]), scale=0.08, pos=(0, 0, -0.15))
            DirectLabel(parent=self.accuracyIcons.find('**/%s' % x.getName()), relief=None,
             text=str(base.localAvatar.accuracy[self.gagIcons.index(x)]), scale=0.08, pos=(0, 0, -0.15))
        for x in self.suitIcons:
            DirectLabel(parent=self.defenseIcons.find('**/%s' % x.getName()), relief=None,
             text=str(base.localAvatar.defense[self.suitIcons.index(x)]), scale=0.73, pos=(0, 0, -1.25))
        self.level['text'] = TTLocalizer.ToonPageLevel % base.localAvatar.getLevel()
        return

    def cleanupToonStats(self):
        for x in self.gagIcons:
            damage = self.damageIcons.find('**/%s/DirectLabel*' % x.getName())
            if not damage.isEmpty():
                damage.removeNode()
            accuracy = self.accuracyIcons.find('**/%s/DirectLabel*' % x.getName())
            if not accuracy.isEmpty():
                accuracy.removeNode()
        for x in self.suitIcons:
            defense = self.defenseIcons.find('**/%s/DirectLabel*' % x.getName())
            if not defense.isEmpty():
                defense.removeNode()
