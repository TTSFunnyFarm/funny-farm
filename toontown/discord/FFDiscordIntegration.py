import time

from direct.directnotify import DirectNotifyGlobal

from otp.discord.DiscordIPCClient import DiscordIPCClient


class FFDiscordIntegration:
    notify = DirectNotifyGlobal.directNotify.newCategory('FFDiscordIntegration')
    clientId = '561678749200941109'
    updatePeriod = 5

    def __init__(self, cr):
        self.cr = cr
        self.client = DiscordIPCClient.forPlatform(self.clientId)
        self.startTime = int(time.time())
        self.activity = {
            'state': 'In-Game',
            'assets': {
                'large_image': 'ttff-icon-1'
            },
            'timestamps': {
                'start': self.startTime
            }
        }

        self.sendActivity()

    def sendActivity(self, task=None):
        # This task runs even if there's no connection.
        # Clear the timestamp; its value will be reset if necessary.
        if 'timestamps' in self.activity and self.activity['timestamps']['start'] != self.startTime:
            del self.activity['timestamps']

        self.activity['state'] = 'In-Game'

        if 'timestamps' not in self.activity:
            self.activity['timestamps'] = {
                'start': self.startTime
            }

        self.client.setActivity(self.activity)

        if task:
            return task.again
        else:
            taskMgr.doMethodLater(self.updatePeriod, self.sendActivity, 'sendActivity')
