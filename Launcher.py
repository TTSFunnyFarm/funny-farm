from panda3d.core import *

loadPrcFileData('launcher config', '''
window-title Toontown\'s Funny Farm
win-size 600 375
win-fixed-size 1
icon-filename resources/phase_3/etc/funnyfarm.ico
''')

from direct.showbase.ShowBase import ShowBase

ShowBase()

from direct.gui.DirectGui import *

DGG.setDefaultFont(loader.loadFont('resources/phase_3/models/fonts/ImpressBT.ttf'))

from direct.interval.IntervalGlobal import *
from subprocess import Popen
import sys

class Launcher:
    version = '1.0.0'

    def __init__(self):
        background = loader.loadTexture('resources/phase_3/maps/launcher_gui.jpg')
        self.frame = DirectFrame(parent=render2d, relief=None, image=background)
        self.versionText = DirectLabel(parent=base.a2dTopLeft, relief=None, text='Funny Farm Launcher v%s' % self.version, pos=(0.5, 0, -0.1), scale=0.08, text_fg=(1.0, 1.0, 1.0, 1.0))
        self.text = DirectLabel(relief=None, text='', pos=(0, 0, -0.5), scale=0.15, text_fg=(1.0, 1.0, 1.0, 1.0))

    def checkForUpdates(self):
        self.text['text'] = 'Checking for updates...'
        # placeholder code for now, we'll download stuff later
        Sequence(Wait(2), Func(self.startGame)).start()

    def updateFiles(self):
        self.text['text'] = 'Updating file n of n'

    def exit(self):
        self.frame.destroy()
        self.frame.removeNode()
        self.versionText.destroy()
        self.versionText.removeNode()
        self.text.destroy()
        self.text.removeNode()
        del self.frame
        del self.versionText
        del self.text
        base.closeWindow(base.win)

    def startGame(self):
        # This is where we would execute FFEngine.exe.
        # So technically, since all this launcher does is check for updates,
        # the user could just execute FFEngine.exe and the game will run fine; it just would not have checked for updates
        self.exit()
        Popen('StartGame.bat')

launcher = Launcher()
launcher.checkForUpdates()

base.run()
