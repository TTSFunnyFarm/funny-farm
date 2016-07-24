from panda3d.core import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import *
from otp.nametag.NametagConstants import *
from otp.otpbase import OTPGlobals
from otp.otpbase import OTPLocalizer
from toontown.toonbase import TTLocalizer
from ChatBalloon import ChatBalloon
import ChatGlobals

import string
AcceptedKeystrokes = string.digits + string.ascii_letters + string.punctuation + ' '

class ChatManager(DirectObject):

    def __init__(self):
        self.gui = None
        self.chatFrame = None
        self.chatButton = None
        self.chatEntry = None
        self.sendButton = None
        self.cancelButton = None
        self.state = None

    def delete(self):
        if self.state == 'open':
            self.closeChatInput()
        self.deleteGui()
        self.disableKeyboardShortcuts()
        self.state = None

    def createGui(self):
        self.state = 'closed'
        self.gui = loader.loadModel('phase_3.5/models/gui/chat_input_gui.bam')
        self.chatButton = DirectButton(image=(self.gui.find('**/ChtBx_ChtBtn_UP'), self.gui.find('**/ChtBx_ChtBtn_DN'), self.gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(0.0683, 0, -0.072), parent=base.a2dTopLeft, scale=1.179, relief=None, image_color=Vec4(1, 1, 1, 1), text=('', OTPLocalizer.ChatManagerChat, OTPLocalizer.ChatManagerChat), text_align=TextNode.ALeft, text_scale=TTLocalizer.TCMnormalButton, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(-0.0525, -0.09), textMayChange=0, sortOrder=DGG.FOREGROUND_SORT_INDEX, command=self.openChatInput, extraArgs=[''])
        self.chatFrame = DirectFrame(parent=base.a2dTopLeft, image=self.gui.find('**/Chat_Bx_FNL'), relief=None, pos=(0.24, 0, -0.2), state=DGG.NORMAL, sortOrder=DGG.FOREGROUND_SORT_INDEX)
        self.chatFrame.hide()
        self.chatEntry = DirectEntry(parent=self.chatFrame, relief=None, scale=0.05, pos=(-0.2, 0, 0.11), entryFont=OTPGlobals.getInterfaceFont(), width=8.6, numLines=3, cursorKeys=0, focus=1, clickSound=None, rolloverSound=None, command=self.sendChat)
        self.chatEntry.bind(DGG.OVERFLOW, self.chatOverflow)
        self.sendButton = DirectButton(parent=self.chatFrame, image=(self.gui.find('**/ChtBx_ChtBtn_UP'), self.gui.find('**/ChtBx_ChtBtn_DN'), self.gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(0.182, 0, -0.088), relief=None, text=('', OTPLocalizer.ChatInputNormalSayIt, OTPLocalizer.ChatInputNormalSayIt), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.sendChat)
        self.cancelButton = DirectButton(parent=self.chatFrame, image=(self.gui.find('**/CloseBtn_UP'), self.gui.find('**/CloseBtn_DN'), self.gui.find('**/CloseBtn_Rllvr')), pos=(-0.151, 0, -0.088), relief=None, text=('', OTPLocalizer.ChatInputNormalCancel, OTPLocalizer.ChatInputNormalCancel), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.closeChatInput)

    def deleteGui(self):
        self.gui.removeNode()
        self.gui = None
        self.chatButton.destroy()
        self.chatButton = None
        self.chatFrame.destroy()
        self.chatFrame = None
        self.chatEntry.destroy()
        self.chatEntry = None
        self.sendButton.destroy()
        self.sendButton = None
        self.cancelButton.destroy()
        self.cancelButton = None

    def enableKeyboardShortcuts(self):
        base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        self.accept('keystroke', self.openChatInput)

    def disableKeyboardShortcuts(self):
        self.ignore('keystroke')
        base.buttonThrowers[0].node().setKeystrokeEvent('')

    def openChatInput(self, key):
        # This is to eliminate keystrokes such as Tab, Enter, Esc
        if key not in AcceptedKeystrokes:
            return
        self.disableKeyboardShortcuts()
        self.chatButton.hide()
        self.chatFrame.show()
        self.chatEntry['focus'] = 1
        self.chatEntry.enterText(key)
        self.state = 'open'

    def closeChatInput(self):
        self.chatFrame.hide()
        self.chatEntry.set('')
        self.chatEntry['focus'] = 0
        self.chatButton.show()
        self.enableKeyboardShortcuts()
        self.state = 'closed'

    def sendChat(self, *args):
        chat = self.chatEntry.get()
        dialogue = None
        if len(chat) > 0:
            if chat[0] == '.':
                base.localAvatar.setChatAbsolute(chat[1:], CFThought)
            else:
                base.localAvatar.setChatAbsolute(chat, CFSpeech|CFTimeout, dialogue=dialogue)
        self.closeChatInput()

    def chatOverflow(self, overflowText):
        self.sendChat(self.chatEntry.get())
