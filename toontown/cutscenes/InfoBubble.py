from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.quest import Quests
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toon import NPCToons, ToonDNA, ToonHead

class InfoBubble(DirectFrame):
    notify = directNotify.newCategory('InfoBubble')

    def __init__(self):
        DirectFrame.__init__(self, parent=base.a2dBottomCenter, relief=None)
        self.initialiseoptions(DirectFrame)
        self.icon = None
        self.currText = None

    def enter(self, index, doneEvent, npcId=0):
        self.showDialog(index, npcId)
        self.doneEvent = doneEvent

    def exit(self):
        self.nextButton.hide()
        self.okButton.hide()
        Sequence(self.bubble.scaleInterval(0.1, (0.16, 1.0, 0.16), blendType='easeInOut'), self.bubble.scaleInterval(0.3, (0.01, 1.0, 0.01), blendType='easeInOut'), Func(self.hideDialog), Func(messenger.send, self.doneEvent)).start()

    def load(self):
        bubbleGui = loader.loadModel('phase_3/models/props/chatbox_noarrow.bam')
        buttonGui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        nextButtonUp = buttonGui.find('**/tt_t_gui_mat_nextUp')
        nextButtonDown = buttonGui.find('**/tt_t_gui_mat_nextDown')
        okButtonUp = buttonGui.find('**/tt_t_gui_mat_okUp')
        okButtonDown = buttonGui.find('**/tt_t_gui_mat_okDown')
        self.bubble = DirectFrame(parent=self, relief=None, image=bubbleGui, pos=(-0.75, 0, -0.05), scale=(0.14, 1.0, 0.14))
        self.nextButton = DirectButton(parent=self.bubble, relief=None, image=(nextButtonUp, nextButtonDown, nextButtonUp),
         image_scale=(1.3, 1.3, 1.3), image1_scale=(1.4, 1.4, 1.4), image2_scale=(1.4, 1.4, 1.4), pos=(9.8, 0, 1.8))
        self.nextButton.hide()
        self.okButton = DirectButton(parent=self.bubble, relief=None, image=(okButtonUp, okButtonDown, okButtonUp),
         image_scale=(2.3, 2.3, 2.3), image1_scale=(2.4, 2.4, 2.4), image2_scale=(2.4, 2.4, 2.4), pos=(9.8, 0, 1.8), command=self.exit)
        self.okButton.hide()
        self.dialog = DirectLabel(parent=self.bubble, relief=None, text='', text_font=ToontownGlobals.getInterfaceFont(),
         pos=(2.9, 0, 2.7), scale=0.4, text_align=TextNode.ALeft, text_wordwrap=16)
        bubbleGui.removeNode()
        buttonGui.removeNode()
        self.hide()

    def unload(self):
        self.bubble.destroy()
        self.nextButton.destroy()
        self.okButton.destroy()
        self.dialog.destroy()
        del self.bubble
        del self.nextButton
        del self.okButton
        del self.dialog

    def showDialog(self, index, npcId=0):
        gui = loader.loadModel('phase_6/models/karting/rim_textures.bam')
        if npcId > 0:
            self.icon = gui.find('**/kart_Rim_5')
            head = self.displayHead(npcId)
            if head:
                head.reparentTo(self.icon)
                head.setPos(0, 0, -0.13)
                head.setHpr(180, 0, 0)
                head.setScale(0.45, 0.45, 0.45)
        else:
            self.icon = gui.find('**/kart_Rim_7')
        self.icon.reparentTo(self.bubble)
        self.icon.setPos(1.5, 0, 2.5)
        self.icon.setScale(1.5)
        gui.removeNode()
        if index > 1000:
            dialog = TTLocalizer.CutsceneDialogDict[index]
        else:
            dialog = TTLocalizer.InfoBubbleDialog[index]
        dialog = Quests.fillInQuestNames(dialog, avName=base.avatarData.setName)
        self.currText = dialog
        self.setPageNumber(0)
        self.bubble.setScale(0.01, 0.01, 0.01)
        self.show()
        Sequence(self.bubble.scaleInterval(0.3, (0.16, 1.0, 0.16), blendType='easeInOut'), self.bubble.scaleInterval(0.1, (0.14, 1.0, 0.14), blendType='easeInOut')).start()

    def hideDialog(self):
        self.icon.removeNode()
        self.icon = None
        self.currText = None
        self.dialog['text'] = ''
        self.nextButton.hide()
        self.okButton.hide()
        self.hide()

    def setPageNumber(self, pageNumber):
        pages = self.currText.split('\x07')
        text = pages[pageNumber]
        self.dialog['text'] = text
        if pageNumber == (len(pages) - 1):
            self.nextButton.hide()
            self.okButton.show()
        else:
            self.nextButton.show()
            self.okButton.hide()
            self.nextButton['command'] = self.setPageNumber
            self.nextButton['extraArgs'] = [pageNumber + 1]
        messenger.send('nextInfoPage')

    def displayHead(self, npcId):
        if npcId not in NPCToons.NPCToonDict:
            return None
        head = hidden.attachNewNode('head')
        desc = NPCToons.NPCToonDict[npcId]
        canonicalZoneId, name, dnaType, gender, accessories, protected, type = desc
        headModel = ToonHead.ToonHead()
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(*dnaType)
        headModel.setupHead(dna, forGui=1)
        headModel.reparentTo(head)
        animalStyle = dna.getAnimal()
        bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
        headModel.setScale(bodyScale / 0.75)
        return head
