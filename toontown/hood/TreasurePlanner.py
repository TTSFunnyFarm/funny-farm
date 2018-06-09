from direct.directnotify import DirectNotifyGlobal


class TreasurePlanner:
    notify = DirectNotifyGlobal.directNotify.newCategory('TreasurePlanner')

    def __init__(self, zoneId, treasureType, callback=None):
        self.zoneId = zoneId
        self.treasureType = treasureType
        self.callback = callback
        self.initSpawnPoints()
        self.treasures = []
        for spawnPoint in self.spawnPoints:
            self.treasures.append(None)

        self.deleteTaskNames = set()
        self.lastRequestId = None
        self.requestStartTime = None
        self.requestCount = None

    def initSpawnPoints(self):
        # Subclasses should override this.
        self.spawnPoints = []
        return self.spawnPoints
