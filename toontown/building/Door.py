from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownGlobals

class Door(DirectObject):
    notify = directNotify.newCategory('Door')

    def __init__(self, door, code):
        self.door = door
        self.code = code
        self.openSfx = base.loader.loadSfx('phase_3.5/audio/sfx/Door_Open_1.ogg')
        self.closeSfx = base.loader.loadSfx('phase_3.5/audio/sfx/Door_Close_1.ogg')
        self.doorX = 1.5
        self.doorTrack = None
        self.doorExitTrack = None
        if 'int' in self.code:
            self.rightDoor = self.door.find('**/' + self.door.getName() + '_right')
            self.leftDoor = self.door.find('**/' + self.door.getName() + '_left')
        else:
            self.rightDoor = self.door.find('**/rightDoor*')
            self.leftDoor = self.door.find('**/leftDoor*')
        self.rightSwing = True
        self.leftSwing = True

    def uniqueName(self, idString):
        return ('%s-%s' % (idString, str(id(self))))

    def getDoorNodePath(self):
        if 'int' in self.code:
            otherNP = self.door.getParent()
        elif self.code == 'door_0':
            building = base.cr.playGame.getActiveZone().geom.find('**/*toon_landmark_hq*')
            otherNP = building.find('**/door_origin_0')
        elif self.code == 'door_1':
            building = base.cr.playGame.getActiveZone().geom.find('**/*toon_landmark_hq*')
            otherNP = building.find('**/door_origin_1')
        else:
            building = self.door
            otherNP = building.find('**/*door_origin*')
        return otherNP

    def avatarEnter(self, avatar):
        base.localAvatar.disable()
        track = Sequence()
        enqueueTrack = self.getAvatarEnqueueTrack(avatar, 0.5)
        enterTrack = self.getAvatarEnterDoorTrack(avatar, 1.0)
        track.append(Func(self.enterOpening))
        track.append(enqueueTrack)
        track.append(Wait(0.4))
        track.append(enterTrack)
        track.append(Func(self.enterClosing))
        track.start()

    def avatarExit(self, avatar):
        track = Sequence()
        exitTrack = self.getAvatarExitTrack(avatar, 0.7)
        track.append(Func(self.exitDoorEnterOpening))
        track.append(exitTrack)
        track.append(Func(self.exitDoorEnterClosing))
        track.start()

    def exitDone(self):
        base.localAvatar.enable()
        if self.code == 'toonhall_int' or self.code == 'loonylabs_int':
            base.camLens.setMinFov(ToontownGlobals.CogHQCameraFov/(4./3.))
            base.localAvatar.fov = ToontownGlobals.CogHQCameraFov
        else:
            base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov/(4./3.))
            base.localAvatar.fov = ToontownGlobals.DefaultCameraFov

    def getAvatarEnqueueTrack(self, avatar, duration):
        back = -5.0
        if back < -9.0:
            back = -9.0
        offset = Point3(self.doorX, back, ToontownGlobals.FloorOffset)
        otherNP = self.getDoorNodePath()
        walkLike = ActorInterval(avatar, 'walk', startTime = 1, duration = duration, endTime = 0.0001)
        standHere = Sequence(LerpPosHprInterval(nodePath = avatar, other = otherNP, duration = duration, pos = offset, hpr = VBase3(0, 0, 0), blendType = 'easeInOut'), Func(avatar.setAnimState, 'neutral'))
        trackName = self.uniqueName('avatarEnqueueDoor')
        track = Parallel(walkLike, standHere, name = trackName)
        return track

    def getAvatarEnterDoorTrack(self, avatar, duration):
        trackName = self.uniqueName('avatarEnterDoor')
        track = Parallel(name = trackName)
        otherNP = self.getDoorNodePath()
        track.append(LerpPosHprInterval(nodePath = camera, other = avatar, duration = duration, pos = Point3(0, -8, avatar.getHeight()), hpr = VBase3(0, 0, 0), blendType = 'easeInOut'))
        finalPos = avatar.getParent().getRelativePoint(otherNP, Point3(self.doorX, 2, ToontownGlobals.FloorOffset))
        moveHere = Sequence(Func(avatar.setAnimState, 'walk'), LerpPosInterval(nodePath = avatar, duration = duration, pos = finalPos, blendType = 'easeIn'))
        track.append(moveHere)
        track.append(Sequence(Wait(duration * 0.5), Func(base.transitions.irisOut, duration * 0.5), Wait(duration * 0.5)))
        return track

    def getAvatarExitTrack(self, avatar, duration):
        otherNP = self.getDoorNodePath()
        trackName = self.uniqueName('avatarExitDoor')
        track = Sequence(name=trackName)
        track.append(Func(avatar.setAnimState, 'walk'))
        track.append(
                PosHprInterval(
                        avatar, Point3(-self.doorX, 0, ToontownGlobals.FloorOffset),
                        VBase3(179, 0, 0), other=otherNP
                )
        )
        track.append(
                PosHprInterval(
                        camera, VBase3(-self.doorX, 5, avatar.getHeight()),
                        VBase3(180, 0, 0), other=otherNP
                )
        )
        finalPos = render.getRelativePoint(
                otherNP, Point3(-self.doorX, -6, ToontownGlobals.FloorOffset)
        )
        track.append(
                LerpPosInterval(
                        nodePath=avatar, duration=duration, pos=finalPos,
                        blendType='easeInOut'
                )
        )
        track.append(Func(self.exitDone))
        track.append(Func(base.transitions.irisIn))
        return track

    def enterOpening(self):
        otherNP = self.getDoorNodePath()
        trackName = self.uniqueName('doorOpen')
        if self.rightSwing:
            h = 100
        else:
            h = -100
        self.finishDoorTrack()
        self.doorTrack = Parallel(SoundInterval(self.openSfx, node=self.rightDoor), Sequence(HprInterval(self.rightDoor, VBase3(0, 0, 0), other=otherNP), Wait(0.4), LerpHprInterval(nodePath=self.rightDoor, duration=0.6, hpr=VBase3(h, 0, 0), startHpr=VBase3(0, 0, 0), other=otherNP, blendType='easeInOut')), name=trackName)
        self.doorTrack.start()

    def enterClosing(self):
        otherNP = self.getDoorNodePath()
        trackName = self.uniqueName('doorClose')
        if self.rightSwing:
            h = 100
        else:
            h = -100
        self.finishDoorTrack()
        self.doorTrack = Sequence(LerpHprInterval(nodePath = self.rightDoor, duration = 1.0, hpr = VBase3(0, 0, 0), startHpr = VBase3(h, 0, 0), other = otherNP, blendType = 'easeInOut'), SoundInterval(self.closeSfx, node = self.rightDoor), Func(messenger.send, 'avatarEnterDone'), name = trackName)
        self.doorTrack.start()

    def exitDoorEnterOpening(self):
        if self.leftSwing:
            h = -100
        else:
            h = 100
        if not self.leftDoor.isEmpty():
            otherNP = self.getDoorNodePath()
            trackName = self.uniqueName('doorDoorExitTrack')
            self.finishDoorExitTrack()
            self.doorExitTrack = Parallel(SoundInterval(self.openSfx, node = self.leftDoor), LerpHprInterval(nodePath = self.leftDoor, duration = 0.59999999999999998, hpr = VBase3(h, 0, 0), startHpr = VBase3(0, 0, 0), other = otherNP, blendType = 'easeInOut'), name = trackName)
            self.doorExitTrack.start()
        else:
            self.notify.warning('exitDoorEnterOpening(): did not find leftDoor')

    def exitDoorEnterClosing(self):
        if self.leftSwing:
            h = -100
        else:
            h = 100
        if not self.leftDoor.isEmpty():
            otherNP = self.getDoorNodePath()
            trackName = self.uniqueName('doorExitTrack')
            self.finishDoorExitTrack()
            self.doorExitTrack = Sequence(LerpHprInterval(nodePath = self.leftDoor, duration = 1.0, hpr = VBase3(0, 0, 0), startHpr = VBase3(h, 0, 0), other = otherNP, blendType = 'easeInOut'), SoundInterval(self.closeSfx, node = self.leftDoor), Func(messenger.send, 'avatarExitDone'), name = trackName)
            self.doorExitTrack.start()
        else:
            self.notify.warning('exitDoorEnterClosing(): did not find leftDoor')

    def finishDoorTrack(self):
        if self.doorTrack:
            self.doorTrack.finish()
        self.doorTrack = None

    def finishDoorExitTrack(self):
        if self.doorExitTrack:
            self.doorExitTrack.finish()
        self.doorExitTrack = None

    def finishAllTracks(self):
        self.finishDoorTrack()
        self.finishDoorExitTrack()
