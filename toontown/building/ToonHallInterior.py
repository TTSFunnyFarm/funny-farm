from panda3d.core import *
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from direct.fsm import ClassicFSM, State
from direct.showbase import Audio3DManager
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import FunnyFarmGlobals
from toontown.toon import NPCToons
from Interior import Interior
import ToonInteriorColors
import random
import Door

class ToonHallInterior(Interior):

    def __init__(self, zoneId):
        Interior.__init__(self)
        self.zoneId = zoneId
        self.interiorFile = 'phase_3.5/models/modules/tt_m_ara_int_toonhall'
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
        Interior.load(self)
        self.interior.find('**/mainhall').setBin('ground', 0)
        self.interior.find('**/hallway').setBin('ground', 0)
        self.interior.find('**/office').setBin('ground', 0)
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.colors = ToonInteriorColors.colors[self.zoneId]
        self.interior.find('**/door_origin').setScale(0.8, 0.8, 0.8)
        self.door = self.setupDoor('door_double_round_ur', 'door_origin')
        doorColor = self.colors['TI_door'][1]
        self.door.setColor(doorColor)
        self.fixDoor(self.door)
        self.generateNPCs()
        self.acceptOnce('avatarExitDone', self.startActive)
        del self.colors
        del self.randomGenerator
        self.interior.flattenMedium()
        self.sillyFSM.enterInitialState()

    def unload(self):
        self.sillyFSM.requestFinalState()
        for npc in self.npcs:
            npc.removeActive()
            npc.delete()
            del npc
        Interior.unload(self)

    def generateNPCs(self):
        flippy = NPCToons.createLocalNPC(2001)
        dimm = NPCToons.createLocalNPC(2018)
        surlee = NPCToons.createLocalNPC(2019)
        prepostera = NPCToons.createLocalNPC(2020)
        origins = [
                self.interior.find('**/npc_origin_0'),
                self.interior.find('**/npc_origin_1'),
                self.interior.find('**/npc_origin_2'),
                self.interior.find('**/npc_origin_3')
        ]
        key = 0
        self.npcs = [flippy, dimm, surlee, prepostera]
        for npc in self.npcs:
            key += 1
            pos = origins[key - 1].getPos()
            hpr = origins[key - 1].getHpr()
            npc.reparentTo(render)
            npc.setPosHpr(pos, hpr)
            npc.addActive()
        flippy.useLOD(1000)
        dimm.initPos()
        surlee.initPos()
        prepostera.initPos()
        dimm.setAnimState('ScientistJealous')
        surlee.setAnimState('ScientistJealous')
        prepostera.setAnimState('ScientistEmcee')

    def startActive(self):
        self.acceptOnce('enterdoor_double_round_ur_trigger', self.__handleDoor)

    def __handleDoor(self, entry):
        door = Door.Door(self.door, 'th_int', self.zoneId)
        door.avatarEnter(base.localAvatar)
        self.acceptOnce('avatarEnterDone', self.__handleEnterFF)

    def __handleEnterFF(self):
        base.cr.playGame.exitPlace()
        base.cr.playGame.enterFFHood(shop='th')

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
        ropes = loader.loadModel('phase_4/models/modules/tt_m_ara_int_ropes')
        ropes.reparentTo(self.interior)
        self.sillyMeter = Actor.Actor('phase_4/models/props/tt_a_ara_ttc_sillyMeter_default', {'arrowTube': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_arrowFluid',
         'phaseOne': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseOne',
         'phaseTwo': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseTwo',
         'phaseThree': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseThree',
         'phaseFour': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFour',
         'phaseFourToFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFourToFive',
         'phaseFive': 'phase_4/models/props/tt_a_ara_ttc_sillyMeter_phaseFive'})
        self.sillyMeter.reparentTo(self.interior)
        self.sillyMeter.setBlend(frameBlend=True)
        self.flatSillyMeter = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_sillyMeterFlat')
        self.flatSillyMeter.reparentTo(self.interior)
        self.flatSillyMeter.hide()
        self.flatDuck = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_scientistDuckFlat')
        loc1 = self.interior.find('**/npc_origin_1')
        if loc1:
            self.flatDuck.reparentTo(loc1)
        self.flatDuck.hide()
        self.flatMonkey = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_scientistMonkeyFlat')
        loc1 = self.interior.find('**/npc_origin_2')
        if loc1:
            self.flatMonkey.reparentTo(loc1)
        self.flatMonkey.hide()
        self.flatHorse = loader.loadModel('phase_3.5/models/modules/tt_m_ara_int_scientistHorseFlat')
        loc1 = self.interior.find('**/npc_origin_3')
        if loc1:
            self.flatHorse.reparentTo(loc1)
        self.flatHorse.hide()
        self.smPhase1 = self.sillyMeter.find('**/stage1')
        self.smPhase2 = self.sillyMeter.find('**/stage2')
        self.smPhase3 = self.sillyMeter.find('**/stage3')
        self.smPhase4 = self.sillyMeter.find('**/stage4')
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase4.hide()
        thermometerLocator = self.sillyMeter.findAllMatches('**/uvj_progressBar')[1]
        thermometerMesh = self.sillyMeter.find('**/tube')
        thermometerMesh.setTexProjector(thermometerMesh.findTextureStage('default'), thermometerLocator, self.sillyMeter)
        self.sillyMeter.flattenMedium()
        self.sillyMeter.makeSubpart('arrow', ['uvj_progressBar*', 'def_springA'])
        self.sillyMeter.makeSubpart('meter', ['def_pivot'], ['uvj_progressBar*', 'def_springA'])
        self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
        self.phase1Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseOne.ogg')
        self.phase1Sfx.setLoop(True)
        self.phase2Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseTwo.ogg')
        self.phase2Sfx.setLoop(True)
        self.phase3Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseThree.ogg')
        self.phase3Sfx.setLoop(True)
        self.phase3Sfx.setVolume(0.5)
        self.phase4Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseFour.ogg')
        self.phase4Sfx.setLoop(True)
        self.phase4To5Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseFourToFive.ogg')
        self.phase4To5Sfx.setLoop(False)
        self.phase5Sfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseFive.ogg')
        self.phase5Sfx.setLoop(True)
        self.arrowSfx = self.audio3d.loadSfx('phase_4/audio/sfx/tt_s_prp_sillyMeterArrow.ogg')
        self.arrowSfx.setLoop(False)
        self.audio3d.setDropOffFactor(0.05)
        self.accept('SillyMeterPhase', self.selectPhase)
        self.accept('SillyMeterIsRunning', self.sillyMeterIsRunning)
        self.selectPhase(3)

    def exitSetup(self):
        self.ignore('SillyMeterPhase')

    def enterPhase1(self):
        self.animSeq = Sequence(Sequence(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0, startFrame=113, endFrame=124), Func(self.arrowSfx.play)), Parallel(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1, startFrame=124, endFrame=153), Sequence(Func(self.phase1Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase1Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.sillyMeter.loop('phaseOne', partName='meter')
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase1(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.audio3d.detachSound(self.phase1Sfx)
        self.phase1Sfx.stop()
        self.sillyMeter.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase2(self):
        self.animSeq = Sequence(Sequence(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0, startFrame=195, endFrame=206), Func(self.arrowSfx.play)), Parallel(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1, startFrame=206, endFrame=235), Sequence(Func(self.phase2Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase2Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.sillyMeter.loop('phaseTwo', partName='meter')
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase2(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.audio3d.detachSound(self.phase2Sfx)
        self.phase2Sfx.stop()
        self.sillyMeter.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase3(self):
        self.animSeq = Sequence(Sequence(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0, startFrame=318, endFrame=329), Func(self.arrowSfx.play)), Parallel(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1, startFrame=329, endFrame=358), Sequence(Func(self.phase3Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase3Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.smPhase3.show()
        self.sillyMeter.loop('phaseThree', partName='meter')
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase3(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.audio3d.detachSound(self.phase3Sfx)
        self.phase3Sfx.stop()
        self.sillyMeter.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase4(self):
        self.animSeq = Sequence(Sequence(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=0, startFrame=441, endFrame=452), Func(self.arrowSfx.play)), Parallel(ActorInterval(self.sillyMeter, 'arrowTube', partName='arrow', constrainedLoop=1, startFrame=452, endFrame=481), Sequence(Func(self.phase4Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase4Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.smPhase3.show()
        self.smPhase4.show()
        self.sillyMeter.loop('phaseFour', partName='meter')
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase4(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase4.hide()
        self.audio3d.detachSound(self.phase4Sfx)
        self.phase4Sfx.stop()
        self.sillyMeter.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase4To5(self):
        self.animSeq = Sequence(Parallel(Func(self.phase4To5Sfx.play), ActorInterval(self.sillyMeter, 'phaseFourToFive', constrainedLoop=0, startFrame=1, endFrame=120)), Parallel(ActorInterval(self.sillyMeter, 'phaseFive', constrainedLoop=1, startFrame=1, endFrame=48), Sequence(Func(self.phase5Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase5Sfx, self.sillyMeter))))
        self.animSeq.start()
        self.smPhase2.show()
        self.smPhase3.show()
        self.smPhase4.show()
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase4To5(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase4.hide()
        self.audio3d.detachSound(self.phase5Sfx)
        self.phase5Sfx.stop()
        self.sillyMeter.stop()
        self.ignore('SillyMeterPhase')

    def enterPhase5(self):
        self.animSeq = Parallel(ActorInterval(self.sillyMeter, 'phaseFive', constrainedLoop=1, startFrame=1, endFrame=48), Sequence(Func(self.phase5Sfx.play), Func(self.audio3d.attachSoundToObject, self.phase5Sfx, self.sillyMeter)))
        self.animSeq.start()
        self.smPhase2.show()
        self.smPhase3.show()
        self.smPhase4.show()
        self.accept('SillyMeterPhase', self.selectPhase)

    def exitPhase5(self):
        self.animSeq.finish()
        del self.animSeq
        self.smPhase2.hide()
        self.smPhase3.hide()
        self.smPhase4.hide()
        self.audio3d.detachSound(self.phase5Sfx)
        self.phase5Sfx.stop()
        self.sillyMeter.stop()
        self.ignore('SillyMeterPhase')

    def enterFlat(self):
        self.sillyMeter.hide()
        self.flatSillyMeter.show()
        self.flatDuck.show()
        self.flatMonkey.show()
        self.flatHorse.show()

    def exitFlat(self):
        self.sillyMeter.show()
        self.flatSillyMeter.hide()
        self.flatDuck.hide()
        self.flatMonkey.hide()
        self.flatHorse.hide()

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
