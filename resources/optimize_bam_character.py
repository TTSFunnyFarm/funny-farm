# Optimize the ridiculous models made by Disney.

from panda3d.bullet import *
from panda3d.bsp import *
from panda3d.core import Loader, CharacterJointEffect, TransformBlend, JointVertexTransform, NodePath, TexturePool

loader = Loader.get_global_ptr()

def do_model(path, out, exclude = []):
    orig_mdl = NodePath(loader.load_sync(path))

    orig_mdl.ls()

    #char = orig_mdl.find("**/+Character").node()
    #root = char.get_bundle(0)

    for gnnp in orig_mdl.find_all_matches("**/+GeomNode"):
        for i in range(gnnp.node().getNumGeoms()):
            state = gnnp.node().getGeomState(i)
            if state.hasAttrib(BSPMaterialAttrib.getClassType()):
                attr = state.getAttrib(BSPMaterialAttrib.getClassType())
                if attr.getMaterial():
                    tex = TexturePool.loadTexture(attr.getMaterial().getKeyvalue("$basetexture"))
                    print(attr.getMaterial().getKeyvalue("$basetexture") + " : " + str(tex.getOrigFileXSize()) + " " + str(tex.getOrigFileYSize()))

    """
    for node in orig_mdl.find_all_matches("**/+ModelNode"):
        if node.has_effect(CharacterJointEffect.get_class_type()):
            print("Found exposed joint", node.get_name())
            joint_name = node.get_name()
            if joint_name in exclude:
                continue
            joint = root.find_child(joint_name)
            gns = node.find_all_matches("**/+GeomNode")
            for gnnp in gns:
                print("\tApplying vertices to joint on gn", gnnp.get_name())
                gn = gnnp.node()
                for i in range(gn.get_num_geoms()):
                    geom = gn.modify_geom(i)
                    state = gn.get_geom_state(i)
                    vdata = geom.modify_vertex_data()
                    blend_table = vdata.modify_transform_blend_table()
                    for j in range(vdata.get_num_rows()):
                        blend_table.add_blend(TransformBlend(JointVertexTransform(joint), 1.0))
                    vdata.set_transform_blend_table(blend_table)
                    geom.set_vertex_data(vdata)
                    gn.set_geom(i, geom)
                gnnp.wrt_reparent_to(node.get_parent())
        node.remove_node()
    """

    orig_mdl.ls()
    #orig_mdl.flatten_strong()
    #orig_mdl.ls()

    #orig_mdl.write_bam_file(out)

do_model("phase_9/models/char/gearProp.bam", "bossCog-legs-zero.bam", ["joint_pelvis"])
