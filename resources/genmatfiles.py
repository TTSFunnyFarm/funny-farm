
from panda3d.core import *
from panda3d.bsp import *

import os
import sys
import glob2
import math

DEBUG_MATS = False

rsrc = "/d/OTHER/lachb/Documents/cio/game/resources/"
prefix = "withmat\\" if DEBUG_MATS else ""

phases = [14]
orig_models = []
for phase in phases:
    orig_models += glob2.glob(prefix + "phase_{0}\\models\\**\\*.bam".format(phase))

matFiles = []

def genVertexLitGenericMatFile(matFilename, texture, material = None):
    fn = Filename(texture.getFilename())
    fn.makeRelativeTo(rsrc, True)
    afn = Filename(texture.getAlphaFilename())
    afn.makeRelativeTo(rsrc, True)

    src =     "VertexLitGeneric\n"
    src +=     "{\n"
    if texture.hasFilename():
        src +=     "\t\"$basetexture\"            \"{0}\"\n".format(fn.getFullpath())
    if texture.hasAlphaFilename():
        src +=    "\t\"$basetexture_alpha\"    \"{0}\"\n".format(afn.getFullpath())
        src +=     "\t\"$translucent\"            \"1\"\n"

    if material is not None:
        material = material.getMaterial()
        if material.hasSpecular():
            spec = material.getSpecular()
            src += "\t\"$phong\"            \"1\"\n"
            src += "\t\"$phongexponent\"    \"{0}\"\n".format(material.getShininess())
            src += "\t\"$phongtint\"        \"{0} {1} {2}\"\n".format(spec[0], spec[1], spec[2])


    src +=     "}\n"

    vfs = VirtualFileSystem.getGlobalPtr()
    vfs.writeFile(matFilename, src, True)

def matFileFromTexture(textureFilename):
    return Filename(textureFilename.getFullpathWoExtension() + ".mat")

def processState(state):
    if DEBUG_MATS:
        if state.hasAttrib(BSPMaterialAttrib.getClassSlot()):
            bma = state.getAttrib(BSPMaterialAttrib.getClassSlot())
            if bma.getMaterial():
                print("=====================================================================")
                print("Material", bma.getMaterial().getFile().getFullpath(), "referenced")
                print("\tShader:", bma.getMaterial().getShader())
                print("\t$basetexture:", bma.getMaterial().getKeyvalue("$basetexture"))
                print("Has TextureAttrib?", state.hasAttrib(TextureAttrib.getClassType()))

        return state

    if state.hasAttrib(TextureAttrib.getClassSlot()):
        tattr = state.getAttrib(TextureAttrib.getClassSlot())
        if (tattr.getNumOnStages() > 1):
            print("Warning: TextureAttrib has multiple on stages")
        elif (tattr.getNumOnStages() == 0):
            print("Warning: TextureAttrib has no texture")
            return state
        stage = tattr.getOnStage(0)
        tex = tattr.getOnTexture(stage)
        matFilename = matFileFromTexture(tex.getFullpath())
        matFilename.makeRelativeTo(rsrc, True)
        mat = None
        if state.hasAttrib(MaterialAttrib.getClassSlot()):
            mat = state.getAttrib(MaterialAttrib.getClassSlot())
        if matFilename.getFullpath() not in matFiles:
            print("Writing mat file " + matFilename.getFullpath())
            genVertexLitGenericMatFile(matFilename, tex, mat)
            matFiles.append(matFilename.getFullpath())

        mat = BSPMaterial.getFromFile(matFilename)
        mattr = BSPMaterialAttrib.make(mat)
        state = state.setAttrib(mattr)
        state = state.removeAttrib(TextureAttrib.getClassSlot())
        if mat:
            state = state.removeAttrib(MaterialAttrib.getClassSlot())

    return state

def r_processNode(node):

    nState = node.getState()
    nProcState = processState(nState)
    if (nProcState != nState):
        node.setState(nProcState)

    if node.isOfType(GeomNode.getClassType()):
        for i in range(node.getNumGeoms()):
            state = node.getGeomState(i)
            procState = processState(state)
            if (procState != state):
                node.setGeomState(i, procState)

    # process the children
    for i in range(node.getNumChildren()):
        r_processNode(node.getChild(i))

def processModel(mdlfile):
    fp = mdlfile.getFullpath()
    if ("/gui/" in fp or "/fonts/" in fp or "/news/" in fp or "/misc/" in fp):
        # skip
        return

    print("Reading", mdlfile.getFullpath())
    loader = Loader.getGlobalPtr()
    try:
        node = loader.loadSync(mdlfile)
    except:
        print("Exception occurred loading model", mdlfile.getFullpath())
        return

    if not node:
        print(mdlfile.getFullpath(), "is bad")
        return

    np = NodePath(node)
    if not np.find("**/+AnimBundleNode").isEmpty():
        # skip animation
        return

    r_processNode(node)

    if not DEBUG_MATS:
        outFilename = Filename("withmat/" + fp)
        if (not os.path.exists(outFilename.getDirname())):
            os.makedirs(outFilename.getDirname())
        np.writeBamFile(outFilename)

#for origMdl in orig_models:
#    processModel(Filename.fromOsSpecific(origMdl))

processModel(Filename("phase_14/models/props/megaphone.bam"))
