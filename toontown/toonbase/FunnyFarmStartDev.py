from panda3d.core import *

if __debug__:
    loadPrcFile('config/general.prc')
else:
    loadPrcFile('config/release.prc')

from toontown.toonbase import FunnyFarmStart
