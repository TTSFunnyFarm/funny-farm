from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import TTLocalizer
from toontown.building import Door
import ZoneUtil

class Hood(DirectObject):
    notify = directNotify.newCategory('Hood')

    def __init__(self):
        self.zoneId = None
        self.hoodFile = None
        self.spookyHoodFile = None
        self.winterHoodFile = None
        self.skyFile = None
        self.spookySkyFile = 'phase_3.5/models/props/BR_sky'
        self.titleColor = (1, 1, 1, 1)
        self.title = None
        self.titleTrack = None
        self.place = None

    def enter(self, shop=None, tunnel=None, init=0):
        if tunnel:
            for linkTunnel in self.geom.findAllMatches('**/linktunnel*'):
                name = linkTunnel.getName().split('_')
                zoneStr = name[2]
                if tunnel == zoneStr:
                    tunnelOrigin = linkTunnel.find('**/tunnel_origin')
                    base.localAvatar.tunnelIn(tunnelOrigin)
        else:
            base.localAvatar.setRandomSpawn(self.zoneId)
            if init:
                Sequence(Wait(0.3), Func(base.localAvatar.enterTeleportIn, 1, 0, self.handleEntered)).start()
                if base.air.holidayMgr.isHalloween():
                    base.localAvatar.setSystemMessage(0, TTLocalizer.HalloweenHolidayMessage)
                elif base.air.holidayMgr.isWinter():
                    base.localAvatar.setSystemMessage(0, TTLocalizer.WinterHolidayMessage)
            else:
                base.localAvatar.enterTeleportIn(callback=self.handleEntered)
        base.avatarData.setLastHood = self.zoneId
        dataMgr.saveToonData(base.avatarData)
        self.spawnTitleText()
        self.startActive()

    def exit(self):
        musicMgr.stopMusic()
        self.ignoreAll()
        if self.titleTrack:
            self.titleTrack.finish()
            self.titleTrack = None
            self.title.cleanup()
            self.title = None

    def load(self):
        if base.air.holidayMgr.isHalloween():
            self.geom = loader.loadModel(self.spookyHoodFile)
            self.startSpookySky()
        elif base.air.holidayMgr.isWinter():
            self.geom = loader.loadModel(self.winterHoodFile)
            self.startSnowySky()
        else:
            self.geom = loader.loadModel(self.hoodFile)
            self.sky = loader.loadModel(self.skyFile)
            self.sky.setTag('sky', 'Regular')
            self.sky.setScale(1.0)
            self.sky.setFogOff()
            self.startSky()
        self.sky.flattenMedium()
        self.geom.reparentTo(render)
        self.geom.flattenMedium()
        gsg = base.win.getGsg()
        if gsg:
            self.geom.prepareScene(gsg)

    def unload(self):
        self.stopSky()
        self.geom.removeNode()
        self.sky.removeNode()
        del self.geom
        del self.sky

    def getHoodText(self):
        hoodId = FunnyFarmGlobals.getHoodId(self.zoneId)
        hoodText = FunnyFarmGlobals.hoodNameMap[hoodId]
        streetName = FunnyFarmGlobals.StreetNames.get(ZoneUtil.getCanonicalBranchZone(self.zoneId))
        if streetName:
            hoodText = hoodText + '\n' + streetName
        return hoodText

    def spawnTitleText(self):
        self.title = OnscreenText(self.getHoodText(), fg=self.titleColor, font=ToontownGlobals.getSignFont(), pos=(0, -0.5), scale=TTLocalizer.HtitleText, drawOrder=0, mayChange=1)
        self.titleTrack = Sequence(Wait(0.1), Wait(6.0), self.title.colorScaleInterval(0.5, Vec4(1.0, 1.0, 1.0, 0.0)), Func(self.title.hide))
        self.titleTrack.start()

    def handleEntered(self):
        base.localAvatar.exitTeleportIn()
        base.localAvatar.enable()
        if base.localAvatar.hp <= 0:
            base.localAvatar.setAnimState('Sad')

    def startActive(self):
        for door in self.geom.findAllMatches('**/*door_trigger*'):
            self.acceptOnce('enter%s' % door.getName(), self.handleDoorTrigger)
        for linkTunnel in self.geom.findAllMatches('**/linktunnel*'):
            name = linkTunnel.getName().split('_')
            hoodStr = name[1]
            zoneStr = name[2]
            linkSphere = linkTunnel.find('**/tunnel_trigger*')
            if linkSphere.isEmpty():
                linkSphere = linkTunnel.find('**/tunnel_sphere')
            linkSphere.setName('tunnel_trigger_%s_%s' % (hoodStr, zoneStr))
            self.acceptOnce('enter%s' % linkSphere.getName(), self.handleEnterTunnel)

    def handleDoorTrigger(self):
        pass

    def handleEnterTunnel(self, collEntry):
        tunnel = collEntry.getIntoNodePath()
        name = tunnel.getName().split('_')
        zoneId = int(name[3])
        tunnelOrigin = tunnel.getParent().find('**/tunnel_origin')
        if tunnelOrigin.isEmpty():
            tunnelOrigin = tunnel.getParent().getParent().find('**/tunnel_origin')
        base.localAvatar.tunnelOut(tunnelOrigin)
        self.acceptOnce('tunnelOutMovieDone', self.enterZone, [zoneId])

    def enterZone(self, zoneId):
        base.cr.playGame.exitActiveZone()
        isStreet = (zoneId % 1000) != 0
        if isStreet:
            self.enterStreet(zoneId)
        else:
            self.enterHood(zoneId)

    def enterHood(self, zoneId):
        tunnel = FunnyFarmGlobals.getNameFromId(self.zoneId)
        base.cr.playGame.enterHood(zoneId, tunnel=tunnel)

    def enterStreet(self, zoneId):
        hoodId = FunnyFarmGlobals.getHoodId(self.zoneId)
        tunnel = FunnyFarmGlobals.getNameFromId(hoodId)
        base.cr.playGame.enterStreet(zoneId, tunnel=tunnel)

    def enterPlace(self, shopId, zoneId):
        pass

    def exitPlace(self):
        pass

    def startSky(self):
        self.sky.reparentTo(camera)
        self.sky.setZ(0.0)
        self.sky.setHpr(0.0, 0.0, 0.0)
        self.sky.setBin('background', 100)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)

    def stopSky(self):
        taskMgr.remove('skyTrack')
        self.sky.reparentTo(hidden)

    def startSpookySky(self):
        if not self.spookySkyFile:
            return
        if hasattr(self, 'sky') and self.sky:
            self.stopSky()
        self.sky = loader.loadModel(self.spookySkyFile)
        self.sky.setTag('sky', 'Halloween')
        self.sky.setScale(1.0)
        self.sky.setDepthTest(0)
        self.sky.setDepthWrite(0)
        self.sky.setColor(0.5, 0.5, 0.5, 1)
        self.sky.setBin('background', 100)
        self.sky.reparentTo(camera)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        fadeIn = self.sky.colorScaleInterval(1.5, Vec4(1, 1, 1, 1), startColorScale=Vec4(1, 1, 1, 0.25), blendType='easeInOut')
        fadeIn.start()
        self.sky.setZ(0.0)
        self.sky.setHpr(0.0, 0.0, 0.0)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)

    def endSpookySky(self):
        if hasattr(self, 'sky') and self.sky:
            self.sky.reparentTo(hidden)
        if hasattr(self, 'sky'):
            self.sky = loader.loadModel(self.skyFile)
            self.sky.setTag('sky', 'Regular')
            self.sky.setScale(1.0)
            self.startSky()

    def startSnowySky(self):
        if hasattr(self, 'sky') and self.sky:
            self.stopSky()
        self.sky = loader.loadModel(self.spookySkyFile)
        self.sky.setTag('sky', 'Winter')
        self.sky.setScale(1.0)
        self.sky.setDepthTest(0)
        self.sky.setDepthWrite(0)
        self.sky.setColor(1, 1, 1, 1)
        self.sky.setBin('background', 100)
        self.sky.setFogOff()
        self.sky.reparentTo(camera)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        fadeIn = self.sky.colorScaleInterval(1.5, Vec4(1, 1, 1, 1), startColorScale=Vec4(1, 1, 1, 0.25), blendType='easeInOut')
        fadeIn.start()
        self.sky.setZ(0.0)
        self.sky.setHpr(0.0, 0.0, 0.0)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)

    def endSnowySky(self):
        if hasattr(self, 'sky') and self.sky:
            self.sky.reparentTo(hidden)
        if hasattr(self, 'sky'):
            self.sky = loader.loadModel(self.skyFile)
            self.sky.setTag('sky', 'Regular')
            self.sky.setScale(1.0)
            self.startSky()
