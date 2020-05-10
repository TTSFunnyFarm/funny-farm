from toontown.toon import Toon, ToonDNA, RoamingToonFSM
from toontown.toon import RoamingToonGlobals as RTG
from toontown.toonbase import FunnyFarmGlobals
import random
class RoamingToon:
    def __init__(self, navMesh, zoneId):
        if not navMesh:
            return
        navMesh = navMesh.node()
        self.navMesh = navMesh
        self.zoneId = zoneId
        self.dna = ToonDNA.ToonDNA()
        self.dna.newToonRandom(random.choice(['m', 'f']))
        self.toon = Toon.Toon()
        self.toon.setDNA(self.dna)
        self.toon.useLOD(1000)
        self.toon.startLookAround()
        self.toon.openEyes()
        self.toon.startBlink()
        #self.toon.setNameVisible(0)
        #self.toon.startBlink()
        #self.toon.startLookAround()
        self.agent = base.navMeshMgr.create_crowd_agent(str(id(self.toon)))
        spawn = random.choice(FunnyFarmGlobals.SpawnPoints[self.zoneId])
        self.agent.setPos(spawn[0])
        self.agent.setHpr(spawn[1])
        self.toon.reparentTo(self.agent)
        self.toon.setH(180)
        self.toon.setZ(-0.17)
        self.toon.initializeBodyCollisions('toon')
        self.toon.loop('neutral')
        self.navMesh.add_crowd_agent(self.agent)
        ap = self.getAgent().get_params()
        ap.set_maxAcceleration(RTG.MAX_ACCELERATION)
        ap.set_maxSpeed(RTG.MAX_SPEED)
        self.getAgent().set_params(ap)
        self.fsm = RoamingToonFSM.RoamingToonFSM(id(self.toon), self.toon)
        taskMgr.add(self.updateMe, "update-" + str(id(self.toon)))

    def updateMe(self, task):
        agent = self.getAgent()
        vel = agent.get_actual_velocity()
        vel = vel.lengthSquared()
        print(vel)
        state = self.fsm.state
        if vel > RTG.RUN_THRESHOLD:
            if state != "Running":
                self.fsm.request('Running')
        elif vel > RTG.WALK_THRESHOLD:
            if state != "Walking":
                self.fsm.request('Walking')
        elif vel < RTG.WALK_THRESHOLD:
            if state == 'Running' or state == 'Walking':
                self.fsm.request('StandingAround')
        return task.cont

    def remove(self):
        self.navMesh.remove_crowd_agent(self.agent)
        self.agent.removeNode()
        del self.agent

    def getAgent(self):
        return self.agent.node()

    def getToon(self):
        return self.toon
