from direct.showbase.ShowBase import ShowBase
from toontown.toonbase import ToontownGlobals
from libotp.nametag.MarginManager import MarginManager
from panda3d.core import *
from libotp import *
from toontown.misc import Injector
from direct.gui import DirectGuiGlobals
import builtins
builtins.settings = {'musicVol': 1.0} #fake settings

class ProtoBase(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        builtins.loader = self.loader
        from prototypes.combat import ProtoGame
        self.initDirectGUIGlobals()
        CullBinManager.getGlobalPtr().addBin('shadow', CullBinManager.BTFixed, 15)
        CullBinManager.getGlobalPtr().addBin('ground', CullBinManager.BTFixed, 14)
        injector = Injector.Injector()
        injector.daemon = True
        injector.start()
        from toontown.toonbase.MusicManager import MusicManager
        builtins.musicMgr = MusicManager()
        self.wantNametags = self.config.GetBool('want-nametags', 1)
        self.initNametagGlobals()
        self.game = ProtoGame.ProtoGame()

    def initDirectGUIGlobals(self):
        DirectGuiGlobals.setDefaultRolloverSound(loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
        DirectGuiGlobals.setDefaultClickSound(loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
        DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui.bam'))
        DirectGuiGlobals.setDefaultFont(ToontownGlobals.getInterfaceFont())

    def initNametagGlobals(self): #copied from ToonBase
        arrow = loader.loadModel('phase_3/models/props/arrow')
        card = loader.loadModel('phase_3/models/props/panel')
        speech3d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox'))
        thought3d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox_thought_cutout'))
        speech2d = ChatBalloon(loader.loadModel('phase_3/models/props/chatbox_noarrow'))
        chatButtonGui = loader.loadModel('phase_3/models/gui/chat_button_gui')
        NametagGlobals.setCamera(self.cam)
        NametagGlobals.setArrowModel(arrow)
        NametagGlobals.setNametagCard(card, VBase4(-0.5, 0.5, -0.5, 0.5))
        if self.mouseWatcherNode:
            NametagGlobals.setMouseWatcher(self.mouseWatcherNode)
        NametagGlobals.setSpeechBalloon3d(speech3d)
        NametagGlobals.setThoughtBalloon3d(thought3d)
        NametagGlobals.setSpeechBalloon2d(speech2d)
        NametagGlobals.setThoughtBalloon2d(thought3d)
        NametagGlobals.setPageButton(PGButton.SReady, chatButtonGui.find('**/Horiz_Arrow_UP'))
        NametagGlobals.setPageButton(PGButton.SDepressed, chatButtonGui.find('**/Horiz_Arrow_DN'))
        NametagGlobals.setPageButton(PGButton.SRollover, chatButtonGui.find('**/Horiz_Arrow_Rllvr'))
        NametagGlobals.setQuitButton(PGButton.SReady, chatButtonGui.find('**/CloseBtn_UP'))
        NametagGlobals.setQuitButton(PGButton.SDepressed, chatButtonGui.find('**/CloseBtn_DN'))
        NametagGlobals.setQuitButton(PGButton.SRollover, chatButtonGui.find('**/CloseBtn_Rllvr'))
        rolloverSound = DirectGuiGlobals.getDefaultRolloverSound()
        if rolloverSound:
            NametagGlobals.setRolloverSound(rolloverSound)
        clickSound = DirectGuiGlobals.getDefaultClickSound()
        if clickSound:
            NametagGlobals.setClickSound(clickSound)
        NametagGlobals.setToon(self.cam)
        self.marginManager = MarginManager()
        self.margins = self.aspect2d.attachNewNode(self.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
        mm = self.marginManager
        self.leftCells = [mm.addGridCell(0, 1, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -1.5)), mm.addGridCell(0, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -1.16667)), mm.addGridCell(0, 3, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopLeft, (0.222222, 0, -0.833333))]
        self.bottomCells = [mm.addGridCell(1.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (-0.8, 0, 0.166667)), mm.addGridCell(3.5, 0, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dBottomCenter, (0.8, 0, 0.166667))]
        self.rightCells = [mm.addGridCell(5, 1, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopRight, (-0.222222, 0, -1.5)), mm.addGridCell(5, 2, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopRight, (-0.222222, 0, -1.16667)), mm.addGridCell(5, 3, -1.33333333333, 1.33333333333, -1.0, 1.0, base.a2dTopRight, (-0.222222, 0, -0.833333))]
