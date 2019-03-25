from direct.showbase.DirectObject import DirectObject

class BuildingAI(DirectObject):
    notify = directNotify.newCategory('Building')
    TOON_STATE = 'toon'
    SUIT_STATE = 'suit'
    ELITE_STATE = 'elite'

    def __init__(self, zoneId, block):
        self.block = block
        self.zoneId = zoneId + 500 + block
        self.mode = self.TOON_STATE
        self.track = None
        self.difficulty = None
        self.numFloors = None

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, self.doId))

    def generate(self):
        pass

    def delete(self):
        pass

    def suitTakeOver(self, track, difficulty, numFloors):
        self.mode = self.SUIT_STATE
        self.track = track
        self.difficulty = difficulty
        self.numFloors = numFloors
        messenger.send('suitTakeOver-%d' % self.zoneId, [track, difficulty, numFloors])

    def eliteTakeOver(self, track):
        self.mode = self.ELITE_STATE
        self.track = track
        messenger.send('eliteTakeOver-%d' % self.zoneId, [track])

    def toonTakeOver(self):
        self.mode = self.TOON_STATE
        messenger.send('toonTakeOver-%d' % self.zoneId)
