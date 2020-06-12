from panda3d.core import *
from direct.task import Task
from direct.directnotify import DirectNotifyGlobal
import os
import sys
import time
import io
class LogAndOutput:
    def __init__(self, orig, log, conBuffer):
        self.orig = orig
        self.log = log
        self.conBuffer = conBuffer
        self.display = None

    def write(self, data):
        self.orig.write(data)
        self.log.write(data)
        self.conBuffer.write(data)
        self.flush()
        #self.writeToConsole(str)
        #print("HI")

    def flush(self):
        self.orig.flush()
        self.log.flush()


class FunnyFarmLogger:
    notify = DirectNotifyGlobal.directNotify.newCategory('FunnyFarmLogger')

    def __init__(self):
        self.logPrefix = 'funnyfarm-'
        self.refreshCallback = None

        ltime = time.localtime()
        logSuffix = '%02d%02d%02d_%02d%02d%02d' % (ltime[0] - 2000, ltime[1], ltime[2],
                                                   ltime[3], ltime[4], ltime[5])

        if not os.path.exists('logs/'):
            os.mkdir('logs/')

        logfile = os.path.join('logs', self.logPrefix + logSuffix + '.log')

        log = open(logfile, 'a')
        self.consoleBuffer = io.StringIO()
        logOut = LogAndOutput(sys.__stdout__, log, self.consoleBuffer)
        logErr = LogAndOutput(sys.__stderr__, log, self.consoleBuffer)
        sys.stdout = logOut
        sys.stderr = logErr

    def refreshDisplay(self, task):
        buff = self.consoleBuffer
        buff.seek(0) #Seek us to the start of the stream or else the following code will break.
        lines = buff.readlines() # We need this to find how many lines we have without much hack 'n' sack.
        data = buff.getvalue()
        if len(lines) > 15:
            buff.truncate(0) #Resize to 0 bytes, cool.
            payload = data.partition('\n')[2]
            buff.write(payload)
        self.display.setText(buff.getvalue())
        return task.cont

    def setDisplay(self, display):
        self.display = display
