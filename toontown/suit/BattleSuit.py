from panda3d.core import *
from libotp import *
from direct.showbase import PythonUtil
from direct.controls.ControlManager import CollisionHandlerRayStart
from direct.interval.IntervalGlobal import *
from direct.task import Task
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.battle import BattleProps
from otp.otpbase import OTPGlobals
from toontown.suit.SuitBase import SuitBase
from toontown.suit.Suit import Suit
from toontown.suit import SuitDialog
from toontown.suit import SuitTimings
import math

class BattleSuit(Suit, SuitBase):
    notify = directNotify.newCategory('BattleSuit')
    HpTextGenerator = TextNode('HpTextGenerator')
    HpTextEnabled = 1

    def __init__(self):
        Suit.__init__(self)
        SuitBase.__init__(self)
        self.doId = 0
        self.activeShadow = 0
        self.virtual = 0
        self.battleDetectName = None
        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None
        self.cRayBitMask = None
        self.lifter = None
        self.cTrav = None
        self.sp = None
        self.fsm = None
        self.prop = None
        self.propInSound = None
        self.propOutSound = None
        self.battleTrapProp = None
        self.reparentTo(hidden)
        self.loop('neutral')
        self.skeleRevives = 0
        self.maxSkeleRevives = 0
        self.reviveFlag = 0
        self.sillySurgeText = False
        self.interactivePropTrackBonus = -1
        self.hpText = None
        self.strText = None
        self.hp = None
        self.maxHP = None
        return

    def setDoId(self, doId):
        self.doId = doId

    def getDoId(self):
        return self.doId

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, self.doId))

    def disable(self):
        self.notify.debug('BattleSuit %d: disabling' % self.getDoId())
        self.ignoreAll()
        self.__removeCollisionData()
        self.cleanupLoseActor()
        self.stop()
        taskMgr.remove(self.uniqueName('blink-task'))
        if hasattr(self, 'mtrack'):
            self.mtrack.pause()
            del self.mtrack

    def delete(self):
        self.notify.debug('BattleSuit %d: deleting' % self.getDoId())
        if hasattr(self, 'dna'):
            del self.dna
        if hasattr(self, 'sp'):
            del self.sp
        Suit.delete(self)
        SuitBase.delete(self)

    def setVirtual(self, virtual):
        pass

    def getVirtual(self):
        return 0

    def setSkeleRevives(self, num):
        if num == None:
            num = 0
        self.skeleRevives = num
        if num > self.maxSkeleRevives:
            self.maxSkeleRevives = num
        if self.getSkeleRevives() > 0:
            nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self._name,
             'dept': self.getStyleDept(),
             'level': '%s%s' % (self.getActualLevel(), TTLocalizer.SkeleRevivePostFix)}
            self.setDisplayName(nameInfo)
        else:
            nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self._name,
             'dept': self.getStyleDept(),
             'level': self.getActualLevel()}
            self.setDisplayName(nameInfo)
        return

    def getSkeleRevives(self):
        return self.skeleRevives

    def getMaxSkeleRevives(self):
        return self.maxSkeleRevives

    def useSkeleRevive(self):
        self.skeleRevives -= 1
        self.currHP = self.maxHP
        self.reviveFlag = 1

    def reviveCheckAndClear(self):
        returnValue = 0
        if self.reviveFlag == 1:
            returnValue = 1
            self.reviveFlag = 0
        return returnValue

    def setDNAString(self, dnaString):
        Suit.setDNAString(self, dnaString)

    def setDNA(self, dna):
        Suit.setDNA(self, dna)
        self.dna = dna

    def getHP(self):
        return self.currHP

    def setHP(self, hp):
        if hp > self.maxHP:
            self.currHP = self.maxHP
        else:
            self.currHP = hp
        return None

    def getDialogueArray(self, *args):
        return Suit.getDialogueArray(self, *args)

    def __removeCollisionData(self):
        self.enableRaycast(0)
        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None
        self.lifter = None
        self.cTrav = None
        return

    def setHeight(self, height):
        Suit.setHeight(self, height)

    def getRadius(self):
        return Suit.getRadius(self)

    def setLevelDist(self, level):
        if self.notify.getDebug():
            self.notify.debug('Got level %d from server for suit %d' % (level, self.getDoId()))
        self.setLevel(level)

    def attachPropeller(self):
        if self.prop == None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        if self.propInSound == None:
            self.propInSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        if self.propOutSound == None:
            self.propOutSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        if base.config.GetBool('want-new-cogs', 0):
            head = self.find('**/to_head')
            if head.isEmpty():
                head = self.find('**/joint_head')
        else:
            head = self.find('**/joint_head')
        self.prop.reparentTo(head)
        return

    def detachPropeller(self):
        if self.prop:
            self.prop.cleanup()
            self.prop.removeNode()
            self.prop = None
        if self.propInSound:
            self.propInSound = None
        if self.propOutSound:
            self.propOutSound = None
        return

    def beginSupaFlyMove(self, pos, moveIn, trackName, walkAfterLanding=True):
        skyPos = Point3(pos)
        if moveIn:
            skyPos.setZ(pos.getZ() + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
        else:
            skyPos.setZ(pos.getZ() + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)
        groundF = 28
        dur = self.getDuration('landing')
        fr = self.getFrameRate('landing')
        if fr:
            animTimeInAir = groundF / fr
        else:
            animTimeInAir = groundF
        impactLength = dur - animTimeInAir
        timeTillLanding = SuitTimings.fromSky - impactLength
        waitTime = timeTillLanding - animTimeInAir
        if self.prop == None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        propDur = self.prop.getDuration('propeller')
        lastSpinFrame = 8
        fr = self.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame + 1) / fr
        if moveIn:
            lerpPosTrack = Sequence(self.posInterval(timeTillLanding, pos, startPos=skyPos), Wait(impactLength))
            shadowScale = self.dropShadow.getScale()
            shadowTrack = Sequence(Func(self.dropShadow.reparentTo, render), Func(self.dropShadow.setPos, pos), self.dropShadow.scaleInterval(timeTillLanding, self.scale, startScale=Vec3(0.01, 0.01, 1.0)), Func(self.dropShadow.reparentTo, self.getShadowJoint()), Func(self.dropShadow.setPos, 0, 0, 0), Func(self.dropShadow.setScale, shadowScale))
            fadeInTrack = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 1), startColorScale=VBase4(1, 1, 1, 0)), Func(self.clearColorScale), Func(self.clearTransparency))
            animTrack = Sequence(Func(self.pose, 'landing', 0), Wait(waitTime), ActorInterval(self, 'landing', duration=dur))
            if walkAfterLanding:
                animTrack.append(Func(self.loop, 'walk'))
            else:
                animTrack.append(Func(self.loop, 'neutral'))
            self.attachPropeller()
            propTrack = Parallel(Sequence(ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=waitTime + spinTime, startTime=0.0, endTime=spinTime), ActorInterval(self.prop, 'propeller', duration=propDur - openTime, startTime=openTime), Func(self.detachPropeller)))
            if hasattr(base.cr.playGame.getActiveZone(), 'place') and not base.cr.playGame.getActiveZone().place:
                propTrack.append(SoundInterval(self.propInSound, duration=waitTime + dur, node=self))
            return Parallel(lerpPosTrack, shadowTrack, fadeInTrack, animTrack, propTrack, name=self.uniqueName('trackName'))
        else:
            lerpPosTrack = Sequence(Wait(impactLength), LerpPosInterval(self, timeTillLanding, skyPos, startPos=pos))
            shadowTrack = Sequence(Func(self.dropShadow.reparentTo, render), Func(self.dropShadow.setPos, pos), self.dropShadow.scaleInterval(timeTillLanding, Vec3(0.01, 0.01, 1.0), startScale=self.scale), Func(self.dropShadow.reparentTo, self.getShadowJoint()), Func(self.dropShadow.setPos, 0, 0, 0))
            fadeOutTrack = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 0), startColorScale=VBase4(1, 1, 1, 1)), Func(self.clearColorScale), Func(self.clearTransparency), Func(self.reparentTo, hidden))
            actInt = ActorInterval(self, 'landing', loop=0, startTime=dur, endTime=0.0)
            self.attachPropeller()
            self.prop.hide()
            propTrack = Parallel(Sequence(Func(self.prop.show), ActorInterval(self.prop, 'propeller', endTime=openTime, startTime=propDur), ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=propDur - openTime, startTime=spinTime, endTime=0.0), Func(self.detachPropeller)))
            if hasattr(base.cr.playGame.getActiveZone(), 'place') and not base.cr.playGame.getActiveZone().place:
                propTrack.append(SoundInterval(self.propOutSound, duration=waitTime + dur, node=self))
            return Parallel(ParallelEndTogether(lerpPosTrack, shadowTrack, fadeOutTrack), actInt, propTrack, name=self.uniqueName('trackName'))
        return

    def enableBattleDetect(self, handler):
        self.collNodePath.setName(self.uniqueName(self.collNodePath.getName()))
        self.accept('enter' + self.collNodePath.getName(), handler)
        return Task.done

    def disableBattleDetect(self):
        self.ignore('enter' + self.collNodePath.getName())
        return

    def enableRaycast(self, enable = 1):
        if not self.cTrav or not hasattr(self, 'cRayNode') or not self.cRayNode:
            return
        self.cTrav.removeCollider(self.cRayNodePath)
        if enable:
            if self.notify.getDebug():
                self.notify.debug('enabling raycast')
            self.cTrav.addCollider(self.cRayNodePath, self.lifter)
        elif self.notify.getDebug():
            self.notify.debug('disabling raycast')

    def initializeBodyCollisions(self, collIdStr):
        Suit.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)
        self.cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        self.cRayNode = CollisionNode('cRay')
        self.cRayNode.addSolid(self.cRay)
        self.cRayNodePath = self.attachNewNode(self.cRayNode)
        self.cRayNodePath.hide()
        self.cRayBitMask = ToontownGlobals.FloorBitmask
        self.cRayNode.setFromCollideMask(self.cRayBitMask)
        self.cRayNode.setIntoCollideMask(BitMask32.allOff())
        self.lifter = CollisionHandlerFloor()
        self.lifter.setOffset(ToontownGlobals.FloorOffset)
        self.lifter.setReach(6.0)
        self.lifter.setMaxVelocity(8.0)
        self.lifter.addCollider(self.cRayNodePath, self)
        self.lifter.addInPattern('enter%in')
        self.lifter.addAgainPattern(str(self.doId) + '-again%in')
        self.lifter.addOutPattern('exit%in')
        self.cTrav = base.cTrav

    def disableBodyCollisions(self):
        self.disableBattleDetect()
        self.enableRaycast(0)
        if self.cRayNodePath:
            self.cRayNodePath.removeNode()
        del self.cRayNode
        del self.cRay
        del self.lifter

    def setState(self, state):
        if self.fsm == None:
            return 0
        if self.fsm.getCurrentState().getName() == state:
            return 0
        return self.fsm.request(state)

    def setBrushOff(self, index):
        self.setChatAbsolute(SuitDialog.getBrushOffText(self.getStyleName(), index), CFSpeech | CFTimeout)

    def __handleBrushOff(self, collEntry):
        self.setBrushOff(SuitDialog.getBrushOffIndex(self.getStyleName()))

    def __handleToonCollision(self, collEntry):
        toonId = base.localAvatar.getDoId()
        self.notify.debug('BattleSuit: requesting a Battle with toon: %d' % toonId)
        self.exitWalk()
        self.enterWaitForBattle()
        messenger.send('requestBattle-%d' % base.localAvatar.zoneId, [self.doId, self.getPos()])

    def calculateHeading(self, a, b):
        xdelta = b[0] - a[0]
        ydelta = b[1] - a[1]
        if ydelta == 0:
            if xdelta > 0:
                h = -90
            else:
                h = 90
        elif xdelta == 0:
            if ydelta > 0:
                h = 0
            else:
                h = 180
        else:
            angle = math.atan2(ydelta, xdelta)
            h = rad2Deg(angle) - 90
        return PythonUtil.fitDestAngle2Src(self.getH(), h)

    def startUpdatePosition(self):
        self.accept('updatePos-%d' % self.doId, self.updatePosition)

    def updatePosition(self, posA, posB):
        self.exitWalk()
        self.enterWalk(posA, posB, 0)

    def stopUpdatePosition(self):
        self.ignore('updatePos-%d' % self.doId)

    def enterOff(self, *args):
        self.hideNametag3d()
        self.hideNametag2d()
        self.wrtReparentTo(hidden)

    def exitOff(self):
        self.wrtReparentTo(render)
        self.showNametag3d()
        self.showNametag2d()
        self.loop('neutral', 0)

    def enterFromSky(self, posA, posB):
        self.enableBattleDetect(self.__handleBrushOff)
        self.loop('neutral', 0)
        h = self.calculateHeading(posA, posB)
        self.setPosHprScale(posA[0], posA[1], posA[2], h, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.mtrack = self.beginSupaFlyMove(posA, 1, 'fromSky')
        self.mtrack.start()

    def exitFromSky(self):
        self.disableBattleDetect()
        self.mtrack.finish()
        del self.mtrack
        self.detachPropeller()

    def enterWalk(self, posA, posB, time):
        self.enableBattleDetect(self.__handleToonCollision)
        self.loop('walk', 0)
        h = self.calculateHeading(posA, posB)
        pos = self.getPosAtTime(posA, posB, time)
        self.setPos(pos[0], pos[1], pos[2])
        self.hprInterval(0.2, (h, 0, 0)).start()
        self.mtrack = Sequence(LerpPosInterval(self, self.getLegTime(posA, posB), posB, startPos=posA), name=self.uniqueName('bellicose'))
        self.mtrack.start(time)

    def exitWalk(self):
        self.disableBattleDetect()
        if hasattr(self, 'mtrack'):
            self.mtrack.pause()
            del self.mtrack

    def enterToSky(self):
        self.enableBattleDetect(self.__handleBrushOff)
        self.mtrack = self.beginSupaFlyMove(self.getPos(), 0, 'toSky')
        self.mtrack.start()

    def exitToSky(self):
        self.disableBattleDetect()
        self.mtrack.finish()
        del self.mtrack
        self.detachPropeller()

    def enterBattle(self):
        self.loop('neutral', 0)
        self.disableBattleDetect()
        self.corpMedallion.hide()
        self.healthBar.show()
        if self.currHP < self.maxHP:
            self.updateHealthBar(0, 1)

    def exitBattle(self):
        self.healthBar.hide()
        self.corpMedallion.show()
        self.currHP = self.maxHP
        self.interactivePropTrackBonus = -1

    def enterWaitForBattle(self):
        self.loop('neutral', 0)

    def exitWaitForBattle(self):
        pass

    def getLegTime(self, posA, posB):
        return (posA - posB).length() / ToontownGlobals.SuitWalkSpeed

    def getPosAtTime(self, posA, posB, time):
        fraction = time / self.getLegTime(posA, posB)
        fraction = min(max(fraction, 0.0), 1.0)

        delta = posB - posA
        pos = posA + delta * (time / self.getLegTime(posA, posB))

        return pos

    def setSkelecog(self, flag):
        SuitBase.setSkelecog(self, flag)
        if flag:
            Suit.makeSkeleton(self)

    def setWaiter(self, flag):
        SuitBase.setWaiter(self, flag)
        if flag:
            Suit.makeWaiter(self)

    def setElite(self, flag):
        SuitBase.setElite(self, flag)
        if flag:
            Suit.makeElite(self)
            nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self._name,
             'dept': self.getStyleDept(),
             'level': '%s %s' % (self.getActualLevel(), TTLocalizer.EliteCogName)}
            self.setDisplayName(nameInfo)
            self.maxHP = self.maxHP + int(round(self.maxHP * 0.25))
            self.currHP = self.maxHP

    def showHpText(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            number = int(number)
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                else:
                    self.HpTextGenerator.setText('+' + str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(0.85), self.hpText.colorInterval(0.1, Vec4(r, g, b, 0), 0.1), Func(self.hideHpText))
                seq.start()

    def showHpTextBoost(self, number, boost):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpText:
                self.hideHpText()
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            stringText = TextNode('stringText')
            stringText.setFont(OTPGlobals.getSignFont())
            if boost == 1:
                stringText.setText('Boost')
                if number <= 0:
                    if number == 0:
                        self.HpTextGenerator.setText('-%d' % number)
                    else:
                        self.HpTextGenerator.setText(str(number))
                else:
                    self.HpTextGenerator.setText('+%d' % number)
            elif boost == 2:
                stringText.setText('Resist')
                if number <= 0:
                    if number == 0:
                        self.HpTextGenerator.setText('-%d' % number)
                    else:
                        self.HpTextGenerator.setText(str(number))
                else:
                    self.HpTextGenerator.setText('+%d' % number)
            if number <= 0:
                r = 0.9
                g = 0
                b = 0
                a = 1
            else:
                r = 0
                g = 0.9
                b = 0
                a = 1
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            self.HpTextGenerator.setTextColor(r, g, b, a)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(1)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)

            stringText.clearShadow()
            stringText.setAlign(TextNode.ACenter)
            stringText.setTextColor(r, g, b, a)
            strTextNode = stringText.generate()
            self.strText = self.attachNewNode(strTextNode)
            self.strText.setScale(0.5)
            self.strText.setBillboardPointEye()
            self.strText.setBin('fixed', 100)

            self.nametag3d.setDepthTest(0)
            self.nametag3d.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.strText.setPos(0, 0, (self.height / 2) + 1.0)
            seq = Sequence(Parallel(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), self.strText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut')), Wait(0.85), Parallel(self.hpText.colorInterval(0.1, Vec4(r, g, b, 0), 0.1), self.strText.colorInterval(0.1, Vec4(r, g, b, 0), 0.1)), Func(self.hideHpText))
            seq.start()

    def showHpString(self, text, duration = 0.85, scale = 0.7):
        if self.HpTextEnabled and not self.ghostMode:
            if text != '':
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                self.HpTextGenerator.setText(text)
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                r = a = 1.0
                g = b = 0.0
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardAxis()
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(duration), self.hpText.colorInterval(0.1, Vec4(r, g, b, 0)), Func(self.hideHpText))
                seq.start()

    def hideHpText(self):
        if self.hpText:
            taskMgr.remove(self.uniqueName('hpText'))
            self.hpText.removeNode()
            self.hpText = None
        if self.strText:
            self.strText.removeNode()
            self.strText = None
        self.nametag3d.clearDepthTest()
        self.nametag3d.clearBin()
        self.sillySurgeText = False

    def getAvIdName(self):
        try:
            level = self.getActualLevel()
        except:
            level = '???'

        return '%s\n%s\nLevel %s' % (self.getName(), self.doId, level)

    def isForeman(self):
        return 0

    def isSupervisor(self):
        return 0

    def setVirtual(self, virtual):
        pass

    def getVirtual(self):
        return 0

    def isVirtual(self):
        return self.getVirtual()
