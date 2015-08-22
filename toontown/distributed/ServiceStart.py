from pandac.PandaModules import *

loadPrcFile('config/config_en.prc')
loadPrcFileData('', 'window-type none')

from direct.directbase import DirectStart
from direct.distributed.ServerRepository import ServerRepository
from direct.distributed.ClientRepository import ClientRepository
from direct.directnotify import DirectNotifyGlobal
import sys

class FunnyFarmServerRepository(ServerRepository):

	def __init__(self):
		self.notify.setInfo(True)
		tcpPort = 12070
		hostname = '127.0.0.1'
		dcFileNames = ['dcFiles/direct.dc', 'dcFiles/toon.dc']
		ServerRepository.__init__(self, tcpPort, serverAddress = hostname, dcFileNames = dcFileNames)
		self.setTcpHeaderSize(4)
		base.setSleep(0.01)

class FunnyFarmAIRepository(ClientRepository):
	notify = directNotify.newCategory('AIRepository')

	def __init__(self):
		self.notify.setInfo(True)
		dcFileNames = ['dcFiles/direct.dc', 'dcFiles/toon.dc']	
		ClientRepository.__init__(self, dcFileNames = dcFileNames, dcSuffix = 'AI')
		self.setTcpHeaderSize(4)
		base.setSleep(0.01)
		tcpPort = 12070
		url = URLSpec('http://127.0.0.1:%s' % tcpPort)
		self.connect([url],
					successCallback = self.connectSuccess,
					failureCallback = self.connectFailure)

	def connectFailure(self, statusCode, statusString):
		raise StandardError, statusString
		
	def connectSuccess(self):
		self.notify.info('Creating AI server globals...')
		self.acceptOnce('createReady', self.createReady)
	
	def createReady(self):
		self.timeManager = self.createDistributedObject(
			className = 'TimeManagerAI', zoneId = 1)

FunnyFarmServerRepository()
FunnyFarmAIRepository()

run()
