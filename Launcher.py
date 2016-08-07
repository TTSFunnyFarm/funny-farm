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
        # Grab the file list for the particular platform the user is on.
        base.graphicsEngine.renderFrame()
        if sys.platform == 'win32':
            base.graphicsEngine.renderFrame()
            self.platform = 'windows'
            base.graphicsEngine.renderFrame()
            if not self.manifest:
                base.graphicsEngine.renderFrame()
                manifestUrl = urllib2.urlopen('http://cdn.toontownsfunnyfarm.com/windows/manifest.json')
                base.graphicsEngine.renderFrame()
                self.manifest = json.loads(manifestUrl.read())
                base.graphicsEngine.renderFrame()
        elif sys.platform == 'unknown':
            if platform.system() == 'Linux':
                base.graphicsEngine.renderFrame()
                self.platform = 'linux'
                base.graphicsEngine.renderFrame()
                if not self.manifest:
                    base.graphicsEngine.renderFrame()
                    manifestUrl = urllib2.urlopen('http://cdn.toontownsfunnyfarm.com/linux/manifest.json')
                    base.graphicsEngine.renderFrame()
                    self.manifest = json.loads(manifestUrl.read())
                    base.graphicsEngine.renderFrame()
            elif platform.system() == 'Darwin':
                base.graphicsEngine.renderFrame()
                self.platform = 'mac'
                base.graphicsEngine.renderFrame()
                if not self.manifest:
                    base.graphicsEngine.renderFrame()
                    manifestUrl = urllib2.urlopen('http://cdn.toontownsfunnyfarm.com/mac/manifest.json')
                    base.graphicsEngine.renderFrame()
                    self.manifest = json.loads(manifestUrl.read())
                    base.graphicsEngine.renderFrame()

        base.graphicsEngine.renderFrame()
        self.fileList = self.manifest.get('files').keys()
        base.graphicsEngine.renderFrame()

    def fetch_server_md5(self, file):
        base.graphicsEngine.renderFrame()
        if not self.manifest:
            base.graphicsEngine.renderFrame()
            self.generateFileList()
            base.graphicsEngine.renderFrame()

        base.graphicsEngine.renderFrame()
        hash = self.manifest.get('files').get(file).get('hash')
        base.graphicsEngine.renderFrame()

        return hash

    def fetch_client_md5(self, file):
        base.graphicsEngine.renderFrame()
        try:
            base.graphicsEngine.renderFrame()
            fileContent = open(file).read()
            base.graphicsEngine.renderFrame()
            hash = hashlib.md5(fileContent).hexdigest()
            base.graphicsEngine.renderFrame()
        except:
            # File is missing!
            base.graphicsEngine.renderFrame()
            hash = None
            base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()

        return hash

    def downloadFile(self, file, method='download'):
        # Increment the current file counter.
        base.graphicsEngine.renderFrame()
        self.currentFile += 1
        base.graphicsEngine.renderFrame()

        # Update the GUI text.
        base.graphicsEngine.renderFrame()
        if method == 'download':
            base.graphicsEngine.renderFrame()
            self.launcher.downloadFiles(self.currentFile, self.numMissingFiles)
            base.graphicsEngine.renderFrame()
        elif method == 'update':
            base.graphicsEngine.renderFrame()
            self.launcher.updateFiles(self.currentFile, self.numOutdatedFiles)
            base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()

        # Resource files need to have the "resources/" prefix stripped from them
        # or else they won't be found on the CDN.
        base.graphicsEngine.renderFrame()
        if file.startswith('resources/'):
            base.graphicsEngine.renderFrame()
            file = file.strip('resources/')
            base.graphicsEngine.renderFrame()

        base.graphicsEngine.renderFrame()
        url = 'http://cdn.toontownsfunnyfarm.com/%s/%s' % (self.platform, file)
        base.graphicsEngine.renderFrame()

        # If the file begins with "phase_", we know it belongs in the "resources" folder,
        # so we will have to add the "resources/" prefix back. We will also do this with
        # files that start with "lib", except they belong in the "lib" folder.
        # Otherwise, place it in the root.
        base.graphicsEngine.renderFrame()
        if file.startswith('phase_'):
            base.graphicsEngine.renderFrame()
            if not os.path.exists('resources/'):
                base.graphicsEngine.renderFrame()
                os.mkdir('resources/')
                base.graphicsEngine.renderFrame()

            base.graphicsEngine.renderFrame()
            urllib.urlretrieve(url, 'resources/' + file)
            base.graphicsEngine.renderFrame()
        elif file.startswith('lib'):
            base.graphicsEngine.renderFrame()
            if not os.path.exists('lib/'):
                base.graphicsEngine.renderFrame()
                os.mkdir('lib/')
                base.graphicsEngine.renderFrame()

            base.graphicsEngine.renderFrame()
            urllib.urlretrieve(url, 'lib/' + file)
            base.graphicsEngine.renderFrame()
        else:
            base.graphicsEngine.renderFrame()
            urllib.urlretrieve(url, file)
            base.graphicsEngine.renderFrame()

    def patch(self):
        # Generate our file list.
        base.graphicsEngine.renderFrame()
        self.generateFileList()
        base.graphicsEngine.renderFrame()

        # Check if the files already exist.
        base.graphicsEngine.renderFrame()
        for file in self.fileList:
            try:
                base.graphicsEngine.renderFrame()
                stream = open(file)
                base.graphicsEngine.renderFrame()
            except:
                # File is missing.
                base.graphicsEngine.renderFrame()
                self.numMissingFiles += 1
                base.graphicsEngine.renderFrame()
                self.filesToDownload.append(file)
                base.graphicsEngine.renderFrame()

        # If there are any files that are missing, download them now.
        for file in self.filesToDownload:
            base.graphicsEngine.renderFrame()
            self.downloadFile(file)
            base.graphicsEngine.renderFrame()

        # Reset the current file counter.
        base.graphicsEngine.renderFrame()
        self.currentFile = 0
        base.graphicsEngine.renderFrame()

        # Now update existing files if needed.
        for file in self.fileList:
            base.graphicsEngine.renderFrame()
            serverHash = self.fetch_server_md5(file)
            base.graphicsEngine.renderFrame()
            clientHash = self.fetch_client_md5(file)
            base.graphicsEngine.renderFrame()
            if clientHash != serverHash:
                # File hash mismatch!
                base.graphicsEngine.renderFrame()
                self.numOutdatedFiles += 1
                base.graphicsEngine.renderFrame()
                self.filesToUpdate.append(file)
                base.graphicsEngine.renderFrame()

        # If there are any files that are outdated, update them now.
        for file in self.filesToUpdate:
            base.graphicsEngine.renderFrame()
            self.downloadFile(file, method='update')
            base.graphicsEngine.renderFrame()

        # Alright, we're done! Start the game...
        base.graphicsEngine.renderFrame()
        self.launcher.startGame()


from panda3d.core import *

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
        base.graphicsEngine.renderFrame()
        background = loader.loadTexture('resources/phase_3/maps/launcher_gui.jpg')
        base.graphicsEngine.renderFrame()
        self.frame = DirectFrame(parent=render2d, relief=None, image=background)
        base.graphicsEngine.renderFrame()
        self.versionText = DirectLabel(parent=base.a2dTopLeft, relief=None, text='Funny Farm Launcher v%s' % self.version, pos=(0.5, 0, -0.1), scale=0.08, text_fg=(1.0, 1.0, 1.0, 1.0))
        base.graphicsEngine.renderFrame()
        self.text = DirectLabel(relief=None, text='', pos=(0, 0, -0.5), scale=0.15, text_fg=(1.0, 1.0, 1.0, 1.0))
        base.graphicsEngine.renderFrame()
        self.setIcon()
        base.graphicsEngine.renderFrame()
        self.patcher = FFPatcher(self)
        base.graphicsEngine.renderFrame()

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
        base.graphicsEngine.renderFrame()
        self.text['text'] = 'Checking for updates...'
        base.graphicsEngine.renderFrame()
        self.patcher.patch()

    def updateFiles(self, curFile, totalFiles):
        base.graphicsEngine.renderFrame()
        self.text['text'] = 'Updating file %s of %s' % (curFile, totalFiles)
        base.graphicsEngine.renderFrame()

    def downloadFiles(self, curFile, totalFiles):
        base.graphicsEngine.renderFrame()
        self.text['text'] = 'Downloading file %s of %s' % (curFile, totalFiles)
        base.graphicsEngine.renderFrame()

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
        if sys.platform == 'win32':
            os._exit(0)

    def startGame(self):
        # This is where we would execute FFEngine.exe.
        # So technically, since all this launcher does is check for updates,
        # the user could just execute FFEngine.exe and the game will run fine; it just would not have checked for updates
        if sys.platform == 'win32':
            Popen('funnyfarm.exe', creationflags=0x08000000)
            self.exit()
        elif sys.platform == 'unknown':
            if platform.system() == 'Linux':
                self.exit()
                os.system('chmod +x ./funnyfarm')
                os.system('./funnyfarm')
                os._exit(0)
            elif platform.system() == 'Darwin':
                self.exit()
                os.system('chmod +x ./startFF.sh')
                os.system('./startFF.sh')
                os._exit(0)


launcher = Launcher()
launcher.checkForUpdates()

base.run()
