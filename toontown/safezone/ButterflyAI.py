import random

from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from direct.showbase.DirectObject import DirectObject

from toontown.safezone import ButterflyGlobals


class ButterflyAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ButterflyAI')

    def __init__(self, air, playground, area, ownerId):
        DirectObject.__init__(self)
        self.doId = id(self)
        self.air = air
        self.playground = playground
        self.area = area
        self.ownerId = ownerId
        self.fsm = ClassicFSM.ClassicFSM('ButterflyAI', [
            State.State('off', self.enterOff, self.exitOff, [
                'Flying', 'Landed']),
            State.State('Flying', self.enterFlying, self.exitFlying, [
                'Landed']),
            State.State('Landed', self.enterLanded, self.exitLanded, [
                'Flying'])], 'off', 'off')
        self.fsm.enterInitialState()
        self.curPos, self.curIndex, self.destPos, self.destIndex, self.time = ButterflyGlobals.getFirstRoute(
            self.playground, self.area, self.ownerId)
        self.stateIndex = 0

    def generate(self):
        messenger.send('generateButterfly', [{'area': self.getArea(),
                                              'doId': self.getDoId(),
                                              'state': self.getState()}])

    def delete(self):
        ButterflyGlobals.recycleIndex(self.curIndex, self.playground, self.area, self.ownerId)
        ButterflyGlobals.recycleIndex(self.destIndex, self.playground, self.area, self.ownerId)
        self.fsm.request('off')
        del self.fsm
        self.deleteClientButterfly()

    def d_setState(self, stateIndex, curIndex, destIndex, time):
        clientButterfly = self.getClientButterfly()
        if clientButterfly:
            clientButterfly.setState(stateIndex, curIndex, destIndex, time, globalClockDelta.getRealNetworkTime())

    def getArea(self):
        return [self.playground, self.area]

    def getState(self):
        return [self.stateIndex, self.curIndex, self.destIndex, self.time, globalClockDelta.getRealNetworkTime()]

    def start(self):
        self.fsm.request('Flying')

    def avatarEnter(self):
        if self.fsm.getCurrentState().getName() == 'Landed':
            self.__ready()
        return None

    def enterOff(self):
        self.stateIndex = ButterflyGlobals.OFF
        return None

    def exitOff(self):
        return None

    def enterFlying(self):
        self.stateIndex = ButterflyGlobals.FLYING
        ButterflyGlobals.recycleIndex(self.curIndex, self.playground, self.area, self.ownerId)
        self.d_setState(ButterflyGlobals.FLYING, self.curIndex, self.destIndex, self.time)
        taskMgr.doMethodLater(self.time, self.__handleArrival, self.uniqueName('butter-flying'))
        return None

    def exitFlying(self):
        taskMgr.remove(self.uniqueName('butter-flying'))
        return None

    def __handleArrival(self, task):
        self.curPos = self.destPos
        self.curIndex = self.destIndex
        self.fsm.request('Landed')
        return task.done

    def enterLanded(self):
        self.stateIndex = ButterflyGlobals.LANDED
        self.time = random.random() * ButterflyGlobals.MAX_LANDED_TIME
        self.d_setState(ButterflyGlobals.LANDED, self.curIndex, self.destIndex, self.time)
        taskMgr.doMethodLater(self.time, self.__ready, self.uniqueName('butter-ready'))
        return None

    def exitLanded(self):
        taskMgr.remove(self.uniqueName('butter-ready'))
        return None

    def __ready(self, task=None):
        self.destPos, self.destIndex, self.time = ButterflyGlobals.getNextPos(self.curPos, self.playground, self.area,
                                                                              self.ownerId)
        self.fsm.request('Flying')
        if task:
            return task.done

    def getDoId(self):
        return self.doId

    def uniqueName(self, idString):
        return idString + '-' + str(self.getDoId())

    def getClientButterfly(self):
        if not hasattr(base.cr.playGame.hood, 'butterflies'):
            return

        butterflies = base.cr.playGame.hood.butterflies[:]
        if not butterflies:
            return

        clientButterfly = None
        for butterfly in butterflies:
            if butterfly and butterfly.getDoId() == self.getDoId():
                clientButterfly = butterfly
                break

        return clientButterfly

    def deleteClientButterfly(self):
        clientButterfly = self.getClientButterfly()
        if clientButterfly:
            clientButterfly.cleanup()
