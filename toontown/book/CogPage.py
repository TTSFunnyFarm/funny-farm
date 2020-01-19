from toontown.book import ShtikerPage
from direct.task.Task import Task
#from . import SummonCogDialog
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.suit import SuitDNA
from toontown.suit import Suit
from toontown.battle import SuitBattleGlobals
from toontown.book.CogPageGlobals import *
SCALE_FACTOR = 1.5
RADAR_DELAY = 0.2
BUILDING_RADAR_POS = (0.375,
 0.065,
 -0.225,
 -0.5)
PANEL_COLORS = (Vec4(0.8, 0.78, 0.77, 1),
 Vec4(0.75, 0.78, 0.8, 1),
 Vec4(0.75, 0.82, 0.79, 1),
 Vec4(0.825, 0.76, 0.77, 1))
PANEL_COLORS_COMPLETE1 = (Vec4(0.7, 0.725, 0.545, 1),
 Vec4(0.625, 0.725, 0.65, 1),
 Vec4(0.6, 0.75, 0.525, 1),
 Vec4(0.675, 0.675, 0.55, 1))
PANEL_COLORS_COMPLETE2 = (Vec4(0.9, 0.725, 0.32, 1),
 Vec4(0.825, 0.725, 0.45, 1),
 Vec4(0.8, 0.75, 0.325, 1),
 Vec4(0.875, 0.675, 0.35, 1))
SHADOW_SCALE_POS = ((1.225,
  0,
  10,
  -0.03),
 (0.9,
  0,
  10,
  0),
 (1.125,
  0,
  10,
  -0.015),
 (1.0,
  0,
  10,
  -0.02),
 (1.0,
  -0.02,
  10,
  -0.01),
 (1.05,
  0,
  10,
  -0.0425),
 (1.0,
  0,
  10,
  -0.05),
 (0.9,
  -0.0225,
  10,
  -0.025),
 (1.25,
  0,
  10,
  -0.03),
 (1.0,
  0,
  10,
  -0.01),
 (1.0,
  0.005,
  10,
  -0.01),
 (1.0,
  0,
  10,
  -0.01),
 (0.9,
  0.005,
  10,
  -0.01),
 (0.95,
  0,
  10,
  -0.01),
 (1.125,
  0.005,
  10,
  -0.035),
 (0.85,
  -0.005,
  10,
  -0.035),
 (1.2,
  0,
  10,
  -0.01),
 (1.05,
  0,
  10,
  0),
 (1.1,
  0,
  10,
  -0.04),
 (1.0,
  0,
  10,
  0),
 (0.95,
  0.0175,
  10,
  -0.015),
 (1.0,
  0,
  10,
  -0.06),
 (0.95,
  0.02,
  10,
  -0.0175),
 (0.9,
  0,
  10,
  -0.03),
 (1.15,
  0,
  10,
  -0.01),
 (1.0,
  0,
  10,
  0),
 (1.0,
  0,
  10,
  0),
 (1.1,
  0,
  10,
  -0.04),
 (0.93,
  0.005,
  10,
  -0.01),
 (0.95,
  0.005,
  10,
  -0.01),
 (1.0,
  0,
  10,
  -0.02),
 (0.9,
  0.0025,
  10,
  -0.03))

class CogPage(ShtikerPage.ShtikerPage):

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        frameModel = loader.loadModel('phase_3.5/models/gui/suitpage_frame')
        frameModel.setScale(0.03375, 1, 0.045)
        frameModel.setPos(0, 10, -0.575)
        self.guiTop = NodePath('guiTop')
        self.guiTop.reparentTo(self)
        self.frameNode = NodePath('frameNode')
        self.frameNode.reparentTo(self.guiTop)
        self.panelNode = NodePath('panelNode')
        self.panelNode.reparentTo(self.guiTop)
        self.iconNode = NodePath('iconNode')
        self.iconNode.reparentTo(self.guiTop)
        self.enlargedPanelNode = NodePath('enlargedPanelNode')
        self.enlargedPanelNode.reparentTo(self.guiTop)
        frame = frameModel.find('**/frame')
        frame.wrtReparentTo(self.frameNode)
        screws = frameModel.find('**/screws')
        screws.wrtReparentTo(self.iconNode)
        icons = frameModel.find('**/icons')
        del frameModel
        self.title = DirectLabel(parent=self.iconNode, relief=None, text=TTLocalizer.SuitPageTitle, text_scale=0.1, text_pos=(0.04, 0), textMayChange=0)
        self.radarButtons = []
        icon = icons.find('**/corp_icon')
        self.corpRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=icon, image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.575), command=self.toggleRadar, extraArgs=[0])
        self.radarButtons.append(self.corpRadarButton)
        icon = icons.find('**/legal_icon')
        self.legalRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=icon, image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.575), command=self.toggleRadar, extraArgs=[1])
        self.radarButtons.append(self.legalRadarButton)
        icon = icons.find('**/money_icon')
        self.moneyRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=(icon, icon, icon), image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.575), command=self.toggleRadar, extraArgs=[2])
        self.radarButtons.append(self.moneyRadarButton)
        icon = icons.find('**/sales_icon')
        self.salesRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=(icon, icon, icon), image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.575), command=self.toggleRadar, extraArgs=[3])
        self.radarButtons.append(self.salesRadarButton)
        for radarButton in self.radarButtons:
            radarButton.building = 0
            radarButton.buildingRadarLabel = None

        gui = loader.loadModel('phase_3.5/models/gui/suitpage_gui')
        self.panelModel = gui.find('**/card')
        self.shadowModels = []
        for index in range(1, len(SuitDNA.suitHeadTypes) + 1):
            self.shadowModels.append(gui.find('**/shadow' + str(index)))

        del gui
        self.makePanels()
        self.radarOn = [0,
         0,
         0,
         0]
        priceScale = 0.1
        emblemIcon = loader.loadModel('phase_3.5/models/gui/tt_m_gui_gen_emblemIcons')
        silverModel = emblemIcon.find('**/tt_t_gui_gen_emblemSilver')
        goldModel = emblemIcon.find('**/tt_t_gui_gen_emblemGold')
        self.silverLabel = DirectLabel(parent=self, relief=None, pos=(-0.25, 0, -0.69), scale=priceScale, image=silverModel, image_pos=(-0.4, 0, 0.4), text=str(localAvatar.emblems[ToontownGlobals.EmblemTypes.Silver]), text_fg=(0.95, 0.95, 0, 1), text_shadow=(0, 0, 0, 1), text_font=ToontownGlobals.getSignFont(), text_align=TextNode.ALeft)
        self.goldLabel = DirectLabel(parent=self, relief=None, pos=(0.25, 0, -0.69), scale=priceScale, image=goldModel, image_pos=(-0.4, 0, 0.4), text=str(localAvatar.emblems[ToontownGlobals.EmblemTypes.Gold]), text_fg=(0.95, 0.95, 0, 1), text_shadow=(0, 0, 0, 1), text_font=ToontownGlobals.getSignFont(), text_align=TextNode.ALeft)
        if not base.cr.wantEmblems:
            self.silverLabel.hide()
            self.goldLabel.hide()
        self.accept(localAvatar.uniqueName('emblemsChange'), self.__emblemChange)
        self.guiTop.setZ(0.625)
        return

    def unload(self):
        self.ignoreAll()
        self.title.destroy()
        self.corpRadarButton.destroy()
        self.legalRadarButton.destroy()
        self.moneyRadarButton.destroy()
        self.salesRadarButton.destroy()
        for panel in self.panels:
            panel.destroy()

        del self.panels
        for shadow in self.shadowModels:
            shadow.removeNode()

        self.panelModel.removeNode()
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        self.updatePage()
        self.bigPanel = None
        self.nextPanel = None
        ShtikerPage.ShtikerPage.enter(self)
        return

    def exit(self):
        taskMgr.remove('buildingListResponseTimeout-later')
        taskMgr.remove('suitListResponseTimeout-later')
        taskMgr.remove('showCogRadarLater')
        taskMgr.remove('showBuildingRadarLater')
        for index in range(0, len(self.radarOn)):
            if self.radarOn[index]:
                self.toggleRadar(index)
                self.radarButtons[index]['state'] = DGG.NORMAL

        ShtikerPage.ShtikerPage.exit(self)

    def resetPanel(self, dept, type):
        panel = self.panels[dept * SuitDNA.suitsPerDept + type]
        panel['text'] = TTLocalizer.SuitPageMystery
        if panel.cogRadarLabel:
            panel.cogRadarLabel.hide()
        if panel.quotaLabel:
            panel.quotaLabel.hide()
        if panel.head:
            panel.head.hide()
        if panel.shadow:
            panel.shadow.hide()
        if panel.summonButton:
            panel.summonButton.hide()
        color = PANEL_COLORS[dept]
        panel['image_color'] = color
        for button in self.radarButtons:
            if button.buildingRadarLabel:
                button.buildingRadarLabel.hide()

    def setPanelStatus(self, panel, status):
        index = self.panels.index(panel)
        if status == COG_UNSEEN:
            panel['text'] = TTLocalizer.SuitPageMystery
        elif status == COG_BATTLED:
            suitName = SuitDNA.suitHeadTypes[index]
            suitFullName = SuitBattleGlobals.SuitAttributes[suitName]['name']
            panel['text'] = suitFullName
            if panel.quotaLabel:
                panel.quotaLabel.show()
            else:
                self.addQuotaLabel(panel)
            if panel.head and panel.shadow:
                panel.head.show()
                panel.shadow.show()
            else:
                self.addSuitHead(panel, suitName)
            if base.localAvatar.hasCogSummons(index):
                if panel.summonButton:
                    panel.summonButton.show()
                else:
                    self.addSummonButton(panel)
        elif status == COG_DEFEATED:
            count = str(base.localAvatar.cogCounts[index])
            if base.localAvatar.cogs[index] < COG_COMPLETE1:
                quota = str(COG_QUOTAS[0][index % SuitDNA.suitsPerDept])
            else:
                quota = str(COG_QUOTAS[1][index % SuitDNA.suitsPerDept])
            panel.quotaLabel['text'] = TTLocalizer.SuitPageQuota % (count, quota)
        elif status == COG_COMPLETE1:
            panel['image_color'] = PANEL_COLORS_COMPLETE1[index / SuitDNA.suitsPerDept]
        elif status == COG_COMPLETE2:
            panel['image_color'] = PANEL_COLORS_COMPLETE2[index / SuitDNA.suitsPerDept]

    def updateAllCogs(self, status):
        for index in range(0, len(base.localAvatar.cogs)):
            base.localAvatar.cogs[index] = status

        self.updatePage()

    def updatePage(self):
        index = 0
        cogs = base.localAvatar.cogs
        for dept in range(0, len(SuitDNA.suitDepts)):
            for type in range(0, SuitDNA.suitsPerDept):
                self.updateCogStatus(dept, type, cogs[index])
                index += 1

        self.updateCogRadarButtons(base.localAvatar.cogRadar)
        self.updateBuildingRadarButtons(base.localAvatar.buildingRadar)

    def updateCogStatus(self, dept, type, status):
        if dept < 0 or dept > len(SuitDNA.suitDepts):
            print('ucs: bad cog dept: ', dept)
        elif type < 0 or type > SuitDNA.suitsPerDept:
            print('ucs: bad cog type: ', type)
        elif status < COG_UNSEEN or status > COG_COMPLETE2:
            print('ucs: bad status: ', status)
        else:
            self.resetPanel(dept, type)
            panel = self.panels[dept * SuitDNA.suitsPerDept + type]
            if status == COG_UNSEEN:
                self.setPanelStatus(panel, COG_UNSEEN)
            elif status == COG_BATTLED:
                self.setPanelStatus(panel, COG_BATTLED)
            elif status == COG_DEFEATED:
                self.setPanelStatus(panel, COG_BATTLED)
                self.setPanelStatus(panel, COG_DEFEATED)
            elif status == COG_COMPLETE1:
                self.setPanelStatus(panel, COG_BATTLED)
                self.setPanelStatus(panel, COG_DEFEATED)
                self.setPanelStatus(panel, COG_COMPLETE1)
            elif status == COG_COMPLETE2:
                self.setPanelStatus(panel, COG_BATTLED)
                self.setPanelStatus(panel, COG_DEFEATED)
                self.setPanelStatus(panel, COG_COMPLETE2)
