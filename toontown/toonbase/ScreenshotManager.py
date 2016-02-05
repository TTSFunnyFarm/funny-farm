from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
import os

class ScreenshotManager:
    notify = DirectNotifyGlobal.directNotify.newCategory('ScreenshotManager')

    def __init__(self):
        base.accept(ToontownGlobals.ScreenshotHotkey, self.takeScreenshot)
        self.lastScreenShotTime = globalClock.getRealTime()

    def takeScreenshot(self):
        if not os.path.exists(TTLocalizer.ScreenshotPath):
            os.mkdir(TTLocalizer.ScreenshotPath)
        logPrefix = 'funnyfarm-'
        namePrefix = 'screenshot'
        namePrefix = TTLocalizer.ScreenshotPath + logPrefix + namePrefix
        if not hasattr(base, 'localAvatar') or not base.localAvatar:
            base.screenshot(namePrefix=namePrefix)
            self.lastScreenShotTime = globalClock.getRealTime()
            return
        base.localAvatar.stopThisFrame = 1
        self.screenshotStr = ''
        messenger.send('takingScreenshot')
        base.graphicsEngine.renderFrame()
        base.screenshot(namePrefix=namePrefix, imageComment=self.screenshotStr)
        self.lastScreenShotTime = globalClock.getRealTime()

    def addScreenshotString(self, str):
        if len(self.screenshotStr):
            self.screenshotStr += '\n'
        self.screenshotStr += str
