from panda3d.core import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.fsm import ClassicFSM, State
from direct.showbase import Audio3DManager
from toontown.hood import ZoneUtil
from toontown.toon import NPCToons
from toontown.toon.NPCScientist import NPCScientist
from toontown.building.Interior import Interior
from toontown.building import ToonInteriorColors
from toontown.building import InteriorStorage
import random
from toontown.building import Door

class LoonyLabsInterior(Interior):

    def __init__(self, shopId, zoneId):
        Interior.__init__(self, shopId, zoneId)
        self.interiorFile = 'phase_14/models/modules/loony_labs'
        self.sillyFSM = ClassicFSM.ClassicFSM('SillyOMeter', [State.State('Setup', self.enterSetup, self.exitSetup, ['Phase1',
                'Phase2',
                'Phase3',
                'Phase4',
                'Phase4To5',
                'Phase5',
                'Flat',
                'Off']),
           State.State('Phase1', self.enterPhase1, self.exitPhase1, ['Phase2', 'Flat', 'Off']),
           State.State('Phase2', self.enterPhase2, self.exitPhase2, ['Phase3', 'Flat', 'Off']),
           State.State('Phase3', self.enterPhase3, self.exitPhase3, ['Phase4', 'Flat', 'Off']),
           State.State('Phase4', self.enterPhase4, self.exitPhase4, ['Phase4To5', 'Flat', 'Off']),
           State.State('Phase4To5', self.enterPhase4To5, self.exitPhase4To5, ['Phase5', 'Flat', 'Off']),
           State.State('Phase5', self.enterPhase5, self.exitPhase5, ['Flat', 'Off']),
           State.State('Flat', self.enterFlat, self.exitFlat, ['Off', 'Phase1']),
           State.State('Off', self.enterOff, self.exitOff, [])], 'Setup', 'Off')

    def load(self):
        # Overrides Interior.load because we don't want to start music here
        self.interior = loader.loadModel(self.interiorFile)
        self.interior.reparentTo(render)
        self.generateNPCs()

        self.interior.find('**/floor').setTransparency(1)
        self.interior.find('**/floor').setColor(1, 1, 1, 0.9)
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        doorOrigin = self.interior.find('**/door_origin')
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        self.doorRef = self.makeReflection(self.door)
        self.doorRef.setSx(-1)
        self.doorRef.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MNone))
        self.door.find('**/door_double_round_ur_trigger').setName('door_trigger_14')
        self.door.find('**/door_trigger_14').setPos(doorOrigin, 0, -0.05, 0)
        doorColor = 0
        if self.zoneId in InteriorStorage.ZoneStyles:
            doorColor = InteriorStorage.ZoneStyles[self.zoneId].get('TI_door', 0)
        self.door.setColor(self.colors['TI_door'][doorColor])
        self.doorRef.setColor(self.colors['TI_door'][doorColor])
        base.localAvatar.makeReflection()
        base.localAvatar.startUpdateReflection()
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()
        self.sillyFSM.enterInitialState()
        self.loadQuestChanges()
        self.acceptOnce('avatarExitDone', self.startActive)

    def unload(self):
        # Overrides Interior.unload because we don't want to stop music here
        self.ignoreAll()
        self.interior.removeNode()
        del self.interior
        if hasattr(self, 'npcs'):
            for npc in self.npcs:
                npc.removeActive()
                npc.delete()
                del npc
        self.unloadQuestChanges()
        base.localAvatar.stopUpdateReflection()
        base.localAvatar.deleteReflection()
        self.sillyFSM.requestFinalState()

    def generateNPCs(self):
        Interior.generateNPCs(self)
        self.npcs[0].initializeBodyCollisions('toon')
        self.npcs[1].initializeBodyCollisions('toon')
        self.npcs[2].initializeBodyCollisions('toon')
        self.npcs[0].loop('scientistJealous', fromFrame=0, toFrame=252)
        self.npcs[1].pingpong('scientistWork', fromFrame=0, toFrame=150)
        self.npcs[2].setAnimState('neutral')
        
        self.ref0 = self.makeToonReflection(self.npcs[0])
        self.ref1 = self.makeToonReflection(self.npcs[1])
        self.ref2 = self.makeToonReflection(self.npcs[2])
        self.ref0.loop('scientistJealous', fromFrame=0, toFrame=252)
        self.ref1.pingpong('scientistWork', fromFrame=0, toFrame=150)
        self.ref2.setAnimState('neutral')

        clipBoards = self.npcs[2].findAllMatches('**/ClipBoard') + self.ref2.findAllMatches('**/ClipBoard')
        for clipBoard in clipBoards:
            if not clipBoard.isEmpty():
                clipBoard.stash()

    def startActive(self):
        base.localAvatar.checkQuestCutscene()
        Interior.startActive(self)
        self.accept('enterdoor_trigger_14', self.handleLabDoorTrigger)

    def handleLabDoorTrigger(self, collEntry):
        building = collEntry.getIntoNodePath().getParent()
        door = Door.Door(building, self.shopId + '_int')
        door.avatarEnter(base.localAvatar)
        Sequence(Wait(0.4), LerpHprInterval(self.doorRef.find('**/door_double_round_ur_right'), 0.6, VBase3(100, 0, 0), blendType='easeInOut')).start()
        self.acceptOnce('avatarEnterDone', self.enterZone)

    def enterZone(self):
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()
        zone = base.cr.playGame.getActiveZone()
        zone.place.unload()
        zone.place = zone.Shop2ClassDict['toonhall']('toonhall', 1514)
        zone.place.load()
        door = Door.Door(zone.place.labDoor, 'toonhall_int')
        door.avatarExit(base.localAvatar)

    def makeReflection(self, model):
        ref = model.copyTo(model.getParent())
        p = model.getP()
        if p != 0:
            if p >= 180:
                ref.setP(p - 180)
            else:
                ref.setP(p + 180)
        else:
            ref.setR(180)
        ref.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))
        ref.setBin('default', 0)
        return ref

    def makeToonReflection(self, toon):
        ref = NPCScientist()
        ref.setDNA(toon.getDNA())
        ref.hideName()
        ref.hideShadow()
        ref.reparentTo(toon)
        ref.setR(180)
        ref.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))
        ref.setBin('default', 0)
        ref.setSx(-1)
        ref.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MNone))
        ref.setZ(-0.15)
        return ref

    def loadQuestChanges(self):
        if base.localAvatar.hasQuestHistory(1004):
            self.selectPhase(5)
        else:
            self.selectPhase(4)
        for questDesc in base.localAvatar.quests:
            if questDesc[0] == 1004:
                self.npcs[0].setPlayRate(0.2, 'scientistJealous')
                self.ref0.setPlayRate(0.2, 'scientistJealous')
                self.npcs[1].setPosHpr(-14, 15, 0, 225, 0, 0)
                for clipBoard in self.npcs[1].findAllMatches('**/ClipBoard') + self.ref1.findAllMatches('**/ClipBoard'):
                    clipBoard.stash()
                self.npcs[1].setAnimState('neutral')
                self.ref1.setAnimState('neutral')
                self.npcs[2].setHpr(270, 0, 0)
                self.flippy = NPCToons.createLocalNPC(1001)
                self.flippy.reparentTo(self.interior)
                self.flippy.setPosHpr(-12, -25, 0, 330, 0, 0)
                self.flippy.initializeBodyCollisions('toon')
                self.flippy.addActive()

    def unloadQuestChanges(self):
        if hasattr(self, 'flippy'):
            self.flippy.delete()
            del self.flippy

    def sillyMeterIsRunning(self, isRunning):
        if isRunning:
            self.sillyFSM.request('Phase1')
        else:
            self.sillyFSM.request('Flat')

    def selectPhase(self, newPhase):
        gotoPhase = 'Phase' + str(newPhase)
        if self.sillyFSM.hasStateNamed(gotoPhase) and not self.sillyFSM.getCurrentState() == self.sillyFSM.getStateNamed(gotoPhase):
            self.sillyFSM.request(gotoPhase)
        else:
            self.notify.warning('Illegal phase transition requested %s' % newPhase)

    def enterSetup(self):
        self.sillyMeter = Actor('phase_4/models/props/tt_a_ara_ttc_sillyMeter_default', {'arrowTube': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_arrowFluid',
         'phaseOne': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseOne',
         'phaseTwo': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseTwo',
         'phaseThree': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseThree',
         'phaseFour': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFour',
         'phaseFourToFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFourToFive',
         'phaseFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFive'})
        self.sillyMeter.reparentTo(self.interior)
        if config.GetBool('smooth-animations', True):
            self.sillyMeter.setBlend(frameBlend=True)
        
        # Reflection of the Silly Meter on the floor. Yes, unfortunately this means
        # we have to render everything twice and animate everything twice.
        self.sillyMeterRef = Actor('phase_4/models/props/tt_a_ara_ttc_sillyMeter_default', {'arrowTube': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_arrowFluid',
         'phaseOne': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseOne',
         'phaseTwo': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseTwo',
         'phaseThree': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseThree',
         'phaseFour': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFour',
         'phaseFourToFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFourToFive',
         'phaseFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFive'})
        self.sillyMeterRef.reparentTo(self.interior)
        if config.GetBool('smooth-animations', True):
            self.sillyMeterRef.setBlend(frameBlend=True)
        self.sillyMeterRef.setHpr(0, 0, 180)
        self.sillyMeterRef.setSx(-1)
        self.sillyMeterRef.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MNone))
        self.sillyMeterRef.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))
        self.sillyMeterRef.setBin('default', 0)

        self.flatSillyMeter = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_sillyMeterFlat')
        self.flatSillyMeter.reparentTo(self.interior)
        self.flatSillyMeter.hide()
        self.smPhase1 = self.sillyMeter.find('**/stage1')
        self.smPhase2 = self.sillyMeter.find('**/stage2')
        self.smPhase3 = self.sillyMeter.find('**/stage3')
        self.smPhase4 = self.sillyMeter.find('**/stage4')
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase4.hide()

        self.smPhase1Ref = self.sillyMeterRef.find('**/stage1')
        self.smPhase2Ref = self.sillyMeterRef.find('**/stage2')
        self.smPhase3Ref = self.sillyMeterRef.find('**/stage3')
        self.smPhase4Ref = self.sillyMeterRef.find('**/stage4')
        self.smPhase2Ref.hide()
        self.smPhase3Ref.hide()
        self.smPhase4Ref.hide()

        thermometerLocator = self.sillyMeter.findAllMatches('**/uvj_progressBar')[1]
        thermometerMesh = self.sillyMeter.find('**/tube')
        thermometerMesh.setTexProjector(thermometerMesh.findTextureStage('default'), thermometerLocator, self.sillyMeter)
        self.sillyMeter.flattenMedium()
        self.sillyMeterRef.flattenMedium()
        self.sillyMeter.makeSubpart('arrow', ['uvj_progressBar*', 'def_springA'])
        self.sillyMeter.makeSubpart('meter', ['def_pivot'], ['uvj_progressBar*', 'def_springA'])
        self.sillyMeterRef.makeSubpart('arrow', ['uvj_progressBar*', 'def_springA'])
        self.sillyMeterRef.makeSubpart('meter', ['def_pivot'], ['uvj_progressBar*', 'def_springA'])
        
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
        self.phase1Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseOne.ogg')
        self.phase1Sfx.setLoop(True)
        self.phase2Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseTwo.ogg')
        self.phase2Sfx.setLoop(True)
        self.phase3Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseThree.ogg')
        self.phase3Sfx.setLoop(True)
        self.phase4Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseFour.ogg')
        self.phase4Sfx.setLoop(True)
        self.phase4To5Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseFourToFive.ogg')
        self.phase4To5Sfx.setLoop(False)
        self.phase5Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseFive.ogg')
        self.phase5Sfx.setLoop(True)
        self.arrowSfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterArrow.ogg')
        self.arrowSfx.setLoop(False)
        self.audio3d.setDropOffFactor(0.25)
        self.accept('SillyMeterIsRunning', self.sillyMeterIsRunning)

    def exitSetup(self):
        self.ignore('SillyMeterPhase')

    def enterPhase1(self):
        self.animSeq = Sequence(Sequence(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0, startFrame=113, endFrame=124), Func(self.arrowSfx.play)), Parallel(Func(self.sillyMeter.loop, 'arrowTube', partName='arrow', fromFrame=124, toFrame=153), Sequence(Func(self.phase1Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase1Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.sillyMeter.loop('phaseOne', partName='meter')
        self.sillyMeterRef.loop('phaseOne', partName='meter')
        self.sillyMeterRef.loop('arrowTube', partName='arrow', fromFrame=124, toFrame=153)
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase1(self):
        self.animSeq.finish()
        del self.animSeq
        self.audio3d.detachSound(self.phase1Sfx)
        self.phase1Sfx.stop()
        self.sillyMeter.stop()
        self.sillyMeterRef.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase2(self):
        self.animSeq = Sequence(Sequence(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0, startFrame=195, endFrame=206), Func(self.arrowSfx.play)), Parallel(Func(self.sillyMeter.loop, 'arrowTube', partName='arrow', fromFrame=206, toFrame=235), Sequence(Func(self.phase2Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase2Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.smPhase2Ref.show()
        self.sillyMeter.loop('phaseTwo', partName='meter')
        self.sillyMeterRef.loop('phaseTwo', partName='meter')
        self.sillyMeterRef.loop('arrowTube', partName='arrow', fromFrame=206, toFrame=235)
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase2(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.smPhase2Ref.hide()
        self.audio3d.detachSound(self.phase2Sfx)
        self.phase2Sfx.stop()
        self.sillyMeter.stop()
        self.sillyMeterRef.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase3(self):
        self.animSeq = Sequence(Sequence(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0, startFrame=318, endFrame=329), Func(self.arrowSfx.play)), Parallel(Func(self.sillyMeter.loop, 'arrowTube', partName='arrow', fromFrame=329, toFrame=358), Sequence(Func(self.phase3Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase3Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.smPhase3.show()
        self.smPhase2Ref.show()
        self.smPhase3Ref.show()
        self.sillyMeter.loop('phaseThree', partName='meter')
        self.sillyMeterRef.loop('phaseThree', partName='meter')
        self.sillyMeterRef.loop('arrowTube', partName='arrow', fromFrame=329, toFrame=358)
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase3(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase2Ref.hide()
        self.smPhase3Ref.hide()
        self.audio3d.detachSound(self.phase3Sfx)
        self.phase3Sfx.stop()
        self.sillyMeter.stop()
        self.sillyMeterRef.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase4(self):
        self.animSeq = Sequence(Sequence(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0, startFrame=441, endFrame=452), Func(self.arrowSfx.play)), Parallel(Func(self.sillyMeter.loop, 'arrowTube', partName='arrow', fromFrame=452, toFrame=480), Sequence(Func(self.phase4Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase4Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.smPhase3.show()
        self.smPhase4.show()
        self.smPhase2Ref.show()
        self.smPhase3Ref.show()
        self.smPhase4Ref.show()
        self.sillyMeter.loop('phaseFour', partName='meter')
        self.sillyMeterRef.loop('phaseFour', partName='meter')
        self.sillyMeterRef.loop('arrowTube', partName='arrow', fromFrame=452, toFrame=480)
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase4(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase4.hide()
        self.smPhase2Ref.hide()
        self.smPhase3Ref.hide()
        self.smPhase4Ref.hide()
        self.audio3d.detachSound(self.phase4Sfx)
        self.phase4Sfx.stop()
        self.sillyMeter.stop()
        self.sillyMeterRef.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase4To5(self):
        self.animSeq = Sequence(Parallel(Func(self.phase4To5Sfx.play), ActorInterval(self.sillyMeter, 'phaseFourToFive', constrainedLoop=0, startFrame=1, endFrame=120), ActorInterval(self.sillyMeterRef, 'phaseFourToFive', constrainedLoop=0, startFrame=1, endFrame=120)), Parallel(Func(self.sillyMeter.loop, 'phaseFive', fromFrame=1, toFrame=48), Func(self.sillyMeterRef.loop, 'phaseFive', fromFrame=1, toFrame=48), Sequence(Func(self.phase5Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase5Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.smPhase3.show()
        self.smPhase4.show()
        self.smPhase2Ref.show()
        self.smPhase3Ref.show()
        self.smPhase4Ref.show()
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase4To5(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase4.hide()
        self.smPhase2Ref.hide()
        self.smPhase3Ref.hide()
        self.smPhase4Ref.hide()
        self.audio3d.detachSound(self.phase5Sfx)
        self.phase5Sfx.stop()
        self.sillyMeter.stop()
        self.sillyMeterRef.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase5(self):
        self.phase5Sfx.play()
        self.audio3d.attachSoundToObject(self.phase5Sfx, self.sillyMeter)
        self.smPhase2.show()
        self.smPhase3.show()
        self.smPhase4.show()
        self.smPhase2Ref.show()
        self.smPhase3Ref.show()
        self.smPhase4Ref.show()
        self.sillyMeter.loop('phaseFive')
        self.sillyMeterRef.loop('phaseFive')
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase5(self):
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase4.hide()
        self.smPhase2Ref.hide()
        self.smPhase3Ref.hide()
        self.smPhase4Ref.hide()
        self.audio3d.detachSound(self.phase5Sfx)
        self.phase5Sfx.stop()
        self.sillyMeter.stop()
        self.sillyMeterRef.stop()
        self.ignore('SillyMeterPhase')

    def enterFlat(self):
        self.sillyMeter.hide()
        self.sillyMeterRef.hide()
        self.flatSillyMeter.show()

    def exitFlat(self):
        self.sillyMeter.show()
        self.sillyMeterRef.show()
        self.flatSillyMeter.hide()

    def enterOff(self):
        if hasattr(self, 'animSeq') and self.animSeq:
            self.animSeq.finish()
        self.ignore('SillyMeterPhase')
        if hasattr(self, 'sillyMeter'):
            del self.sillyMeter
        if hasattr(self, 'smPhase1'):
            del self.smPhase1
        if hasattr(self, 'smPhase2'):
            del self.smPhase2
        if hasattr(self, 'smPhase3'):
            del self.smPhase3
        if hasattr(self, 'smPhase4'):
            del self.smPhase4
        if hasattr(self, 'sillyMeterRef'):
            del self.sillyMeterRef
        if hasattr(self, 'smPhase1Ref'):
            del self.smPhase1Ref
        if hasattr(self, 'smPhase2Ref'):
            del self.smPhase2Ref
        if hasattr(self, 'smPhase3Ref'):
            del self.smPhase3Ref
        if hasattr(self, 'smPhase4Ref'):
            del self.smPhase4Ref
        self.cleanUpSounds()

    def exitOff(self):
        pass

    def cleanUpSounds(self):

        def __cleanUpSound__(soundFile):
            if soundFile.status() == soundFile.PLAYING:
                soundFile.setLoop(False)
                soundFile.stop()

        if hasattr(self, 'audio3d'):
            self.audio3d.disable()
            del self.audio3d
        if hasattr(self, 'phase1Sfx'):
            __cleanUpSound__(self.phase1Sfx)
            del self.phase1Sfx
        if hasattr(self, 'phase2Sfx'):
            __cleanUpSound__(self.phase2Sfx)
            del self.phase2Sfx
        if hasattr(self, 'phase3Sfx'):
            __cleanUpSound__(self.phase3Sfx)
            del self.phase3Sfx
        if hasattr(self, 'phase4Sfx'):
            __cleanUpSound__(self.phase4Sfx)
            del self.phase4Sfx
        if hasattr(self, 'phase4To5Sfx'):
            __cleanUpSound__(self.phase4To5Sfx)
            del self.phase4To5Sfx
        if hasattr(self, 'phase5Sfx'):
            __cleanUpSound__(self.phase5Sfx)
            del self.phase5Sfx
        if hasattr(self, 'arrowSfx'):
            __cleanUpSound__(self.arrowSfx)
            del self.arrowSfx
