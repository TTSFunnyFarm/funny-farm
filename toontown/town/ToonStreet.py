from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase import FunnyFarmGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import FFTime

class ToonStreet(DirectObject):
	notify = directNotify.newCategory('ToonStreet')

	def __init__(self):
		self.zoneId = None
		self.streetFile = None
		self.spookyStreetFile = None
		self.winterStreetFile = None
		self.skyFile = None
		self.spookySkyFile = 'phase_3.5/models/props/BR_sky'
		self.titleText = None
		self.titleColor = (1, 1, 1, 1)

	def enter(self, tunnel=None):
		base.localAvatar.setZoneId(self.zoneId)
		self.titleText = OnscreenText(self.titleText, fg=self.titleColor, font=ToontownGlobals.getSignFont(), pos=(0, -0.5), scale=TTLocalizer.HtitleText, drawOrder=0, mayChange=1)
		self.spawnTitleText()

	def exit(self):
		self.ignoreAll()
		if self.titleText:
			self.titleText.cleanup()
			self.titleText = None

	def load(self):
		if FFTime.isHalloween():
			self.geom = loader.loadModel(self.spookyStreetFile)
			self.sky = loader.loadModel(self.spookySkyFile)
			self.sky.setColorScale(0.5, 0.5, 0.5, 1)
		elif FFTime.isWinter():
			self.geom = loader.loadModel(self.winterStreetFile)
			self.sky = loader.loadModel(self.spookySkyFile)
		else:
			self.geom = loader.loadModel(self.streetFile)
			self.sky = loader.loadModel(self.skyFile)
		
		self.geom.reparentTo(render)
		self.sky.reparentTo(render)

	def unload(self):
		self.geom.removeNode()
		self.sky.removeNode()
		del self.geom
		del self.sky

	def spawnTitleText(self):
		self.titleText.show()
		self.titleText.setColor(Vec4(*self.titleColor))
		self.titleText.clearColorScale()
		self.titleText.setFg(self.titleColor)
		seq = Sequence(Wait(0.1), Wait(6.0), self.titleText.colorScaleInterval(0.5, Vec4(1.0, 1.0, 1.0, 0.0)), Func(self.titleText.hide))
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