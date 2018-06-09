from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.SZTreasure import SZTreasure


class FFTreasure(SZTreasure):
    notify = DirectNotifyGlobal.directNotify.newCategory('FFTreasure')

    def __init__(self):
        SZTreasure.__init__(self)
        self.modelPath = 'phase_4/models/props/icecream'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
