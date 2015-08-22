import yaml.dist as yaml
import binascii

class Account(yaml.YAMLObject):
	yaml_tag = 'Account'

	def __init__(self, username=None, accessLevel=0):
		self.username = username
		self.accessLevel = accessLevel
		self.WARNING = 'DO NOT EDIT. This is ENCRYPTED data. Changing ANY of it will crash your game.'

	def setUsername(self, name):
		self.username = name

	def getUsername(self):
		return self.username

	def setAccessLevel(self, level):
		self.accessLevel = level

	def getAccessLevel(self):
		return self.accessLevel

	def encrypt(self):
		self.username = binascii.hexlify(self.username)
		self.accessLevel = hex(self.accessLevel)

	def decrypt(self):
		self.username = binascii.unhexlify(self.username)
		self.accessLevel = int(self.accessLevel, 0)