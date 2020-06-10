from panda3d.core import *
from panda3d.bsp import *

import os

def lbr():
    print("\n====================================================\n")

inp_file = raw_input("Input file: ")
out_file = raw_input("Output file: ")

lbr()

engine = os.environ.get("CIOENGINE", "..\\..\\cio-panda3d\\built_x64")

normalsStr = ""
normals = True
while (normalsStr not in ["y", "n"]):
    normalsStr = raw_input("Calculate vertex normals? [Y/N]: ").lower()
    if normalsStr == "y":
        normals = True
    elif normalsStr == "n":
        normals = False

print("Running egg-trans...")
cmd  = engine + "\\bin\\egg-trans -o {0} ".format(inp_file)
if normals:
    print("Also calculating vertex normals")
    cmd += "-nv 90 "
cmd += "-tbnall "
cmd += inp_file
os.system(cmd)

lbr()

loader = Loader.getGlobalPtr()
node = loader.loadSync(inp_file)
np = NodePath(node)
np.clearMaterial()
for child in np.findAllMatches("**"):
    child.clearMaterial()
    if child.node().isOfType(GeomNode.getClassType()):
        for i in range(child.node().getNumGeoms()):
            state = child.node().getGeomState(i)
            if state.hasAttrib(MaterialAttrib.getClassType()):
                state = state.removeAttrib(MaterialAttrib.getClassType())
                child.node().setGeomState(i, state)
            if state.hasAttrib(TextureAttrib.getClassType()):
                state = state.removeAttrib(TextureAttrib.getClassType())
                child.node().setGeomState(i, state)

meshes = np.findAllMatches("**/+GeomNode")
for meshNp in meshes:
    mat_file = raw_input("Material file for mesh `{0}`: ".format(meshNp.getName()))
    mat = BSPMaterial.getFromFile(mat_file)
    meshNp.setAttrib(BSPMaterialAttrib.make(mat))
    if mat.hasTransparency():
        print(meshNp.getName(), "has $translucent or $alpha")
        meshNp.setTransparency(TransparencyAttrib.MDual, 1)
    dbs = raw_input("\tDouble sided? [Y/N]: ").lower()
    if dbs == "y":
        meshNp.setTwoSided(True, 1)

lbr()

optimizeStr = ""
optimize = False
while (optimizeStr not in ["y", "n"]):
    optimizeStr = raw_input("Optimize model? (highly recommended) [Y/N]: ").lower()
    if optimizeStr == "y":
        optimize = True
    elif optimizeStr == "n":
        optimize = False

lbr()

if optimize:
    print("\nModel before optimization:")
    np.ls()

    np.flattenStrong()

    print("\nModel after optimization:")
    np.ls()
    print

lbr()

print("Writing {0}...".format(out_file))
np.writeBamFile(out_file)
