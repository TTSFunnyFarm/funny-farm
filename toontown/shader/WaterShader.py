from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import DirectObject
from direct.task import Task
from toontown.toon import Toon

WATER_SPEED = 0.03

class WaterShader(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory("WaterShader")
    def __init__(self):
        DirectObject.DirectObject.__init__(self)
        self.reflectionFB = None
        self.refractionFB = None
        self.shader = None
        self.geom = None
        self.reflectionCam = None
        self.refractionCam = None
        self.reflectGeom = None
        self.refractGeom = None
        self.reflectCP = None
        self.refractCP = None
        self.toon = None
        self.toonAnim = None
        self.toonAnimRate = None
        self.waterPos = 0

    def start(self, waterName, landGeom, sky):
        if self.shader is not None:
            self.notify.warning("Tried to generate WaterShader twice")
            return
        # Make geom copies
        self.reflectGeom = render.attachNewNode("refl")
        self.refractGeom = render.attachNewNode("refr")
        self.reflectGeom.detachNode()
        self.refractGeom.detachNode()
        landGeom.copyTo(self.reflectGeom)
        landGeom.copyTo(self.refractGeom)
        sky.copyTo(self.reflectGeom)
        sky.copyTo(self.refractGeom)
        self.reflectGeom.find('**/' + waterName).removeNode()
        self.refractGeom.find('**/' + waterName).removeNode()
        # Make framebuffers
        reflFactor = config.GetFloat("reflection-scale-factor", 0.25)
        refrFactor = config.GetFloat("refraction-scale-factor", 0.75)
        self.reflectionFB = base.win.makeTextureBuffer("waterRefl", int(base.win.getXSize() * reflFactor), int(base.win.getYSize() * reflFactor))
        self.refractionFB = base.win.makeTextureBuffer("waterRefr", int(base.win.getXSize() * refrFactor), int(base.win.getYSize() * refrFactor))
        self.reflectionCam = base.makeCamera(self.reflectionFB)
        self.refractionCam = base.makeCamera(self.refractionFB)
        self.reflectionCam.reparentTo(self.reflectGeom)
        self.refractionCam.reparentTo(self.refractGeom)
        self.reflectionCam.node().setLens(base.camLens)
        self.refractionCam.node().setLens(base.camLens)
        taskMgr.add(self.updateRefl, self.taskName('updateRefl'))
        taskMgr.add(self.updateRefr, self.taskName('updateRefr'))
        # Make a duplicate of the player
        self.toon = Toon.Toon()
        self.toon.setDNA(base.localAvatar.getDNA())
        self.toon.setHat(*base.avatarData.setHat)
        self.toon.setGlasses(*base.avatarData.setGlasses)
        self.toon.setBackpack(*base.avatarData.setBackpack)
        self.toon.setShoes(*base.avatarData.setShoes)
        self.toon.applyCheesyEffect(base.avatarData.setCheesyEffect)
        self.toon.hideName()
        self.toon.hideShadow()
        self.toon.reparentTo(self.refractGeom)
        self.toon.setAnimState('neutral', 1.0)
        taskMgr.add(self.updateToon, self.taskName('updateToon'))
        # Load shader
        self.shader = Shader.load(Shader.SL_GLSL, "phase_3/models/shaders/water_vert.glsl", "phase_3/models/shaders/water_frag.glsl")
        self.geom = landGeom.find('**/' + waterName)
        self.geom.setTransparency(TransparencyAttrib.M_alpha)
        self.reflectCP = self.reflectGeom.attachNewNode(PlaneNode("reflPlane", LPlane(0, 0, 1, -self.waterPos)))
        self.refractCP = self.refractGeom.attachNewNode(PlaneNode("refrPlane", LPlane(0, 0, -1, self.waterPos)))
        self.reflectGeom.setClipPlane(self.reflectCP)
        self.refractGeom.setClipPlane(self.refractCP)
        self.geom.setShader(self.shader)
        # Texture setup
        dudvMap = loader.loadTexture('phase_14/maps/water_dudv.jpg')
        self.reflectionFB.getTexture().setWrapU(Texture.WM_repeat)
        self.reflectionFB.getTexture().setWrapV(Texture.WM_repeat)
        self.refractionFB.getTexture().setWrapU(Texture.WM_repeat)
        self.refractionFB.getTexture().setWrapV(Texture.WM_repeat)
        dudvMap.setWrapV(Texture.WM_repeat)
        self.geom.setShaderInput("reflectTex", self.reflectionFB.getTexture())
        self.geom.setShaderInput("refractTex", self.refractionFB.getTexture())
        self.geom.setShaderInput("dudvMap", dudvMap)
        self.geom.setShaderInput("moveFactor", 0)
        self.geom.setShaderInput("cameraPos", base.camera.getPos(render))
        taskMgr.add(self.updateUniforms, self.taskName('updateUniforms'))


    def stop(self):
        taskMgr.remove(self.taskName('updateRefl'))
        taskMgr.remove(self.taskName('updateRefr'))
        taskMgr.remove(self.taskName('updateUniforms'))
        taskMgr.remove(self.taskName('updateToon'))
        if self.geom:
            self.geom.clearShader()
            self.geom = None
        # Remove shader
        if self.shader is not None:
            self.shader.releaseAll()
            self.shader = None
        # Remove framebuffers
        if self.reflectionFB is not None:
            self.reflectionFB.clearRenderTextures()
            base.graphicsEngine.removeWindow(self.reflectionFB)
            self.reflectionFB = None
        if self.refractionFB is not None:
            self.refractionFB.clearRenderTextures()
            base.graphicsEngine.removeWindow(self.refractionFB)
            self.refractionFB = None
        if self.reflectGeom:
            self.reflectGeom.removeNode()
            self.reflectGeom = None
        if self.refractGeom:
            self.refractGeom.removeNode()
            self.refractGeom = None
        if self.reflectCP:
            self.reflectCP.removeNode()
            self.reflectCP = None
        if self.refractCP:
            self.refractCP.removeNode()
            self.refractCP = None
        if self.toon:
            self.toon.delete()
            self.toon = None
        if self.reflectionCam:
            self.reflectionCam.removeNode()
            self.reflectionCam = None
        if self.refractionCam:
            self.refractionCam.removeNode()
            self.refractionCam = None
        self.toonAnim = None
        self.toonAnimRate = None

    def updateRefl(self, task):
        if self.reflectionCam is None:
            return Task.done
        dist = 2 * (base.cam.getZ(render) - self.waterPos)
        self.reflectionCam.setX(base.cam.getX(render))
        self.reflectionCam.setY(base.cam.getY(render))
        self.reflectionCam.setZ(base.cam.getZ(render) - dist)
        self.reflectionCam.setH(base.cam.getH(render))
        self.reflectionCam.setP(-base.cam.getP(render))
        self.reflectionCam.setR(-base.cam.getR(render))
        return Task.cont

    def updateRefr(self, task):
        if self.refractionCam is None:
            return Task.done
        self.refractionCam.setPos(*base.cam.getPos(render))
        self.refractionCam.setHpr(*base.cam.getHpr(render))
        return Task.cont

    def updateUniforms(self, task):
        moveFactor = (WATER_SPEED * globalClock.getFrameTime()) % 1
        self.geom.setShaderInput("moveFactor", moveFactor)
        self.geom.setShaderInput("cameraPos", base.cam.getPos(render))
        return Task.cont

    def updateToon(self, task):
        self.toon.setPos(base.localAvatar.getPos(render))
        self.toon.setHpr(base.localAvatar.getHpr(render))
        anim = self.toonAnim
        animRate = self.toonAnimRate
        playingAnim = base.localAvatar.getCurrentAnim()
        playingRate = base.localAvatar.getPlayRate()
        if playingAnim == None:
            playingAnim = base.localAvatar.playingAnim
        if anim != playingAnim or animRate != playingRate:
            self.toonAnim = playingAnim
            self.toonAnimRate = playingRate
            if playingAnim == 'jump-idle' or playingAnim == 'running-jump-idle':
                if playingAnim == 'running-jump-idle':
                    self.toon.playingAnim = None
                self.toon.setAnimState('jumpAirborne', 1.0)
            elif playingAnim == 'jump-land' or playingAnim == 'running-jump-land':
                self.toon.setAnimState('jumpLand', 1.0)
            elif playingAnim == 'openBook':
                self.toon.enterOpenBook()
            elif playingAnim == 'readBook':
                self.toon.enterReadBook()
            elif playingAnim == 'closeBook':
                self.toon.enterCloseBook()
            else:
                if self.toon.animFSM.getStateNamed(self.toonAnim):
                    self.toon.setAnimState(self.toonAnim, self.toonAnimRate)
                else:
                    self.toon.loop(self.toonAnim)
        return Task.cont

    def taskName(self, task):
        return "{0}-{1}".format(task, id(self))
