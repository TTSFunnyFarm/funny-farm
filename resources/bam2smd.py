from panda3d.core import Loader, NodePath, CharacterJoint, PartBundle, AnimBundle, AnimGroup, PartGroup, AnimChannelACMatrixSwitchType
from panda3d.core import GeomVertexReader, InternalName, TransformBlend, TransformBlendTable, Vec3, Vec2, GeomVertexArrayFormat
from panda3d.core import TransformState, Mat4, Filename, AnimBundleNode, JointVertexTransform

import math
import os

loader = Loader.getGlobalPtr()

def loadModel(path):
    return NodePath(loader.loadSync(path))

unknown = 0
def getUnknownName():
    global unknown
    name = "unknown{0}".format(unknown)
    unknown += 1
    return name

def boneFrameString(boneId, pos, rot):
    return "{0}  {1:.6f} {2:.6f} {3:.6f}  {4:.6f} {5:.6f} {6:.6f}\n".format(boneId, pos[0], pos[1], pos[2], rot[0], rot[1], rot[2])

FLT_EPSILON = 1e-5

def normalizeMat3(mat):
    for i in range(3):
        mat[i] = Vec3(mat[i][0], mat[i][1], mat[i][2]).normalized()
    return mat

def mat3NormalizedToEulO2(mat):
    i = 0
    j = 1
    k = 2

    cy = math.hypot(mat[i][i], mat[i][j])

    eul1 = Vec3()
    eul2 = Vec3()
    if cy > 16.0 * FLT_EPSILON:
        eul1[i] = math.atan2(mat[j][k], mat[k][k])
        eul1[j] = math.atan2(-mat[i][k], cy)
        eul1[k] = math.atan2(mat[i][j], mat[i][i])

        eul2[i] = math.atan2(-mat[j][k], -mat[k][k])
        eul2[j] = math.atan2(-mat[i][k], -cy)
        eul2[k] = math.atan2(-mat[i][j], -mat[i][i])
    else:
        eul1[i] = math.atan2(-mat[k][j], mat[j][j])
        eul1[j] = math.atan2(-mat[i][k], cy)
        eul1[k] = 0

        eul2 = eul1

    return [eul1, eul2]

def mat3NormalizedToEulO(mat):
    eul1, eul2 = mat3NormalizedToEulO2(mat)

    d1 = abs(eul1[0]) + abs(eul1[1]) + abs(eul1[2])
    d2 = abs(eul2[0]) + abs(eul2[1]) + abs(eul2[2])

    if d1 > d2:
        return eul2
    else:
        return eul1

class Skeleton:

    def __init__(self, roots):
        # Bone ID   :   PartGroup/AnimGroup
        self.bones = {}

        # PartGroup/AnimGroup   :   Bone ID
        self.group2BoneId = {}

        # Bone ID   :   Parent Bone ID
        self.boneParents = {}

        print(roots)

        if roots:
            for i in range(len(roots)):
                rootNp = roots[i]
                root = rootNp.node()
                if isinstance(root, AnimBundleNode):
                    bundle = root.getBundle()
                else:
                    bundle = root.getBundle(0)
                if i == 0:
                    parent = None
                else:
                    parentName = rootNp.getParent().node().getName()
                    parent = None
                    for j in range(len(roots)):
                        pRoot = roots[j].node()
                        if i == j:
                            continue
                        parent = pRoot.findJoint(parentName)
                        if parent:
                            break

                self.r_traverseSkeleton(bundle, parent, True)

    def r_traverseSkeleton(self, group, parentGroup, isRoot = False):
        if not "Bundle" in group.__class__.__name__:
            self.addBone(group, parentGroup)

        for i in range(group.getNumChildren()):
            self.r_traverseSkeleton(group.getChild(i), group if not isRoot else parentGroup)

    def addBone(self, bone, parentBone = None):
        boneId = len(self.bones)
        self.bones[boneId] = bone
        self.group2BoneId[bone] = boneId
        if parentBone and not "Bundle" in parentBone.__class__.__name__:
            self.boneParents[boneId] = self.group2BoneId[parentBone]
        else:
            self.boneParents[boneId] = -1

    def getBone(self, boneId):
        return self.bones.get(boneId, None)

    def getBoneId(self, bone):
        return self.group2BoneId[bone]

    def getBoneParent(self, boneId):
        return self.boneParents[boneId]

    def getBoneName(self, boneId):
        return self.bones[boneId].getName()

    def __str__(self):
        ret = "nodes\n"
        if len(self.bones):
            boneKeys = sorted(self.bones.keys())
            for i in range(len(boneKeys)):
                boneId = boneKeys[i]
                ret += "{0} \"{1}\" {2}\n".format(boneId, self.getBoneName(boneId), self.getBoneParent(boneId))
        else:
            ret += "0 \"root\" -1\n"
        ret += "end\n"

        return ret

def processModel(path):
    scene = loadModel(path)
    if scene.isEmpty():
        print("Error converting `{0}`!".format(path))
        return

    fPath = Filename.fromOsSpecific(path)
    outputPath = Filename.toOsSpecific(Filename("bam2smd/" + fPath.getDirname() + "/" + fPath.getBasenameWoExtension() + "/"))
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    isCharacter = not scene.find("**/+Character").isEmpty()
    isAnimation = not scene.find("**/+AnimBundleNode").isEmpty()

    if not isAnimation:
        if isCharacter:
            nodes = Skeleton(scene.findAllMatches("**/+Character"))
        else:
            nodes = Skeleton(None)

        names = {}

        for geomNp in scene.findAllMatches("**/+GeomNode"):
            smd = "version 1\n"

            smd += str(nodes)

            smd += "skeleton\n"
            smd += "time 0\n"
            if isCharacter:
                boneIds = sorted(nodes.bones.keys())
                for iBone in range(len(boneIds)):
                    boneId = boneIds[iBone]
                    bone = nodes.bones[boneId]
                    if isinstance(bone, CharacterJoint):
                        boneTform = bone.getTransformState()
                        pos = boneTform.getPos()
                        boneMat = boneTform.getMat().getUpper3()
                        #boneMat.transposeInPlace()
                        rot = mat3NormalizedToEulO(boneMat)
                    else:
                        pos = Vec3()
                        rot = Vec3()
                    smd += boneFrameString(boneId, pos, rot)
            else:
                smd += "0  0 0 0  0 0 0\n"
            smd += "end\n"

            smd += "triangles\n"
            for geom in geomNp.node().getGeoms():
                geom = geom.decompose()
                vdata = geom.getVertexData()
                blendTable = vdata.getTransformBlendTable()
                for prim in geom.getPrimitives():
                    numTris = prim.getNumPrimitives()
                    for nTri in range(numTris):
                        start = prim.getPrimitiveStart(nTri)
                        end = prim.getPrimitiveEnd(nTri)

                        smd += "no_material\n"

                        for primVert in range(start, end):
                            vertIdx = prim.getVertex(primVert)

                            reader = GeomVertexReader(vdata)

                            reader.setColumn(InternalName.getVertex())
                            reader.setRow(vertIdx)
                            pos = reader.getData3f()

                            uv = Vec2(0, 0)
                            if vdata.hasColumn(InternalName.getTexcoord()):
                                reader.setColumn(InternalName.getTexcoord())
                                reader.setRow(vertIdx)
                                uv = reader.getData2f()

                            norm = Vec3.forward()
                            if vdata.hasColumn(InternalName.getNormal()):
                                reader.setColumn(InternalName.getNormal())
                                reader.setRow(vertIdx)
                                norm = reader.getData3f()

                            smd += "0  {0:.6f} {1:.6f} {2:.6f}  {3:.6f} {4:.6f} {5:.6f}  {6:.6f} {7:.6f}  ".format(pos[0], pos[1], pos[2],
                                                            norm[0], norm[1], norm[2], uv[0], uv[1])
                            if (isCharacter and blendTable and vdata.getNumArrays() > 1 and
                            vdata.getArray(1).hasColumn(InternalName.getTransformBlend())):
                                reader.setColumn(1, vdata.getArray(1).getArrayFormat().getColumn(InternalName.getTransformBlend()))
                                reader.setRow(vertIdx)
                                nBlend = reader.getData1i()
                                blend = blendTable.getBlend(nBlend)
                                numTransforms = blend.getNumTransforms()
                                smd += "{0} ".format(numTransforms)
                                for nTransform in range(numTransforms):
                                    transform = blend.getTransform(nTransform)
                                    if isinstance(transform, JointVertexTransform):
                                        boneId = nodes.getBoneId(transform.getJoint())
                                        smd += "{0} {1:.6f} ".format(boneId, blend.getWeight(nTransform))
                            else:
                                smd += "1 0 1.0"
                            smd += "\n"
            smd += "end\n"

            smdFile = geomNp.getName()
            if len(smdFile) == 0:
                smdFile = getUnknownName()
            elif names.get(smdFile, 0) > 0:
                smdFile = smdFile + "_{0}".format(names[smdFile])
                names[smdFile] += 1
            else:
                names[smdFile] = 1
            smdFile += ".smd"

            outFile = open(outputPath + "\\" + smdFile, "w")
            outFile.write(smd)
            outFile.flush()
            outFile.close()
    else:
        bundles = scene.findAllMatches("**/+AnimBundleNode")
        bundle = bundles[0].node().getBundle()
        nodes = Skeleton(bundles)

        smd = "version 1\n"

        smd += str(nodes)

        smd += "skeleton\n"
        numFrames = bundle.getNumFrames()
        boneIds = sorted(nodes.bones.keys())
        for iFrame in range(numFrames):
            smd += "time {0}\n".format(iFrame)
            for iBone in range(len(boneIds)):
                bone = nodes.getBone(boneIds[iBone])
                if isinstance(bone, AnimChannelACMatrixSwitchType):
                    boneFrameMat = Mat4()
                    bone.getValueNoScaleShear(iFrame, boneFrameMat)
                    boneFrameTransform = TransformState.makeMat(boneFrameMat)
                    pos = boneFrameTransform.getPos()
                    rotMat = boneFrameMat.getUpper3()
                    #rotMat.transposeInPlace()
                    rot = mat3NormalizedToEulO(rotMat)
                    smd += boneFrameString(boneIds[iBone], pos, rot)

        smd += "end\n"

        smdFile = fPath.getBasenameWoExtension() + ".smd"
        outFile = open(outputPath + "\\" + smdFile, "w")
        outFile.write(smd)
        outFile.flush()
        outFile.close()

#processModel("phase_3/models/char/tt_a_chr_dgm_shorts_torso_1000.bam")
#processModel("phase_3/models/char/tt_a_chr_dgm_shorts_legs_1000.bam")
#processModel("phase_3/models/char/tt_a_chr_dgm_skirt_head_1000.bam")
#processModel("phase_3/models/char/tt_a_chr_dgm_shorts_torso_neutral.bam")
#processModel("phase_3/models/char/tt_a_chr_dgm_skirt_head_neutral.bam")
#processModel("flippy_palette.bam")
#processModel("phase_3/models/char/tt_a_chr_dgm_shorts_legs_run.bam")
#processModel("phase_3/models/char/tt_a_chr_dgm_shorts_torso_run.bam")
#processModel("phase_4/models/char/suitB-lose.bam")
#processModel("phase_3.5/models/char/suitA-mod.bam")
#processModel("phase_3.5/models/char/suitB-mod.bam")
#processModel("phase_3.5/models/char/suitC-mod.bam")
#processModel("phase_9/models/char/gearProp.bam")
#processModel('phase_4/models/cogHQ/gagTank.bam')
processModel("phase_5/models/char/suitB-throw-object.bam")
