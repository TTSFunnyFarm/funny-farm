from panda3d.core import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleBldg import BattleBldg
from toontown.building.ElevatorConstants import *
from toontown.building.ElevatorUtils import *
from toontown.building.Elevator import Elevator
from toontown.building.SuitInteriorBase import SuitInteriorBase
from toontown.building.SuitPlannerInterior import SuitPlannerInterior

class SuitInterior(SuitInteriorBase):

    def __init__(self, zoneId, track, difficulty, numFloors):
        SuitInteriorBase.__init__(self, zoneId, track)
        self.difficulty = difficulty
        self.numFloors = numFloors
        self.toons = [base.localAvatar]
        self.suits = []
        self.activeSuits = []
        self.reserveSuits = []
        self.joiningReserves = []
        self.BottomFloor_SuitPositions = [Point3(0, 15, 0),
         Point3(10, 20, 0),
         Point3(-7, 24, 0),
         Point3(-10, 0, 0)]
        self.BottomFloor_SuitHs = [75,
         170,
         -91,
         -44]
        self.Cubicle_SuitPositions = [Point3(0, 18, 0),
         Point3(10, 12, 0),
         Point3(-9, 11, 0),
         Point3(-3, 13, 0)]
        self.Cubicle_SuitHs = [170,
         56,
         -52,
         10]
        self.BossOffice_SuitPositions = [Point3(0, 15, 0),
         Point3(10, 20, 0),
         Point3(-10, 6, 0),
         Point3(-17, 34, 11)]
        self.BossOffice_SuitHs = [170,
         120,
         12,
         38]
        self.floorModelA = 'phase_7/models/modules/suit_interior'
        self.floorModelB = 'phase_7/models/modules/cubicle_room'
        self.floorModelC = 'phase_7/models/modules/boss_suit_office'
        self.elevatorFilename = 'phase_4/models/modules/elevator'
        self.entranceElevator = Elevator(ELEVATOR_NORMAL)
        self.exitElevator = Elevator(ELEVATOR_NORMAL)
        self.battleMusic = base.loader.loadMusic('phase_7/audio/bgm/encntr_general_bg_indoor.ogg')
        self.bossMusic = base.loader.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.ogg')
        self.waitMusic = base.loader.loadMusic('phase_7/audio/bgm/encntr_toon_winning_indoor.ogg')
        self.planner = SuitPlannerInterior(self.numFloors, self.difficulty, self.track)
        self.townBattle = base.cr.playGame.street.townBattle
        self.battle = None
        self.toonSkillPtsGained = {}
        self.toonExp = {}
        self.toonOrigQuests = {}
        self.toonItems = {}
        self.toonOrigMerits = {}
        self.toonMerits = {}
        self.toonParts = {}
        self.suitsKilled = []
        self.helpfulToons = []

    def enter(self):
        SuitInteriorBase.enter(self)

    def enterFloor(self):
        SuitInteriorBase.enterFloor(self)
        self.enterBattle()

    def loadNextFloor(self):
        self.exitResting()
        if self.floor:
            self.unloadFloor()
        self.currentFloor += 1
        if self.currentFloor == 1:
            self.loadFloor(self.floorModelA)
            SuitHs = self.BottomFloor_SuitHs
            SuitPositions = self.BottomFloor_SuitPositions
        elif self.currentFloor < self.numFloors:
            self.loadFloor(self.floorModelB)
            SuitHs = self.Cubicle_SuitHs
            SuitPositions = self.Cubicle_SuitPositions
        elif self.currentFloor == self.numFloors:
            self.loadFloor(self.floorModelC)
            SuitHs = self.BossOffice_SuitHs
            SuitPositions = self.BossOffice_SuitPositions
        self.entranceElevator.setup(self.elevatorModel.copyTo(hidden), self.floor.find('**/elevator-in'), self.track, self.difficulty, self.numFloors)
        self.exitElevator.setup(self.elevatorModel.copyTo(hidden), self.floor.find('**/elevator-out'), self.track, self.difficulty, self.numFloors)
        self.entranceElevator.forceCloseDoors()
        self.exitElevator.forceCloseDoors()

        suitHandles = self.planner.genFloorSuits(self.currentFloor - 1)
        self.suits = suitHandles['activeSuits']
        self.activeSuits = []
        for suit in self.suits:
            self.activeSuits.append(suit)
        self.reserveSuits = suitHandles['reserveSuits']

        for index in range(len(self.suits)):
            self.suits[index].reparentTo(render)
            self.suits[index].setPos(SuitPositions[index])
            if len(self.suits) > 2:
                self.suits[index].setH(SuitHs[index])
            else:
                self.suits[index].setH(170)
            self.suits[index].loop('neutral')

        self.playElevator()

    def unload(self):
        SuitInteriorBase.unload(self)
        del self.battleMusic
        del self.bossMusic
        del self.waitMusic
        del self.planner
        del self.toons
        del self.suits
        del self.activeSuits
        del self.reserveSuits
        del self.joiningReserves
        del self.BottomFloor_SuitPositions
        del self.BottomFloor_SuitHs
        del self.Cubicle_SuitPositions
        del self.Cubicle_SuitHs
        del self.BossOffice_SuitPositions
        del self.BossOffice_SuitHs
        del self.battle
        del self.toonSkillPtsGained
        del self.toonExp
        del self.toonOrigQuests
        del self.toonItems
        del self.toonOrigMerits
        del self.toonMerits
        del self.toonParts
        del self.suitsKilled
        del self.helpfulToons

    def enterBattle(self):
        base.localAvatar.disable()
        base.localAvatar.experienceBar.hide()
        self.battle = BattleBldg(self, self.townBattle, toons=self.toons, suits=self.suits)
        self.battle.reparentTo(render)
        self.battle.suitsKilled = self.suitsKilled
        self.battle.battleCalc.toonSkillPtsGained = self.toonSkillPtsGained
        self.battle.toonExp = self.toonExp
        self.battle.toonOrigQuests = self.toonOrigQuests
        self.battle.toonItems = self.toonItems
        self.battle.toonOrigMerits = self.toonOrigMerits
        self.battle.toonMerits = self.toonMerits
        self.battle.toonParts = self.toonParts
        self.battle.helpfulToons = self.helpfulToons
        if self.currentFloor == self.numFloors:
            self.battle.setBossBattle(1)
            music = self.bossMusic
        else:
            self.battle.setBossBattle(0)
            music = self.battleMusic
        self.battle.enter(creditMultiplier=2.0)
        base.playMusic(music, looping=1, volume=0.9)
        self.accept(self.townBattle.doneEvent, self.exitBattle)

    def exitBattle(self, doneStatus):
        self.ignore(self.townBattle.doneEvent)
        self.battleMusic.stop()
        self.battle.cleanupBattle()
        self.battle.delete()
        self.battle = None
        base.localAvatar.experienceBar.show()
        if doneStatus == 'victory':
            base.localAvatar.setAnimState('neutral')
            base.cr.playGame.street.exitPlace()
            base.cr.playGame.street.enter()
            zoneId = base.cr.playGame.street.zoneId
            building = None
            for tb in base.cr.playGame.getActiveZone().buildings:
                if self.block == tb.getBlock():
                    building = tb
                    break
            if building:
                building.victor = base.localAvatar.getDoId()
                building.enterWaitForVictors()
                taskMgr.doMethodLater(1.0, self.handleInsideElevator, 'handleInsideElevator')
        elif doneStatus == 'defeat':
            base.localAvatar.died()
        else:
            base.localAvatar.enable()
            self.enterResting()

    def handleInsideElevator(self, task):
        messenger.send('insideVictorElevator')
        return task.done

    def enterResting(self):
        base.playMusic(self.waitMusic, looping=1, volume=0.7)
        self.entranceElevator.closeDoors()
        self.exitElevator.openDoors()
        self.exitElevator.addActive()

    def exitResting(self):
        self.waitMusic.stop()

    def handleRoundDone(self, totalHp, totalMaxHp, deadSuits):
        for suit in deadSuits:
            self.activeSuits.remove(suit)

        if len(self.reserveSuits) > 0 and len(self.activeSuits) < 2:
            self.joiningReserves = []
            hpPercent = 100 - float(totalHp) / float(totalMaxHp) * 100.0
            for info in self.reserveSuits:
                if info[1] <= hpPercent and len(self.activeSuits) < 2:
                    self.suits.append(info[0])
                    self.activeSuits.append(info[0])
                    self.joiningReserves.append(info)

            for info in self.joiningReserves:
                self.reserveSuits.remove(info)
                if info[0] in self.battle.suits:
                    self.battle.suits.remove(info[0])
            self.battle.setMembers(*self.battle.getMembers())

            if len(self.joiningReserves) > 0:
                self.enterReservesJoining()
                return
        self.battle.startCamTrack()

    def __playReservesJoining(self):
        index = 0
        for info in self.joiningReserves:
            suit = info[0]
            suit.reparentTo(render)
            suit.setPos(self.exitElevator.np, Point3(ElevatorPoints[index + 1][0], ElevatorPoints[index + 1][1], ElevatorPoints[index + 1][2]))
            suit.setH(180)
            suit.enterBattle()
            suit.battleTrap = NO_TRAP
            index += 1

        track = Sequence(Func(camera.wrtReparentTo, self.exitElevator.np), Func(camera.setPos, Point3(0, -8, 2)), Func(camera.setHpr, Vec3(0, 10, 0)), Func(self.exitElevator.openDoors), Wait(ElevatorData[ELEVATOR_NORMAL]['openTime']), Wait(SUIT_HOLD_ELEVATOR_TIME), Func(camera.wrtReparentTo, render))
        track.start()

    def __playCloseElevatorOut(self):
        track = Sequence(Wait(SUIT_LEAVE_ELEVATOR_TIME), Func(self.exitElevator.closeDoors))
        track.start()

    def enterReservesJoining(self):
        self.__playReservesJoining()
        taskMgr.doMethodLater(ElevatorData[ELEVATOR_NORMAL]['openTime'] + SUIT_HOLD_ELEVATOR_TIME, self.exitReservesJoining, 'reservesJoining')
        return None

    def exitReservesJoining(self, task):
        for info in self.joiningReserves:
            self.battle.suitRequestJoin(info[0])
        self.__playCloseElevatorOut()
        if len(self.battle.activeSuits) == 0:
            camera.setPos(self.battle, 0, -15, 6)
            self.acceptOnce('battle-%d-adjustDone' % self.battle.doId, self.battle.startCamTrack)
            camera.headsUp(self.exitElevator.np)
        else:
            self.battle.startCamTrack()
        self.joiningReserves = []
        return task.done
