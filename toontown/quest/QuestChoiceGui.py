from panda3d.core import *
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownTimer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.quest import Quests, QuestPoster

class QuestChoiceGui(DirectFrame):
    notify = directNotify.newCategory('QuestChoiceGui')

    def __init__(self):
        DirectFrame.__init__(self, relief=None, parent=base.a2dLeftCenter, geom=DGG.getDefaultDialogGeom(), geom_color=Vec4(0.8, 0.6, 0.4, 1), geom_scale=(1.85, 1, 0.9), geom_hpr=(0, 0, -90), pos=(0.5, 0, 0))
        self.initialiseoptions(QuestChoiceGui)
        self.questChoicePosters = []
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.cancelButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.7, 1, 1), text=TTLocalizer.QuestChoiceGuiCancel, text_scale=0.06, text_pos=(0, -0.02), command=self.chooseQuest, extraArgs=[0])
        guiButton.removeNode()
        base.setCellsAvailable(base.leftCells, 0)
        base.setCellsAvailable([base.bottomCells[0], base.bottomCells[1]], 0)

    def setQuests(self, quests, timeout):
        for i in range(0, len(quests)):
            questId = quests[i]
            qp = QuestPoster.QuestPoster()
            qp.reparentTo(self)
            qp.showChoicePoster(questId, self.chooseQuest)
            self.questChoicePosters.append(qp)

        if len(quests) == 1:
            self['geom_scale'] = (1, 1, 0.9)
            self.questChoicePosters[0].setPos(0, 0, 0.1)
            self.cancelButton.setPos(0.15, 0, -0.375)
        elif len(quests) == 2:
            self['geom_scale'] = (1.5, 1, 0.9)
            self.questChoicePosters[0].setPos(0, 0, -0.2)
            self.questChoicePosters[1].setPos(0, 0, 0.4)
            self.cancelButton.setPos(0.15, 0, -0.625)
        elif len(quests) == 3:
            self['geom_scale'] = (1.85, 1, 0.9)
            for p in self.questChoicePosters:
            	p.setScale(0.95)
            self.questChoicePosters[0].setPos(0, 0, -0.4)
            self.questChoicePosters[1].setPos(0, 0, 0.125)
            self.questChoicePosters[2].setPos(0, 0, 0.65)
            self.cancelButton.setPos(0.15, 0, -0.8)

    def chooseQuest(self, questId):
        if questId != 0:
            if config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: CREATEATASK: Create A Task.')
        base.setCellsAvailable(base.leftCells, 1)
        base.setCellsAvailable([base.bottomCells[0], base.bottomCells[1]], 1)
        messenger.send('chooseQuest', [questId])

    def timeout(self):
        messenger.send('chooseQuest', [0])
