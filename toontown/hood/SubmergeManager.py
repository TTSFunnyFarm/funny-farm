from panda3d.core import *
from direct.task import Task
from toontown.toon import Walk

class SubmergeManager:
    def __init__(self, sky, waterLevel = 0):
        self.sky = sky
        self.waterLevel = waterLevel
        self.cameraSubmerged = 0
        self.toonSubmerged = 0
        self.walkStateData = Walk.Walk('walkDone')
        self.walkStateData.load()
        self.underwaterSound = base.loader.loadSfx('phase_4/audio/sfx/AV_ambient_water.ogg')
        self.swimSound = base.loader.loadSfx('phase_4/audio/sfx/AV_swim_single_stroke.ogg')
        self.submergeSound = base.loader.loadSfx('phase_5.5/audio/sfx/AV_jump_in_water.ogg')
        self.fog = Fog('SubmergeFog')
        self.whiteFogColor = Vec4(0.95, 0.95, 0.95, 1)
        self.underwaterFogColor = Vec4(0.0, 0.0, 0.6, 1.0)

    def start(self):
        taskMgr.add(self.__checkToonUnderwater, 'check-toon-underwater')
        taskMgr.add(self.__checkCameraUnderwater, 'check-cam-underwater')

    def stop(self):
        taskMgr.remove('check-toon-underwater')
        taskMgr.remove('check-cam-underwater')
        self.setNoFog()

    def cleanup(self):
        self.stop()
        self.walkStateData.unload()
        del self.walkStateData

    def __checkCameraUnderwater(self, task):
        if camera.getZ(render) < self.waterLevel:
            self.__submergeCamera()
        else:
            self.__emergeCamera()
        return Task.cont

    def __checkToonUnderwater(self, task):
        if base.localAvatar.getZ() < self.waterLevel - 4.0:
            self.__submergeToon()
        else:
            self.__emergeToon()
        return Task.cont

    def __submergeCamera(self):
        if self.cameraSubmerged == 1:
            return
        self.setUnderwaterFog()
        base.playSfx(self.underwaterSound, looping=1, volume=0.8)
        self.cameraSubmerged = 1
        self.walkStateData.setSwimSoundAudible(1)

    def __emergeCamera(self):
        if self.cameraSubmerged == 0:
            return
        self.setNoFog()
        self.underwaterSound.stop()
        self.cameraSubmerged = 0
        self.walkStateData.setSwimSoundAudible(0)

    def __submergeToon(self):
        if self.toonSubmerged == 1:
            return
        base.playSfx(self.submergeSound)
        self.walkStateData.fsm.request('swimming', [self.swimSound])
        pos = base.localAvatar.getPos(render)
        base.localAvatar.playSplashEffect(pos[0], pos[1], self.waterLevel)
        self.toonSubmerged = 1

    def __emergeToon(self):
        if self.toonSubmerged == 0:
            return
        self.walkStateData.fsm.request('walking')
        self.toonSubmerged = 0

    def setUnderwaterFog(self):
        self.fog.setColor(self.underwaterFogColor)
        self.fog.setLinearRange(0.1, 100.0)
        render.setFog(self.fog)
        self.sky.setFog(self.fog)

    def setNoFog(self):
        render.clearFog()
        self.sky.clearFog()
