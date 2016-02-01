from Tkinter import *
import threading
from subprocess import Popen
import sys

class Launcher:

    def __init__(self):
        self.window = Tk()
        self.window.resizable(False, False)
        self.window.geometry('300x100+810+490')
        self.window.title('Toontown\'s Funny Farm')
        self.frame = Frame(self.window)
        self.frame.pack()
        self.text = Label(self.window, text='Checking for updates...', height=5, font=('Helvetica', 12))
        self.text.pack()

    def checkForUpdates(self):
        # placeholder code for now, we'll download stuff later
        threading.Timer(2, self.exit).start()

    def exit(self):
        self.window.destroy()
        self.window.quit()
        del self.window
        del self.frame
        del self.text
        self.startGame()
        sys.exit()

    def startGame(self):
        # This is where we would execute FFEngine.exe.
        # So technically, since all this launcher does is check for updates,
        # the user could just execute FFEngine.exe and the game will run fine; it just would not have checked for updates
        p = Popen('StartGame.bat')

launcher = Launcher()
launcher.checkForUpdates()
launcher.window.mainloop()
