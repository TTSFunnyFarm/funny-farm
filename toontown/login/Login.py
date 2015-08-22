from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TTDialog
import __builtin__

class Login(DirectObject):
    notify = directNotify.newCategory('Login')

    def enter(self):
        base.transitions.fadeIn()
        soundMgr.startLogin()
        self.bg.show()
        base.setBackgroundColor(Vec4(0.992, 0.314, 0.004, 1))

    def exit(self, *args):
        __builtin__.playToken = self.loginEntry.get()
        if len(playToken) < 6:
            self.lengthError = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.Acknowledge, text='Usernames must be at least 6 characters long.', fadeScreen=0.5, command=self.__handleLengthError)
            self.lengthError.show()
            return
        elif ' ' in playToken:
            self.spaceError = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.Acknowledge, text='Please do not include spaces in your username.', fadeScreen=0.5, command=self.__handleSpaceError)
            self.spaceError.show()
            return
        self.accept('accountError', self.__handleAccountError)
        if not dataMgr.getAccountFilename(playToken):
            dataMgr.createAccount(playToken)
        else:
            dataMgr.loadAccount(playToken)
        if not dataMgr.maxAccounts:
            Sequence(Func(base.transitions.fadeOut), Wait(1), Func(self.__handleExit)).start()

    def __handleExit(self):
        soundMgr.stopLogin()
        self.unload()
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)
        start.startFunnyFarm()

    def load(self):
        gui = loader.loadModel('phase_3/models/gui/login_background')
        self.bg = DirectFrame(image=gui, relief=None)
        self.bg.hide()

        self.logo = loader.loadModel('phase_3/models/gui/toontown-logo')
        self.logo.reparentTo(self.bg)
        self.logo.setPos(0, 0, 0.6)
        self.logo.setSz(0.8)

        self.loginText = DirectLabel(parent=self.bg, relief=None, pos=(0, 0, 0.1), scale=0.1, text='LOGIN', text_font=ToontownGlobals.getSignFont(), text_fg=(0.93, 0.26, 0.28, 1.0))
        self.username = DirectLabel(parent=self.bg, relief=None, pos=(-0.8, 0, -0.2), scale=0.08, text='Username:', text_font=ToontownGlobals.getSignFont(), text_fg=(0.93, 0.26, 0.28, 1.0))

        loginGui = loader.loadModel('phase_3/models/props/chatbox_input')
        self.loginFrame = DirectFrame(parent=self.bg, image=loginGui, relief=None, scale=(0.1, 1, 0.06), pos=(-0.45, 0, -0.2))
        self.loginEntry = DirectEntry(parent=self.loginFrame, relief=None, scale=(0.7, 1, 1.2), entryFont=ToontownGlobals.getToonFont(), width=13.0, numLines=1, focus=1, cursorKeys=1, command=self.exit)
        self.loginInfo = DirectLabel(parent=self.bg, relief=None, pos=(0, 0, -0.5), scale=0.07, text='Don\'t have a username?\nMake one up and click PLAY!\nAn account will be created for you.', text_font=ToontownGlobals.getToonFont())
        self.loginNote = DirectLabel(parent=self.bg, relief=None, pos=(0, 0, -0.95), scale=0.04, text='Note: You cannot create more than 5 accounts on a single user.', text_font=ToontownGlobals.getToonFont())

        buttonGui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        squareUp = buttonGui.find('**/tt_t_gui_mat_namePanelSquareUp')
        squareDown = buttonGui.find('**/tt_t_gui_mat_namePanelSquareDown')
        squareHover = buttonGui.find('**/tt_t_gui_mat_namePanelSquareHover')
        self.playButton = DirectButton(parent=self.bg, relief=None, image=(squareUp,
         squareDown,
         squareHover,
         squareUp), image_scale=(0.8, 0, 1.5), pos=(0.7, 0, -0.17), text='PLAY!', text_scale=0.08, text_pos=(0, -0.02), text_font=ToontownGlobals.getSignFont(), text_fg=(0.93, 0.26, 0.28, 1.0), command=self.exit)

        helpGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_brd_help')
        helpUp = helpGui.find('**/tt_t_gui_brd_helpUp')
        helpDown = helpGui.find('**/tt_t_gui_brd_helpDown')
        helpHover = helpGui.find('**/tt_t_gui_brd_helpHover')
        self.helpButton = DirectButton(parent=self.bg, relief=None, image=(helpUp,
         helpDown,
         helpHover,
         helpUp), pos=(0.7, 0, -0.55), text=('', 'Help'), text_scale=0.06, text_pos=(0, -0.12), text_font=ToontownGlobals.getToonFont(), command=self.help)

    def unload(self):
        self.bg.destroy()
        del self.bg

    def help(self):
        self.help = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.Acknowledge, pos=(0, 0, 0.15), scale=0.8, text='About TTFF Data Management\n\nWhy don\'t I need a password?\n-------------------------------------------------------\nAll of your data is safely stored on your computer. Nothing is being sent to any servers whatsoever.\n(Not even the TTFF Staff will know your username!) For this reason, we feel that a password is unnecessary since you are the only one who can access your account.\n\nWait, won\'t someone else be able to access my account if they know my username?\n-------------------------------------------------------\nAbsolutely not. Your account can only be accessed on YOUR computer, so if someone living across the country put in your username, it would create an entirely new account on their computer.', text_align=TextNode.ALeft, text_wordwrap=24, fadeScreen=0.5, command=self.__cleanupHelp)
        self.help.show()

    def __cleanupHelp(self, *args):
        self.help.destroy()

    def __handleAccountError(self):
        acc1 = dataMgr.loadAccountByIndex(1000000)
        acc2 = dataMgr.loadAccountByIndex(2000000)
        acc3 = dataMgr.loadAccountByIndex(3000000)
        acc4 = dataMgr.loadAccountByIndex(4000000)
        acc5 = dataMgr.loadAccountByIndex(5000000)
        self.accError = TTDialog.TTDialog(parent=aspect2dp, style=TTDialog.Acknowledge, text='You cannot create more than 5 accounts on a single user. Please log in to one of your existing accounts:\n' + acc1.username + '\n' + acc2.username + '\n' + acc3.username + '\n' + acc4.username + '\n' + acc5.username, text_wordwrap=15, fadeScreen=0.5, command=self.__cleanupAccError)
        self.accError.show()

    def __cleanupAccError(self, *args):
        self.accError.destroy()

    def __handleLengthError(self, *args):
        self.lengthError.destroy()

    def __handleSpaceError(self, *args):
        self.spaceError.destroy()
