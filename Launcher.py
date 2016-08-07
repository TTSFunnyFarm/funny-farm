import hashlib
import urllib
import urllib2
import sys
import platform
import json
import os

class FFPatcher:

    def __init__(self, launcher):
        self.launcher = launcher
        self.platform = ''
        self.manifest = None
        self.fileList = None
        self.currentFile = 0
        self.numMissingFiles = 0
        self.numOutdatedFiles = 0
        self.filesToDownload = []
        self.filesToUpdate = []

    def generateFileList(self):
        # Get the platform the user is on.
        if sys.platform == 'win32':
            self.platform = 'windows'
        elif sys.platform == 'unknown':
            if platform.system() == 'Linux':
                self.platform = 'linux'
            elif platform.system() == 'Darwin':
                self.platform = 'mac'

        # Grab the file list for the particular platform the user is on.
        if not self.manifest:
            manifestUrl = urllib2.urlopen('http://cdn.toontownsfunnyfarm.com/%s/manifest.json' % self.platform)
            self.manifest = json.loads(manifestUrl.read())

        self.fileList = self.manifest.get('files').keys()

    def fetch_server_md5(self, file):
        if not self.manifest:
            self.generateFileList()

        hash = self.manifest.get('files').get(file).get('hash')

        return hash

    def fetch_client_md5(self, file):
        try:
            fileContent = open(file).read()
            hash = hashlib.md5(fileContent).hexdigest()
        except:
            # File is missing!
            hash = None

        return hash

    def downloadFile(self, file, method='download'):
        # Increment the current file counter.
        self.currentFile += 1

        # Update the GUI text.
        if method == 'download':
            self.launcher.downloadFiles(self.currentFile, self.numMissingFiles)
        elif method == 'update':
            self.launcher.updateFiles(self.currentFile, self.numOutdatedFiles)

        # Resource files need to have the "resources/" prefix stripped from them
        # or else they won't be found on the CDN.
        if file.startswith('resources/'):
            file = file.strip('resources/')

        url = 'http://cdn.toontownsfunnyfarm.com/%s/%s' % (self.platform, file)

        # If the file begins with "phase_", we know it belongs in the "resources" folder,
        # so we will have to add the "resources/" prefix back. We will also do this with
        # files that start with "lib", except they belong in the "lib" folder.
        # Otherwise, place it in the root.
        if file.startswith('phase_'):
            if not os.path.exists('resources/'):
                os.mkdir('resources/')

            urllib.urlretrieve(url, 'resources/' + file)
        elif file.startswith('lib'):
            if not os.path.exists('lib/'):
                os.mkdir('lib/')

            urllib.urlretrieve(url, 'lib/' + file)
        else:
            urllib.urlretrieve(url, file)

    def patch(self):
        # Generate our file list.
        self.generateFileList()

        # Check if the files already exist.
        for file in self.fileList:
            try:
                stream = open(file)
            except:
                # File is missing.
                self.numMissingFiles += 1
                self.filesToDownload.append(file)

        # If there are any files that are missing, download them now.
        for file in self.filesToDownload:
            self.downloadFile(file)

        # Reset the current file counter.
        self.currentFile = 0

        # Now update existing files if needed.
        for file in self.fileList:
            serverHash = self.fetch_server_md5(file)
            clientHash = self.fetch_client_md5(file)
            if clientHash != serverHash:
                # File hash mismatch!
                self.numOutdatedFiles += 1
                self.filesToUpdate.append(file)

        # If there are any files that are outdated, update them now.
        for file in self.filesToUpdate:
            self.downloadFile(file, method='update')

        # Alright, we're done! Start the game...
        self.launcher.startGame()


from panda3d.core import *

if __debug__:
    loadPrcFile('config/launcher.prc')

from direct.showbase.ShowBase import ShowBase

ShowBase()

from direct.gui.DirectGui import *

DGG.setDefaultFont(loader.loadFont('resources/phase_3/models/fonts/ImpressBT.ttf'))

from direct.interval.IntervalGlobal import *
if sys.platform == 'win32':
    from subprocess import Popen
import tempfile
import shutil
import atexit

class Launcher:
    version = '1.0.0'

    def __init__(self):
        background = loader.loadTexture('resources/phase_3/maps/launcher_gui.jpg')
        self.frame = DirectFrame(parent=render2d, relief=None, image=background)
        self.versionText = DirectLabel(parent=base.a2dTopLeft, relief=None, text='Funny Farm Launcher v%s' % self.version, pos=(0.5, 0, -0.1), scale=0.08, text_fg=(1.0, 1.0, 1.0, 1.0))
        self.text = DirectLabel(relief=None, text='', pos=(0, 0, -0.5), scale=0.15, text_fg=(1.0, 1.0, 1.0, 1.0))
        if not __debug__:
            self.setIcon()
        self.patcher = FFPatcher(self)

    def setIcon(self):
        tempdir = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, tempdir)
        vfs = VirtualFileSystem.getGlobalPtr()

        searchPath = DSearchPath()
        searchPath.appendDirectory(Filename('resources/phase_3/etc'))

        p3filename = Filename('funnyfarm.ico')
        found = vfs.resolveFilename(p3filename, searchPath)
        if not found:
            return # Can't do anything past this point.

        with open(os.path.join(tempdir, 'funnyfarm.ico'), 'wb') as f:
            f.write(vfs.readFile(p3filename, False))

        wp = WindowProperties()
        wp.setIconFilename(Filename.fromOsSpecific(os.path.join(tempdir, 'funnyfarm.ico')))
        base.win.requestProperties(wp)

    def checkForUpdates(self):
        self.text['text'] = 'Checking for updates...'
        if not __debug__:
            self.patcher.patch()
        else:
            Sequence(Wait(2), Func(self.startGame)).start()

    def updateFiles(self, curFile, totalFiles):
        self.text['text'] = 'Updating file %s of %s' % (curFile, totalFiles)

    def downloadFiles(self, curFile, totalFiles):
        self.text['text'] = 'Downloading file %s of %s' % (curFile, totalFiles)

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
        if __debug__:
            self.exit()
            Popen('StartGame.bat')
        else:
            if sys.platform == 'win32':
                self.exit()
                Popen('funnyfarm.exe', creationflags=0x08000000)
            elif sys.platform == 'unknown':
                if platform.system() == 'Linux':
                    self.exit()
                    os.system('chmod +x ./funnyfarm')
                    os.system('./funnyfarm')
                elif platform.system() == 'Darwin':
                    self.exit()
                    os.system('chmod +x ./startFF.sh')
                    os.system('./startFF.sh')


launcher = Launcher()
launcher.checkForUpdates()

base.run()
