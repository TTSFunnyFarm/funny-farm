from panda3d.core import *
from toontown.toon.NPCToonBase import *
from toontown.minigame import ClerkPurchase
from toontown.book.PurchaseManagerConstants import *
from toontown.toon import NPCToons
from direct.task.Task import Task
from toontown.toonbase import TTLocalizer
from toontown.hood import ZoneUtil
from toontown.toontowngui import TeaserPanel
from otp.nametag.NametagConstants import *

class NPCClerk(NPCToonBase):

    def __init__(self):
        NPCToonBase.__init__(self)
        self.purchase = None
        self.isLocalToon = 0
        self.av = None
        self.timedOut = 0
        self.purchaseDoneEvent = 'purchaseDone'
        return

    def disable(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.purchase:
            self.purchase.exit()
            self.purchase.unload()
            self.purchase = None
        self.av = None
        base.localAvatar.posCamera(0, 0)
        NPCToonBase.disable(self)
        return

    def allowedToEnter(self):
        return True

    def handleOkTeaser(self):
        self.dialog.destroy()
        del self.dialog
        place = base.cr.playGame.hood.place
        if place:
            place.fsm.request('walk')

    def handleCollisionSphereEnter(self, collEntry):
        if self.allowedToEnter():
            base.localAvatar.disable()
            base.localAvatar.setAnimState('neutral', 1)
            self.avatarEnter()
        else:
            base.localAvatar.disable()
            base.localAvatar.setAnimState('neutral', 1)
            self.dialog = TeaserPanel.TeaserPanel(pageName='otherGags', doneFunc=self.handleOkTeaser)

    def __handleUnexpectedExit(self):
        self.notify.warning('unexpected exit')
        self.av = None
        return

    def resetClerk(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.purchase:
            self.purchase.exit()
            self.purchase.unload()
            self.purchase = None
        self.setH(180)
        self.startLookAround()
        self.detectAvatars()
        if self.isLocalToon:
            self.freeAvatar()
        return Task.done

    def setMovie(self, mode, npcId, avId, timestamp):
        timeStamp = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.remain = NPCToons.CLERK_COUNTDOWN_TIME - timeStamp
        self.isLocalToon = avId == base.localAvatar.doId
        if mode == NPCToons.PURCHASE_MOVIE_CLEAR:
            return
        if mode == NPCToons.PURCHASE_MOVIE_TIMEOUT:
            taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
            taskMgr.remove(self.uniqueName('lerpCamera'))
            if self.isLocalToon:
                self.ignore(self.purchaseDoneEvent)
            if self.purchase:
                self.__handlePurchaseDone()
            self.setChatAbsolute(TTLocalizer.STOREOWNER_TOOKTOOLONG, CFSpeech | CFTimeout)
            self.resetClerk()
        elif mode == NPCToons.PURCHASE_MOVIE_START:
            self.av = base.localAvatar
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                self.accept(self.av.uniqueName('disable'), self.__handleUnexpectedExit)
            self.setupAvatars(self.av)
            if self.isLocalToon:
                camera.wrtReparentTo(render)
                self.cameraLerp = LerpPosQuatInterval(camera, 1, Point3(-5, 9, self.getHeight() - 0.5), Point3(-150, -2, 0), other=self, blendType='easeInOut')
                self.cameraLerp.start()
            self.setChatAbsolute(TTLocalizer.STOREOWNER_GREETING, CFSpeech | CFTimeout)
            if self.isLocalToon:
                taskMgr.doMethodLater(1.0, self.popupPurchaseGUI, self.uniqueName('popupPurchaseGUI'))
        elif mode == NPCToons.PURCHASE_MOVIE_COMPLETE:
            self.setChatAbsolute(TTLocalizer.STOREOWNER_GOODBYE, CFSpeech | CFTimeout)
            self.resetClerk()
        elif mode == NPCToons.PURCHASE_MOVIE_NO_MONEY:
            self.setChatAbsolute(TTLocalizer.STOREOWNER_NEEDJELLYBEANS, CFSpeech | CFTimeout)
            self.resetClerk()
        return

    def popupPurchaseGUI(self, task):
        self.setChatAbsolute('', CFSpeech)
        self.acceptOnce(self.purchaseDoneEvent, self.__handlePurchaseDone)
        self.accept('boughtGag', self.__handleBoughtGag)
        self.purchase = ClerkPurchase.ClerkPurchase(base.localAvatar, self.remain, self.purchaseDoneEvent)
        self.purchase.load()
        self.purchase.enter()
        return Task.done

    def __handleBoughtGag(self):
        self.setInventory(base.localAvatar.inventory.exportInventoryData(), base.localAvatar.getMoney(), 0)

    def __handlePurchaseDone(self):
        self.ignore('boughtGag')
        self.setInventory(base.localAvatar.inventory.exportInventoryData(), base.localAvatar.getMoney(), 1)
        if self.purchase:
            self.purchase.exit()
            self.purchase.unload()
            self.purchase = None
        return

    ### AI functions (rather, what normally are AI functions) ###

    def avatarEnter(self):
        avId = base.localAvatar.getDoId()
        NPCToonBase.avatarEnter(self)
        av = base.localAvatar
        if av is None:
            self.notify.warning('toon isnt there! toon: %s' % avId)
            return
        if self.isBusy():
            self.freeAvatar(avId)
            return
        if av.getMoney():
            self.sendStartMovie(avId)
        else:
            self.sendNoMoneyMovie(avId)
        return

    def sendStartMovie(self, avId):
        self.busy = avId
        self.setMovie(NPCToons.PURCHASE_MOVIE_START,
         self.npcId,
         avId,
         ClockDelta.globalClockDelta.getRealNetworkTime())
        taskMgr.doMethodLater(NPCToons.CLERK_COUNTDOWN_TIME, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def sendNoMoneyMovie(self, avId):
        self.busy = avId
        self.setMovie(NPCToons.PURCHASE_MOVIE_NO_MONEY,
         self.npcId,
         avId,
         ClockDelta.globalClockDelta.getRealNetworkTime())
        self.sendClearMovie(None)
        return

    def sendTimeoutMovie(self, task):
        self.timedOut = 1
        self.setMovie(NPCToons.PURCHASE_MOVIE_TIMEOUT,
         self.npcId,
         self.busy,
         ClockDelta.globalClockDelta.getRealNetworkTime())
        self.sendClearMovie(None)
        return Task.done

    def sendClearMovie(self, task):
        self.busy = 0
        self.timedOut = 0
        self.setMovie(NPCToons.PURCHASE_MOVIE_CLEAR,
         self.npcId,
         0,
         ClockDelta.globalClockDelta.getRealNetworkTime())
        return Task.done

    def completePurchase(self, avId):
        self.busy = avId
        self.setMovie(NPCToons.PURCHASE_MOVIE_COMPLETE,
         self.npcId,
         avId,
         ClockDelta.globalClockDelta.getRealNetworkTime())
        self.sendClearMovie(None)
        return

    def setInventory(self, invData, newMoney, done):
        avId = base.localAvatar.getDoId()
        if self.busy != avId:
            if self.busy != 0:
                self.notify.warning('setInventory from unknown avId: %s busy: %s' % (avId, self.busy))
            return
        if avId:
            av = base.localAvatar
            newInventory = av.inventory.makeFromInventoryData(invData)
            currentMoney = av.getMoney()
            if av.inventory.validatePurchase(newInventory, currentMoney, newMoney):
                av.setMoney(newMoney)
                if done:
                    av.setInventory(av.inventory.exportInventoryData())
                    av.setMoney(newMoney)
            else:
                self.notify.warning('Avatar ' + str(avId) + ' attempted an invalid purchase.')
                av.setInventory(av.inventory.exportInventoryData())
                av.setMoney(av.getMoney())
        if self.timedOut:
            return
        if done:
            taskMgr.remove(self.uniqueName('clearMovie'))
            self.completePurchase(avId)

    def __handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        self.sendTimeoutMovie(None)
        return
