from panda3d.core import *
from direct.actor.Actor import Actor
actor = Actor()
actor.loadModel("phase_3/models/char/tt_a_chr_dgm_shorts_legs_1000.bam", "legs")
actor.find("**/boots_long").removeNode()
actor.find("**/boots_short").removeNode()
actor.find("**/shoes").removeNode()
actor.loadModel("phase_3/models/char/tt_a_chr_dgm_skirt_head_1000.bam", "head")

actor.loadAnims({"neutral": "phase_3/models/char/tt_a_chr_dgm_shorts_legs_neutral.bam"}, "legs")
actor.loadModel("phase_3/models/char/tt_a_chr_dgm_shorts_torso_1000.bam", "torso")
actor.loadAnims({"neutral": "phase_3/models/char/tt_a_chr_dgm_shorts_torso_1000.bam"}, "torso")
#actor.loadModel("phase_3/models
actor.getPart("torso").reparentTo(actor.find("**/joint_hips"))
actor.getPart("head").reparentTo(actor.getPart("torso").find("**/def_head"))
#actor.getGeomNode().setScale(0.85)
actor.clearModelNodes()
actor.flattenLight()
actor.postFlatten()
actor.ls()
#actor.listJoints()
actor.writeBamFile("flippy.bam")

#head = Loader.getGlobalPtr().loadSync("phase_3/models/char/tt_a_chr_dgm_skirt_head_1000.bam")
#NodePath(head).writeBamFile("flippy_head.bam")


