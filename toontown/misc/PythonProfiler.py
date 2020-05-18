# Author: mfwass - https://github.com/mfwass/
# Date: 11/6/2019
# Filename: PythonProfiler.py

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
import cProfile
import time
import pstats
import io

class PythonProfiler(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('PythonProfiler')
    notify.setInfo(1)

    def __init__(self):
        DirectObject.__init__(self)
        self.active = False
        self.profiler = None
        self.startTime = None

    def startProfiling(self, sort, duration=None):
        self.sortby = sort
        self.notify.info("Started profiling with method: {}".format(sort))
        if self.active:
            self.notify.warning('Attempted to profile client while already profiling the client!')
            return

        self.profiler = cProfile.Profile()
        self.profiler.enable()

        self.active = True
        self.startTime = time.time()

        if not duration:
            self.accept("stopProfiling", self.stopProfiling)
            self.notify.warning('Started profiling without set duration! Listening for stopProfiling message.')
        else:
            base.taskMgr.doMethodLater(duration, self.stopProfiling, 'profiler-task')

    def stopProfiling(self, task=None):
        if not self.active:
            self.notify.warning('Attempted to stop profiling process when not profiling the process!')
            return

        self.profiler.disable()
        self.active = False

        outstream = io.StringIO()

        #######################
        # Options for sortby: #
        #######################
        #    calls            #
        #    cumulative       #
        #    cumtime          #
        #    file             #
        #    filename         #
        #    module           #
        #    ncalls           #
        #    pcalls           #
        #    line             #
        #    name             #
        #    nfl              #
        #    stdname          #
        #    time             #
        #    tottime          #
        #######################

        result = pstats.Stats(self.profiler, stream=outstream).sort_stats(self.sortby)
        result.print_stats()

        f = open("results/%s_profile_results_%s.txt" % (game.process, int(time.time())), 'w')
        f.write('\n')
        f.write(outstream.getvalue())
        f.write('\n\n')
        f.close()

        if task:
            return task.done

    def getTimeProfiled(self):
        if self.active:
            return time.time() - self.startTime
        else:
            return 0
