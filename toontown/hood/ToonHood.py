from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer

class ToonHood(DirectObject):
    notify = directNotify.newCategory('ToonHood')

    def __init__(self):
        self.zoneId = None
        self.hoodFile = None
        self.spookyHoodFile = None
        self.winterHoodFile = None
        self.skyFile = None
        self.spookySkyFile = 'phase_3.5/models/props/BR_sky'
        self.titleText = None
        self.titleColor = (1, 1, 1, 1)
        self.title = None

    def enter(self, shop=None, tunnel=None, init=False):
        if shop:
            return
        if not tunnel:
            base.localAvatar.enableAvatarControls()
            base.localAvatar.setRandomSpawn(self.zoneId)
            if init:
                Sequence(Wait(0.3), Func(base.localAvatar.enterTeleportIn, 1, 0, self.__handleTeleport, [True])).start()
                if base.air.holidayMgr.isHalloween():
                    base.localAvatar.setSystemMessage(0, TTLocalizer.HalloweenHolidayMessage)
                elif base.air.holidayMgr.isWinter():
                    base.localAvatar.setSystemMessage(0, TTLocalizer.WinterHolidayMessage)
            else:
                base.localAvatar.enterTeleportIn(callback=self.__handleTeleport)
        base.localAvatar.setZoneId(self.zoneId)
        base.avatarData.setLastHood = self.zoneId
        dataMgr.saveToonData(base.avatarData, playToken)
        self.title = OnscreenText(self.titleText, fg=self.titleColor, font=ToontownGlobals.getSignFont(), pos=(0, -0.5), scale=TTLocalizer.HtitleText, drawOrder=0, mayChange=1)
        self.spawnTitleText()

    def exit(self):
        self.ignoreAll()
        if self.title:
            self.title.cleanup()
            self.title = None

    def load(self):
        if base.air.holidayMgr.isHalloween():
            self.geom = loader.loadModel(self.spookyHoodFile)
            self.sky = loader.loadModel(self.spookySkyFile)
            self.sky.setColorScale(0.5, 0.5, 0.5, 1)
        elif base.air.holidayMgr.isWinter():
            self.geom = loader.loadModel(self.winterHoodFile)
            self.sky = loader.loadModel(self.spookySkyFile)
        else:
            self.geom = loader.loadModel(self.hoodFile)
            self.sky = loader.loadModel(self.skyFile)
        self.geom.reparentTo(render)
        self.sky.reparentTo(render)
        self.geom.flattenMedium()
        self.sky.flattenMedium()

    def unload(self):
        self.geom.removeNode()
        self.sky.removeNode()
        del self.geom
        del self.sky

    def spawnTitleText(self):
        self.title.show()
        self.title.setColor(Vec4(*self.titleColor))
        self.title.clearColorScale()
        self.title.setFg(self.titleColor)
        seq = Sequence(Wait(0.1), Wait(6.0), self.title.colorScaleInterval(0.5, Vec4(1.0, 1.0, 1.0, 0.0)), Func(self.title.hide))
        seq.start()

    def startSkyTrack(self):
        clouds1 = self.sky.find('**/cloud1')
        clouds2 = self.sky.find('**/cloud2')
        if clouds1.isEmpty() or clouds2.isEmpty():
            return
        clouds1.setScale(0.7, 0.7, 0.7)
        clouds2.setScale(0.9, 0.9, 0.9)
        self.clouds1Spin = clouds1.hprInterval(360,  Vec3(60,  0,  0))
        self.clouds2Spin = clouds2.hprInterval(360,  Vec3(-60,  0,  0))
        self.clouds1Spin.loop()
        self.clouds2Spin.loop()

    def stopSkyTrack(self):
        self.clouds1Spin.finish()
        self.clouds2Spin.finish()

    def __handleTeleport(self, init=False):
        base.localAvatar.exitTeleportIn()
        base.localAvatar.book.showButton()
        base.localAvatar.beginAllowPies()
