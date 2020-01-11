from panda3d.core import *
from toontown.toonbase.ToontownGlobals import *
from toontown.toon import Walk

class PublicWalk(Walk.Walk):

    def __init__(self, doneEvent):
        Walk.Walk.__init__(self, doneEvent)

    def load(self):
        Walk.Walk.load(self)

    def unload(self):
        Walk.Walk.unload(self)

    def enter(self, slowWalk = 0):
        Walk.Walk.enter(self, slowWalk)
        base.localAvatar.book.showButton()
        self.sticker = settings[base.getCurrentDevice()]['shtiker']
        self.accept(self.sticker, self.__handleStickerBookEntry)
        self.accept('enterStickerBook', self.__handleStickerBookEntry)
        self.options = settings[base.getCurrentDevice()]['options']
        self.accept(self.options, self.__handleOptionsEntry)
        self.accept('refresh-controls', self.refreshControls)
        base.localAvatar.beginAllowPies()

    def refreshControls(self):
        self.ignore(self.sticker)
        self.ignore(self.options)
        self.sticker = settings[base.getCurrentDevice()]['shtiker']
        self.options = settings[base.getCurrentDevice()]['options']
        self.accept(self.options, self.__handleOptionsEntry)
        self.accept(self.sticker, self.__handleStickerBookEntry)

    def exit(self):
        Walk.Walk.exit(self)
        base.localAvatar.book.hideButton()
        self.ignore(self.sticker)
        self.ignore('enterStickerBook')
        self.ignore(self.options)
        self.ignore('refresh-controls')
        base.localAvatar.endAllowPies()

    def __handleStickerBookEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if base.localAvatar.book.isObscured() or currentState == 'jumpAirborne':
            return
        else:
            base.localAvatar.book.open()

    def __handleOptionsEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if base.localAvatar.book.isObscured() or currentState == 'jumpAirborne':
            return
        else:
            base.localAvatar.book.open(esc=True)
