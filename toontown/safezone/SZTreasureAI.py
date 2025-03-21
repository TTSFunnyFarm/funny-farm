from direct.directnotify import DirectNotifyGlobal

from toontown.safezone.TreasureAI import TreasureAI


class SZTreasureAI(TreasureAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZTreasure')

    def __init__(self, air, treasurePlanner, x, y, z):
        TreasureAI.__init__(self, air, treasurePlanner, x, y, z)
        self.healAmount = treasurePlanner.healAmount

    def validAvatar(self):
        return 0 < base.localAvatar.hp < base.localAvatar.maxHp

    def setGrab(self):
        TreasureAI.setGrab(self)
        if base.localAvatar:
            if self.validAvatar():
                hp = base.localAvatar.hp + self.healAmount
                base.localAvatar.setHealth(hp, base.localAvatar.maxHp, showText=1)
