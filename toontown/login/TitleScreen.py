from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from direct.gui.DirectGui import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.effects.FireworkShowMixin import FireworkShowMixin
from toontown.parties import PartyGlobals
import random

class TitleScreen(DirectObject):
    notify = directNotify.newCategory('TitleScreen')

    def __init__(self):
        self.track = None
        base.disableMouse()
        base.setBackgroundColor(FunnyFarmGlobals.DefaultBackgroundColor)
        base.camLens.setMinFov(52.0/(4./3.))
        camera.setPosHpr(0, 0, 0, 0, -45, 0)
        self.titleText = None
        self.load()

    def load(self):
        if base.air.holidayMgr.isWinter():
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo_christmas')
        elif base.air.holidayMgr.isHalloween():
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo_halloween')
        else:
            self.logo = loader.loadModel('phase_3/models/gui/toontown-logo')
        self.logo.reparentTo(aspect2d)
        self.logo.setPos(0, 0, 0.2)
        self.logo.setSx(1.2)
        self.logo.hide()
        self.titleText = DirectLabel(parent=aspect2d, relief=None, pos=(0, 0, -0.5), text='Click to begin!', text_scale=0.1, text_fg=(1, 1, 1, 1), text_align=TextNode.ACenter, text_font=FunnyFarmGlobals.getMinnieFont(), text_shadow=(0, 0, 0, 1))
        self.titleText.hide()
        gameVersion = config.GetString('game-version', 'no_version_set')
        self.versionText = DirectLabel(parent=base.a2dBottomLeft, relief=None, pos=(0.033, 0, 0.025), text=gameVersion, text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_align=TextNode.ALeft, text_font=FunnyFarmGlobals.getMinnieFont(), text_shadow=(0, 0, 0, 1))
        self.versionText.hide()
        self.pandaLogo = loader.loadModel('phase_3/models/gui/panda3d_logo.bam')
        self.pandaLogo.reparentTo(base.a2dBottomRight)
        self.pandaLogo.setPos(-0.22, 0, 0.07)
        self.pandaLogo.setScale(0.4)
        self.pandaLogo.hide()
        pandaText = DirectLabel(parent=self.pandaLogo, relief=None, pos=(0, 0, 0.08), text='Powered by', text_scale=0.1, text_fg=Vec4(1, 1, 1, 1), text_align=TextNode.ACenter, text_font=FunnyFarmGlobals.getMinnieFont(), text_shadow=(0, 0, 0, 1))
        if base.air.holidayMgr.isWinter():
            self.ground = loader.loadModel('phase_4/models/minigames/toon_cannon_gameground_winter')
        else:
            self.ground = loader.loadModel('phase_4/models/minigames/toon_cannon_gameground')
        self.ground.reparentTo(render)
        self.ground.setScale(1.1)
        self.ground.setColorScale(0.55, 0.55, 0.55, 1.0)
        self.ground.flattenStrong()
        self.sky = loader.loadModel('phase_8/models/props/DL_sky')
        self.sky.reparentTo(render)
        self.sky.setScale(2.0)
        self.sky.flattenStrong()
        self.fireworkShow = FireworkShowMixin()

    def unload(self):
        self.ignoreAll()
        taskMgr.remove('showTimeout')
        self.logo.removeNode()
        self.titleText.destroy()
        self.versionText.destroy()
        self.pandaLogo.removeNode()
        self.ground.removeNode()
        self.sky.removeNode()
        self.fireworkShow.disable()
        del self.logo
        self.titleText = None
        del self.versionText
        del self.pandaLogo
        del self.ground
        del self.sky
        del self.fireworkShow

    def startShow(self):
        self.track = Sequence()
        self.track.append(camera.posHprInterval(6.0, pos=(0, -350, 55), hpr=(0, 12, 0), blendType='easeInOut'))
        self.track.append(Func(self.logo.show))
        self.track.append(self.logo.colorScaleInterval(2.0, colorScale=(1, 1, 1, 1), startColorScale=(1, 1, 1, 0)))
        self.track.append(Func(self.versionText.show))
        self.track.append(self.versionText.colorScaleInterval(1.0, colorScale=(1, 1, 1, 1), startColorScale=(1, 1, 1, 0)))
        self.track.append(Func(self.pandaLogo.show))
        self.track.append(self.pandaLogo.colorScaleInterval(1.0, colorScale=(1, 1, 1, 1), startColorScale=(1, 1, 1, 0)))
        self.track.append(Func(self.titleText.show))
        self.track.append(self.titleText.colorScaleInterval(1.0, colorScale=(1, 1, 1, 1), startColorScale=(1, 1, 1, 0)))
        self.titleSeq = Sequence(self.titleText.colorScaleInterval(1.0, (1, 1, 1, 0.2)), self.titleText.colorScaleInterval(1.0, (1, 1, 1, 1)))
        self.track.append(Func(self.titleSeq.loop))
        self.track.append(Func(self.acceptOnce, 'mouse1', self.exitShow))
        if base.air.holidayMgr.isWinter():
            showTypes = [FunnyFarmGlobals.CHRISTMAS_FIREWORKS]
            print('yeh')
        else:
            showTypes = [FunnyFarmGlobals.JULY4_FIREWORKS, PartyGlobals.FireworkShows.Summer]
        self.fireworkShow.startShow(random.choice(showTypes), 0, 0, 0)
        taskMgr.doMethodLater(self.fireworkShow.fireworkShow.getShowDuration(), self.exitShow, 'showTimeout')
        self.track.start()

    def exitShow(self, *args):
        self.track.finish()
        self.titleSeq.finish()
        self.track = Sequence()
        self.track.append(Parallel(self.titleText.colorScaleInterval(1.0, (1, 1, 1, 0)), Sequence(Func(base.transitions.fadeOut, 1.0), Wait(1.5), Func(self.unload), Func(base.cr.begin))))
        self.track.start()
        return Task.done
