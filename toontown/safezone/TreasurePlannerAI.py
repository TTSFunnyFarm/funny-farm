from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


class TreasurePlannerAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('TreasurePlannerAI')

    def __init__(self, zoneId, treasureConstructor, callback=None):
        DirectObject.__init__(self)
        self.zoneId = zoneId
        self.treasureConstructor = treasureConstructor
        self.callback = callback
