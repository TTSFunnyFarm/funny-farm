from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from toontown.leveleditor.DNAParser import DNAParser
#from libtoontown import *
import os
parser = DNAParser()
parser.parse_file()
loadPrcFile("config/level_editor.prc")
base = ShowBase()
base.run()
