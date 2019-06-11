import time

class CheesyEffectMgrAI:
    notify = directNotify.newCategory('CheesyEffectMgrAI')

    def __init__(self):
        self.duration = None
        self.startTime = None

    def startTimer(self, unit, duration, startTime):
        if unit == 'm':
            duration = duration * 60
        elif unit == 'h':
            duration = duration * 60 * 60
        elif unit == 'd':
            duration = duration * 24 * 60 * 60
        else:
            self.notify.error("startTimer: Invalid unit of time given. Must be 'm', 'h', or 'd'.")
        self.duration = duration
        self.startTime = startTime
        taskMgr.doMethodLater(0.1, self.__checkTime, 'cheesyEffectTimer')

    def __checkTime(self, task):
        if taskMgr.hasTaskNamed('cheesyEffectTimer'):
            taskMgr.remove('cheesyEffectTimer')
        now = time.time()
        timeElapsed = now - self.startTime
        if timeElapsed >= self.duration:
            messenger.send('cheesyEffectTimeout')
            self.stopTimer()
        else:
            timeLeft = self.duration - timeElapsed
            taskMgr.doMethodLater(timeLeft, self.__checkTime, 'cheesyEffectTimer')

    def stopTimer(self):
        if taskMgr.hasTaskNamed('cheesyEffectTimer'):
            taskMgr.remove('cheesyEffectTimer')
        self.duration = None
        self.startTime = None
