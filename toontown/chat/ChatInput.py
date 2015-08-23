from panda3d.core import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import *
from otp.nametag.NametagConstants import *
from otp.otpbase import OTPGlobals
from otp.otpbase import OTPLocalizer
from toontown.toonbase import TTLocalizer
from ChatBalloon import ChatBalloon
import ToonChatGarbler
import re

class ChatInput(DirectObject):

    def __init__(self):
        self.keyList = [
         'a',
         'b',
         'c',
         'd',
         'e',
         'f',
         'g',
         'h',
         'i',
         'j',
         'k',
         'l',
         'm',
         'n',
         'o',
         'p',
         'q',
         'r',
         's',
         't',
         'u',
         'v',
         'w',
         'x',
         'y',
         'z',
         ',',
         '.',
         '/',
         ';',
         ':',
         '"',
         "'",
         '{',
         '}',
         '[',
         ']',
         '-',
         '_',
         '+',
         '=',
         '<',
         '>',
         '?',
         '!',
         '`',
         '~',
         '@',
         '#',
         '$',
         '%',
         '^',
         '&',
         '*',
         '(',
         ')',
         '1',
         '2'
         '3'
         '4',
         '5',
         '6',
         '7',
         '8',
         '9',
         '0',
         '|',
         'space']
        self.gui = None
        self.chatBx = None
        self.chat_btn = None
        self.chatEntry = None
        self.chatButton = None
        self.cancelButton = None
        self.whisperLabel = None
        self.state = None
        self.garbler = ToonChatGarbler.ToonChatGarbler()
        return

    def createGui(self):
        self.state = 'closed'
        self.gui = loader.loadModel('phase_3.5/models/gui/chat_input_gui.bam')
        self.chatBx = DirectFrame(parent=base.a2dTopLeft, image=self.gui.find('**/Chat_Bx_FNL'), relief=None, pos=(0.24, 0, -0.2), state=DGG.NORMAL, sortOrder=DGG.FOREGROUND_SORT_INDEX)
        self.chatBx.hide()
        self.chat_btn = DirectButton(image=(self.gui.find('**/ChtBx_ChtBtn_UP'), self.gui.find('**/ChtBx_ChtBtn_DN'), self.gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(0.0683, 0, -0.072), parent=base.a2dTopLeft, scale=1.179, relief=None, image_color=Vec4(1, 1, 1, 1), text=('', OTPLocalizer.ChatManagerChat, OTPLocalizer.ChatManagerChat), text_align=TextNode.ALeft, text_scale=TTLocalizer.TCMnormalButton, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(-0.0525, -0.09), textMayChange=0, sortOrder=DGG.FOREGROUND_SORT_INDEX, command=self.openChatInput, extraArgs=[None])
        return

    def deleteGui(self):
        self.gui.removeNode()
        self.gui = None
        self.chatBx.destroy()
        self.chatBx = None
        self.chat_btn.destroy()
        self.chat_btn = None
        return

    def enableKeyboardShortcuts(self):
        for key in self.keyList:
            self.acceptOnce(key, self.openChatInput, [key])
            self.acceptOnce('shift-' + key, self.openChatInput, [key.upper()])

    def disableKeyboardShortcuts(self):
        for key in self.keyList:
            self.ignore(key)
            self.ignore('shift-' + key)

    def openChatInput(self, key):
        self.disableKeyboardShortcuts()
        self.chat_btn.hide()
        self.chatBx.show()
        self.chatEntry = DirectEntry(parent=self.chatBx, relief=None, scale=0.05, pos=(-0.2, 0, 0.11), entryFont=OTPGlobals.getInterfaceFont(), initialText=key, width=8.6, numLines=3, cursorKeys=0, focus=1, clickSound=None, rolloverSound=None, command=self.sendChat)
        if key == 'space':
            self.chatEntry.enterText(' ')
        self.chatEntry.bind(DGG.OVERFLOW, self.chatOverflow)
        self.chatButton = DirectButton(parent=self.chatBx, image=(self.gui.find('**/ChtBx_ChtBtn_UP'), self.gui.find('**/ChtBx_ChtBtn_DN'), self.gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(0.182, 0, -0.088), relief=None, text=('', OTPLocalizer.ChatInputNormalSayIt, OTPLocalizer.ChatInputNormalSayIt), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.sendChat)
        self.cancelButton = DirectButton(parent=self.chatBx, image=(self.gui.find('**/CloseBtn_UP'), self.gui.find('**/CloseBtn_DN'), self.gui.find('**/CloseBtn_Rllvr')), pos=(-0.151, 0, -0.088), relief=None, text=('', OTPLocalizer.ChatInputNormalCancel, OTPLocalizer.ChatInputNormalCancel), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.close_ChtBx)
        self.whisperLabel = DirectLabel(parent=self.chatBx, pos=(0.02, 0, 0.23), relief=DGG.FLAT, frameColor=(1, 1, 0.5, 1), frameSize=(-0.23,
         0.23,
         -0.07,
         0.05), text=OTPLocalizer.ChatInputNormalWhisper, text_scale=0.04, text_fg=Vec4(0, 0, 0, 1), text_wordwrap=9.5, textMayChange=1)
        self.whisperLabel.hide()
        self.state = 'open'
        return

    def sendChat(self, *args):
        chat = self.chatEntry.get()
        messageChanged = False
        dialogue = None
        if len(chat) > 0:
            whitelistFile = 'resources/phase_4/etc/twhitelist.dat'
            with open(whitelistFile) as whitelist:
                approvedList = whitelist.read().split()
                words = re.sub('[.,!?]', ' ', chat).split()
                for word in words:
                    if word.lower() not in approvedList:
                        oldWord = r'\b' + '(' + word + ')' + r'\b'
                        newWord = self.garbler.garbleSingle(base.localAvatar, chat)
                        if messageChanged:
                            newMessage = re.sub(oldWord, '\1slant\1' + newWord + '\2', newMessage, count=1)
                        else:
                            newMessage = re.sub(oldWord, '\1slant\1' + newWord + '\2', chat, count=1)
                        messageChanged = True
            if chat[0] == '.':
                if messageChanged:
                    chat = newMessage
                base.localAvatar.setChatAbsolute(chat[1:], CFThought)
            else:
                if messageChanged:
                    chat = newMessage
                    animalType = base.localAvatar.getStyle().getType()
                    dialogue = base.loadSfx('phase_3.5/audio/dial/AV_' + animalType + '_long.ogg')
                base.localAvatar.setChatAbsolute(chat, CFSpeech|CFTimeout, dialogue=dialogue)
        self.close_ChtBx()

    def chatOverflow(self, overflowText):
        self.sendChat(self.chatEntry.get())

    def close_ChtBx(self):
        self.chatBx.hide()
        self.cancelButton.destroy()
        self.cancelButton = None
        self.chatButton.destroy()
        self.chatButton = None
        self.chatEntry.destroy()
        self.chatEntry = None
        self.chat_btn.show()
        self.enableKeyboardShortcuts()
        self.state = 'closed'
        return

    def delete(self):
        if self.state == 'open':
            self.close_ChtBx()
        self.deleteGui()
        self.disableKeyboardShortcuts()
        self.state = None
        return
