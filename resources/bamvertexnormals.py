from panda3d.core import *

import os
import sys
import glob2
import math
phases = [3, 3.5, 4, 5, 5.5, 6, 7, 8, 9, 10, 11, 12, 13]
orig_models = []
for phase in phases:
    orig_models += glob2.glob("non_revamp\\phase_{0}\\models\\**\\*.bam".format(phase))

vertexDatas = {}
orig2modVdata = {}

def isAnimation(node):
    return not node.find("**/+AnimBundleNode").isEmpty()

def alreadyHasVertexData(vdata):
    for data in vertexDatas.keys():
        if vdata.compareTo(data) == 0:
            return True
    return False

class VertexReference:
    pass

currentMdlFile = ""
currentGeomNode = ""

class VertexData:

    def __init__(self, vdata):
        self.vdata = vdata

        format = GeomVertexFormat(self.vdata.getFormat())
        for i in range(format.getNumArrays()):
            array = format.modifyArray(i)
            if array.hasColumn('vertex') and not array.hasColumn('normal'):
                array.addColumn('normal', 3, GeomVertexFormat.NT_stdfloat, GeomVertexFormat.C_normal)
                format.setArray(i, array)
        self.vdata.setFormat(GeomVertexFormat.registerFormat(format))

        self.primitives = []
        self.vertices = []
        for i in range(vdata.getNumRows()):
            self.vertices.append(Vertex(i))
        """
        reader = GeomVertexReader(vdata, 'vertex')
        for i in range(vdata.getNumRows()):
            vert = self.vertices[i]
            reader.setRow(i)
            vertPos = Vec3(reader.getData3f())
            for j in range(vdata.getNumRows()):
                if i == j:
                    continue
                reader.setRow(j)
                pos = Vec3(reader.getData3f())
                if pos == vertPos:
                    vert.similarVerts.append(self.vertices[j])
        """

        self.geoms = []
        self.geomStates = []

    def collectVertexNormals(self):
        collection = {}
        for prim in self.primitives:
            for i in range(len(prim.vpositions)):
                ref = VertexReference()
                ref.polygon = prim
                ref.normal = prim.normal
                ref.vertex = i
                pos = prim.vpositions[i]
                if not pos in collection:
                    collection[pos] = [ref]
                else:
                    collection[pos].append(ref)

        return collection

    def applyNormals(self):
        cosAngle = math.cos(deg2Rad(90.0))
        collection = self.collectVertexNormals()

        # First apply face normals
        #writer = GeomVertexWriter(self.vdata)
        #for prim in self.primitives:
        #    for row in prim.vertices:
        #        writer.setRow(row)
        #        writer.setColumn(InternalName.getNormal())
        #        writer.setData3f(prim.normal)

        citerator = list(collection.items())
        ci = 0
        while (ci < len(citerator)):
            group = citerator[ci][1]
            pos = citerator[ci][0]
            #print("{0} polygons on vertex at position {1}".format(len(group), pos))

            gi = 0
            while (gi < len(group)):
                baseRef = group[gi]
                newGroup = []
                leftoverGroup = []
                newGroup.append(baseRef)
                gi += 1

                while (gi < len(group)):
                    ref = group[gi]
                    dot = baseRef.normal.dot(ref.normal)
                    if dot > cosAngle:
                        newGroup.append(ref)
                    else:
                        leftoverGroup.append(ref)
                    gi += 1

                self.doComputeVertexNormals(newGroup)
                group = leftoverGroup
                gi = 0
            ci += 1

    def doComputeVertexNormals(self, group):

        normal = Vec3(0)
        for ref in group:
            normal += ref.normal
        normal /= float(len(group))
        normal.normalize()

        for ref in group:

            row = ref.polygon.origVertices[ref.vertex]
            #print("orig vertex", row)

            reader = GeomVertexReader(self.vdata)
            reader.setColumn('vertex')
            reader.setRow(row)
            #print(reader.getData3f())

            #if self.vdata.hasColumn('transform_blend'):
            #    reader.setColumn('transform_blend')
            #    reader.setRow(row)
            #    print("Transform blend before:", reader.getData1f())

            # Create a unique vertex in the table for this polygon
            temp = GeomVertexData('temp', self.vdata.getFormat(), self.vdata.getUsageHint())
            temp.setNumRows(1)
            temp.copyRowFrom(0, self.vdata, row, Thread.getCurrentThread())
            twriter = GeomVertexWriter(temp, 'normal')
            twriter.setRow(0)
            twriter.setData3f(normal)

            #if temp.hasColumn('transform_blend'):
            #    treader = GeomVertexReader(temp, 'transform_blend')
            #    treader.setRow(0)
            #    print("Transform blend copy:", treader.getData1f())

            #print(treader.getData3f())

            newRow = self.vdata.getNumRows()
            self.vdata.setNumRows(newRow + 1)
            self.vdata.copyRowFrom(newRow, temp, 0, Thread.getCurrentThread())

            #if self.vdata.hasColumn('transform_blend'):
            #    nreader = GeomVertexReader(self.vdata)
            #    nreader.setColumn('transform_blend')
            #    nreader.setRow(newRow)
            #    print("Transform blend after 2:", nreader.getData1f())

            #nreader.setColumn('vertex')
            #nreader.setRow(newRow)
            #print(nreader.getData3f())

            #print("Polygon vertices before", ref.polygon.vertices)

            ref.polygon.vertices[ref.vertex] = newRow

    def applyNormalsNah(self):
        writer = GeomVertexWriter(self.vdata)
        for vert in self.vertices:
            writer.setRow(vert.vertexIdx)
            writer.setColumn(InternalName.getNormal())
            writer.setData3f(vert.calcNormal())

class Primitive:

    def __init__(self, primitive, start, end, vdata, geomIdx):
        self.geomIdx = geomIdx
        self.vdata = vdata
        reader = GeomVertexReader(vdata)
        self.vertices = []
        self.origVertices = []
        vpositions = []
        for i in range(start, end):
            vertIdx = primitive.getVertex(i)
            self.vertices.append(vertIdx)
            self.origVertices.append(vertIdx)
            reader.setRow(vertIdx)
            reader.setColumn(InternalName.getVertex())
            pos = Vec3(reader.getData3f())
            vpositions.append(pos)
            vert = vertexDatas[vdata].vertices[vertIdx]
            vert.primitivesUsing.append(self)
            for similarVert in vert.similarVerts:
                similarVert.primitivesUsing.append(self)

        self.normal = Vec3(0)
        # Now that we have the vertex positions for this primitive,
        # calculate the face normal.
        for i in range(len(vpositions)):
            v0 = vpositions[i]
            v1 = vpositions[(i + 1) % len(vpositions)]
            self.normal[0] += v0[1] * v1[2] - v0[2] * v1[1]
            self.normal[1] += v0[2] * v1[0] - v0[0] * v1[2]
            self.normal[2] += v0[0] * v1[1] - v0[1] * v1[0]
        self.normal.normalize()

        self.vpositions = vpositions
        self.primitive = primitive

    def getNormal(self):
        return self.normal

class Vertex:

    def __init__(self, vertexIdx):
        # vertexIdx: index into GeomVertexData
        # primitivesUsing: list of GeomPrimitives which reference this vertex
        #
        # To calculate a normal for this vertex, we will average all of the primitive normals
        # that reference this vertex.
        self.vertexIdx = vertexIdx
        self.primitivesUsing = []
        self.similarVerts = []
        self.smooth = True

    def calcNormal(self):
        normal = Vec3(0)
        if self.smooth:
            for prim in self.primitivesUsing:
                normal += prim.getNormal()
            normal /= float(len(self.primitivesUsing))
            normal.normalize()
            return normal
        elif len(self.primitivesUsing) > 0:
            normal = self.primitivesUsing[0].normal
        return normal

def processPrimitive(prim, vdata, geom):
    prim = prim.decompose()
    prims = prim.getNumPrimitives()
    for i in range(prims):
        start = prim.getPrimitiveStart(i)
        end = prim.getPrimitiveEnd(i)
        primData = Primitive(prim, start, end, vdata, geom)
        vertexDatas[vdata].primitives.append(primData)

def processGeom(geom, state):
    global vertexDatas
    origVData = geom.getVertexData()
    if not origVData in orig2modVdata:
        vdata = geom.modifyVertexData()
        orig2modVdata[origVData] = vdata
        vertexDatas[vdata] = VertexData(vdata)
    else:
        vdata = orig2modVdata[origVData]

    if not vdata in vertexDatas:
        # question mark?
        return 0

    vertexDatas[vdata].geoms.append(geom)
    vertexDatas[vdata].geomStates.append(state)

    #print("appended geom", geom, "to vertex data", vertexDatas[vdata])
    for i in range(geom.getNumPrimitives()):
        prim = geom.modifyPrimitive(i)
        processPrimitive(prim, vdata, len(vertexDatas[vdata].geoms) - 1)

    return 1

def processGeomNode(geomNode):
    # A GeomNode is a node in the scene graph which contains Geom objects,
    # the smallest pieces of renderable geometry.
    # Vertices cannot be shared across GeomNodes
    # Only Geoms in the same GeomNode can possibly share vertices
    #
    # To calculate a vertex normal for each vertex of the GeomVertexDatas,
    # we must walk through each primitive of each Geom

    global currentGeomNode
    currentGeomNode = geomNode.getName()

    global vertexDatas
    vertexDatas = {}
    orig2modVdata = {}

    for i in range(geomNode.getNumGeoms()):
        geom = geomNode.modifyGeom(i)
        if not processGeom(geom, geomNode.getGeomState(i)):
            return 0

    geomNode.removeAllGeoms()

    for vertexData in vertexDatas.values():
        vertexData.applyNormals()

        # remove unused vertices
        references = []
        for row in range(vertexData.vdata.getNumRows()):
            references.append(0)
            for prim in vertexData.primitives:
                if row in prim.vertices:
                    references[row] += 1

        # This is a cheat, we know that all of the unreferenced vertices are at the beginning.
        # So we'll just subtract the number of unreferenced vertices from each primitive index.
        #unreferenced = references.count(0)
        #for prim in vertexData.primitives:
            #for i in range(len(prim.vertices)):
                #prim.vertices[i] -= unreferenced

        #GeomVertexData(vertexData.vdata.getName(), vertexData.vdata.getFormat(), vertexData.vdata.getUsageHint())
        #for i in range(unreferenced, vertexData.vdata.getNumRows()):
            #newData.copyRowFrom(i - unreferenced, vertexData.vdata, i, Thread.getCurrentThread())

        for i in range(len(vertexData.geoms)):
            geom = vertexData.geoms[i]
            geom.clearPrimitives()
            state = vertexData.geomStates[i]
            # Apply the modified GeomVertexData to the Geom.
            # It should have a new filled in vertex normal column.
            geom.setVertexData(vertexData.vdata)
            geomNode.addGeom(geom, state)

        for primData in vertexData.primitives:

            if len(primData.vertices) < 3:

                print("Error: primitive with less than 3 verts")
                return 0

                continue

            prim = GeomTriangles(primData.primitive.getUsageHint())
            geom = vertexData.geoms[primData.geomIdx]
            prim.addVertices(*primData.vertices)
            prim.closePrimitive()
            geom.addPrimitive(prim)

            vertexData.geoms[primData.geomIdx] = geom

            #reader = GeomVertexReader(vertexData.vdata)
            #if vertexData.vdata.hasColumn('transform_blend'):
            #    reader.setColumn('transform_blend')
            #    print("Transform blend:")
            #    for i in range(len(primData.vertices)):
            #        reader.setRow(primData.vertices[i])
            #        data = reader.getData1f()
            #        print("\t", data)

        for i in range(len(vertexData.geoms)):
            geom = vertexData.geoms[i]
            state = vertexData.geomStates[i]
            geomNode.addGeom(geom, state)

    return 1

def processModel(mdlFile):
    print("Processing model file `{0}`".format(mdlFile))
    global currentMdlFile
    currentMdlFile = mdlFile.getFullpath()
    mdl = NodePath(Loader.getGlobalPtr().loadSync(mdlFile))

    if not isAnimation(mdl):
        geomNodes = mdl.findAllMatches("**/+GeomNode")
        for gnnp in geomNodes:
            if not processGeomNode(gnnp.node()):

                print("Skipping, error processing")
                return
        outFilename = Filename(mdlFile.getFullpath().replace("non_revamp", "revamp2"))
        if (not os.path.exists(outFilename.getDirname())):
            os.makedirs(outFilename.getDirname())
        mdl.writeBamFile(outFilename)
    else:
        print("It's an animation, skipping")

    mdl.removeNode()
    del mdl

for mdl in orig_models:
    processModel(Filename.fromOsSpecific(mdl))

#processModel(Filename("non_revamp/sphere.egg"))
