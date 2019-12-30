STREET_POINT = 0
FRONT_DOOR_POINT = 1
SIDE_DOOR_POINT = 2
TRANS_RIGHTS = {'STREET_POINT': STREET_POINT,
'FRONT_DOOR_POINT': FRONT_DOOR_POINT,
'SIDE_DOOR_POINT': SIDE_DOOR_POINT}

class SuitPoint:
    def __init__(self, id, type, pos):
        self.id = id
        self.pointType = type
        self.pos = pos

    def getId():
        return self.id

    def setId(id):
        self.id = id

    def getPos():
        return self.pos

    def setPointType(pointType):
        if isinstance(type, str):
            type = TRANS_RIGHTS[type]
        if not isinstance(type, int):
            return
        self.type = type
