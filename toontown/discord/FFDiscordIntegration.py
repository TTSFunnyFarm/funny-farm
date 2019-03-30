import time

from direct.directnotify import DirectNotifyGlobal

from otp.discord.DiscordIPCClient import DiscordIPCClient


class FFDiscordIntegration:
    notify = DirectNotifyGlobal.directNotify.newCategory('FFDiscordIntegration')
    clientId = ''  # TODO
    updatePeriod = 5

    def __init__(self, cr):
        self.cr = cr
        self.client = DiscordIPCClient.forPlatform(self.clientId)
        self.startTime = int(time.time())
