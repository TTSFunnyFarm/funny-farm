from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import *
from direct.showbase.DirectObject import DirectObject
notify = directNotify.newCategory("SelectManager")
class SelectManager(DirectObject):
    def __init__(self):
        #CollisionTraverser  and a Collision Handler is set up
        self.picker = CollisionTraverser()
        #self.picker.showCollisions(render)
        self.pq = CollisionHandlerQueue()

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(2))
        #box.setCollideMask(BitMask32.bit(1))

        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP,self.pq)

        self.accept('mouse1',self.mouseDown)

    def mouseDown(self):
        # check if we have access to the mouse
        if base.mouseWatcherNode.hasMouse():
            # get the mouse position
            mat = Mat4(camera.getMat())
            mat.invertInPlace()
            base.mouseInterfaceNode.setMat(mat)
            mpos = base.mouseWatcherNode.getMouse()

            # set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(base.camNode,mpos.getX(),mpos.getY())
            self.picker.traverse(render)
            # if we have hit something sort the hits so that the closest is first and highlight the node
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()
                pickedObj = pickedObj.getParent()
                pickedObj = pickedObj.findNetTag('clickable')
                #pickedObj.setZ(pickedObj.getZ() + 5)
                if not pickedObj:
                    return
                print('click on ' + pickedObj.getName())
                if base.lvlEditor.selected == pickedObj:
                    return
                base.lvlEditor.selectItem(pickedObj)
            #elif base.lvlEditor.selected:
                #obj = base.objectMgr.getObject(hash(self.selected))
                #obj.onClick()
                #print(self.selected)
                #self.selected = None
