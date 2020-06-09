# Decompresses the FFTW compressed animations and saved out the uncompressed
# versions to disk. (We don't need them to be compressed anymore, and FFTW
# is deprecated in Panda.)

from panda3d.core import *

import os
import sys
import glob
import math
#phases = [3, 3.5, 4, 5, 5.5, 6, 7, 8, 9, 10, 11, 12, 13]
phases = [14]
orig_models = []
for phase in phases:
    orig_models += glob.glob("phase_{0}\\models\\**\\*.bam".format(phase))

def is_animation(node):
    return not node.find("**/+AnimBundleNode").is_empty()

def process_model(filename):
    print("Processing %s" % (filename.get_fullpath()))
    loader = Loader.get_global_ptr()
    try:
        mdlnp = NodePath(loader.load_sync(filename))
    except:
        return
    if not is_animation(mdlnp):
        # Not an animation, skip.
        print("Not an animation.")
        return

    out_filename = Filename("uncompressed_anims/" + filename.get_fullpath())
    os_out = Filename(Filename.to_os_specific(Filename(out_filename.get_dirname())))
    print(os_out)
    if (not os.path.exists(os_out.get_fullpath())):
        os.makedirs(os_out.get_fullpath())

    print("Writing uncompressed %s" % (out_filename.get_fullpath()))
    mdlnp.write_bam_file(out_filename)

for mdl in orig_models:
    process_model(Filename.from_os_specific(mdl))
