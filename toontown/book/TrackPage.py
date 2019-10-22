from panda3d.core import *
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import TTLocalizer
from toontown.toon import Toon
from toontown.book import ShtikerPage

MAX_FRAMES = 16
Track2Anim = {ToontownBattleGlobals.HEAL_TRACK: 'juggle',
 ToontownBattleGlobals.TRAP_TRACK: 'toss',
 ToontownBattleGlobals.LURE_TRACK: 'hypnotize',
 ToontownBattleGlobals.SOUND_TRACK: 'sound',
 ToontownBattleGlobals.THROW_TRACK: 'throw',
 ToontownBattleGlobals.SQUIRT_TRACK: 'firehose',
 ToontownBattleGlobals.DROP_TRACK: 'pushbutton'}

class TrackFrame(DirectFrame):

    def __init__(self, index):
        DirectFrame.__init__(self, relief=None)
        self.initialiseoptions(TrackFrame)
        self.index = index
        self.frame = DirectFrame(parent=self, relief=None, image=loader.loadModel('phase_3.5/models/gui/filmstrip'), image_scale=1, text=str(self.index), text_pos=(0.26, -0.22), text_fg=(1, 1, 1, 1), text_scale=0.1)
        self.question = DirectLabel(parent=self.frame, relief=None, pos=(0, 0, -0.15), text='?', text_scale=0.4, text_pos=(0, 0.04), text_fg=(0.72, 0.72, 0.72, 1))
        self.toon = None
        return

    def makeToon(self):
        if not self.toon:
            self.toon = Toon.Toon()
            self.toon.setDNA(base.localAvatar.getStyle())
            self.toon.getGeomNode().setDepthWrite(1)
            self.toon.getGeomNode().setDepthTest(1)
            self.toon.useLOD(500)
            self.toon.reparentTo(self.frame)
            s = 0.1
            self.toon.setPosHprScale(0, 10, -0.25, 210, 0, 0, s, s, s)
            self.ignore('nametagAmbientLightChanged')

    def play(self, trackId):
        try:
            anim = Track2Anim[trackId]
        except IndexError as err:
            anim = 'neutral'
        if self.toon:
            numFrames = self.toon.getNumFrames(anim) - 1
            fromFrame = 0
            toFrame = numFrames / MAX_FRAMES * self.index
            self.toon.play(anim, None, fromFrame, toFrame - 1)
        return

    def setTrained(self, trackId):
        if not self.toon:
            self.makeToon()
        try:
            anim = Track2Anim[trackId]
            frame = (self.toon.getNumFrames(anim) - 1) / MAX_FRAMES * self.index
        except IndexError as err:
            anim = 'neutral'
            frame = 0
        self.toon.pose(anim, frame)
        self.toon.show()
        self.question.hide()
        trackColorR, trackColorG, trackColorB = ToontownBattleGlobals.TrackColors[trackId]
        self.frame['image_color'] = Vec4(trackColorR, trackColorG, trackColorB, 1)
        self.frame['text_fg'] = Vec4(trackColorR * 0.3, trackColorG * 0.3, trackColorB * 0.3, 1)
        return

    def setUntrained(self, trackId):
        if self.toon:
            self.toon.delete()
            self.toon = None
        self.question.show()
        if trackId == -1:
            self.frame['image_color'] = Vec4(0.7, 0.7, 0.7, 1)
            self.frame['text_fg'] = Vec4(0.5, 0.5, 0.5, 1)
            self.question['text_fg'] = Vec4(0.6, 0.6, 0.6, 1)
        else:
            trackColorR, trackColorG, trackColorB = ToontownBattleGlobals.TrackColors[trackId]
            self.frame['image_color'] = Vec4(trackColorR * 0.7, trackColorG * 0.7, trackColorB * 0.7, 1)
            self.frame['text_fg'] = Vec4(trackColorR * 0.3, trackColorG * 0.3, trackColorB * 0.3, 1)
            self.question['text_fg'] = Vec4(trackColorR * 0.6, trackColorG * 0.6, trackColorB * 0.6, 1)
        return

class TrackPage(ShtikerPage.ShtikerPage):
    notify = directNotify.newCategory('TrackPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.trackFrames = []

    def placeFrames(self):
        rowAmount = 4
        rowY = 0.38
        rowSpace = 0.28
        rowPos = []
        for i in range(4):
            rowPos.append(rowY)
            rowY -= rowSpace

        colX = -0.65
        colSpace = 0.276
        colPos = []
        for i in range(rowAmount):
            colPos.append(colX)
            colX += colSpace

        for index in range(1, MAX_FRAMES + 1):
            index = index - 1
            frame = self.trackFrames[index]
            col = index % rowAmount
            row = int(index / rowAmount)
            frame.setPos(colPos[col], 0, rowPos[row])
            frame.setScale(0.39)

    def clearPage(self):
        for index in range(1, MAX_FRAMES - 1):
            self.trackFrames[index].setUntrained(-1)

        self.trackText['text'] = TTLocalizer.TrackPageClear

    def updatePage(self):
        trackId, trackProgress = base.localAvatar.getTrackProgress()
        maxFrames = MAX_FRAMES - 2
        if trackId > -1:
            trackColorR, trackColorG, trackColorB = ToontownBattleGlobals.TrackColors[trackId]
            self.trackText['text_fg'] = Vec4(trackColorR * 0.3, trackColorG * 0.3, trackColorB * 0.3, 1)
            trackName = ToontownBattleGlobals.Tracks[trackId].capitalize()
            self.trackText['text'] = TTLocalizer.TrackPageTraining % trackName
            for index in range(0, maxFrames):
                if trackProgress >= index + 1:
                    self.trackFrames[index].setTrained(trackId)
                else:
                    self.trackFrames[index].setUntrained(trackId)

            self.trackFrames[maxFrames].setUntrained(trackId)
        else:
            self.clearPage()

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.TrackPageTitle, text_scale=0.1, pos=(0, 0, 0.65))
        self.subtitle = DirectLabel(parent=self, relief=None, text=TTLocalizer.TrackPageSubtitle, text_scale=0.05, text_fg=(0.5, 0.1, 0.1, 1), pos=(0, 0, 0.56))
        self.trackText = DirectLabel(parent=self, relief=None, text='', text_scale=0.05, text_fg=(0.5, 0.1, 0.1, 1), pos=(0.6, 0, 0.15))
        for index in range(1, MAX_FRAMES + 1):
            frame = TrackFrame(index)
            frame.reparentTo(self)
            self.trackFrames.append(frame)
        self.placeFrames()
        self.endFrame = self.trackFrames[-1]
        self.endFrame.question.hide()
        endFrame = self.endFrame.frame
        endFrame['text'] = TTLocalizer.TrackPageDone
        endFrame['text_font'] = ToontownGlobals.getMinnieFont()
        endFrame['text_scale'] = TTLocalizer.TPendFrame
        endFrame['image_color'] = Vec4(0.2, 0.2, 0.2, 1)
        endFrame['text_fg'] = (1, 1, 1, 1)
        endFrame['text_pos'] = (0, -0.08)
        return

    def unload(self):
        del self.title
        del self.subtitle
        del self.trackText
        del self.trackFrames
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        self.updatePage()
        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        self.clearPage()
        ShtikerPage.ShtikerPage.exit(self)
