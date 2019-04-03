from panda3d.core import *
from toontown.toonbase import FunnyFarmGlobals

STREET_POINT = 0
FRONT_DOOR_POINT = 1

SuitPoints = {
    FunnyFarmGlobals.RicketyRoad: [
        (0, STREET_POINT, Point3(-5, 15, -0.5)),
        (1, STREET_POINT, Point3(25, 15, -0.5)),
        (2, STREET_POINT, Point3(55, 15, -0.5)),
        (3, STREET_POINT, Point3(95, 15, -0.5)),
        (4, STREET_POINT, Point3(135, 15, -0.5)),
        (5, STREET_POINT, Point3(165, 15, -0.5)),
        (6, STREET_POINT, Point3(165, 65, -0.5)),
        (7, STREET_POINT, Point3(165, 102, -0.5)),
        (8, STREET_POINT, Point3(165, 135, -0.5)),
        (9, STREET_POINT, Point3(140, 135, -0.5)),
        (10, STREET_POINT, Point3(115, 135, -0.5)),
        (11, STREET_POINT, Point3(95, 135, -0.5)),
        (12, STREET_POINT, Point3(95, 105, -0.5)),
        (13, STREET_POINT, Point3(95, 75, -0.5)),
        (14, STREET_POINT, Point3(65, 75, -0.5)),
        (15, STREET_POINT, Point3(35, 75, -0.5)),
        (16, STREET_POINT, Point3(15, 75, -0.5)),
        (17, STREET_POINT, Point3(8, 80, -0.5)),
        (18, STREET_POINT, Point3(5, 90, -0.5)),
        (19, STREET_POINT, Point3(5, 110, -0.5)),
        (20, STREET_POINT, Point3(5, 130, -0.5)),
        (21, STREET_POINT, Point3(8, 140, -0.5)),
        (22, STREET_POINT, Point3(15, 145, -0.5)),
        (23, STREET_POINT, Point3(45, 145, -0.5)),
        (24, STREET_POINT, Point3(45, 175, -0.5)),
        (25, STREET_POINT, Point3(45, 205, -0.5)),
        (26, STREET_POINT, Point3(75, 205, -0.5)),
        (27, STREET_POINT, Point3(105, 205, -0.5)),
        (28, STREET_POINT, Point3(145, 205, -0.5)),
        (29, STREET_POINT, Point3(145, 215, -0.5)),
        (30, STREET_POINT, Point3(105, 215, -0.5)),
        (31, STREET_POINT, Point3(75, 215, -0.5)),
        (32, STREET_POINT, Point3(35, 215, -0.5)),
        (33, STREET_POINT, Point3(35, 185, -0.5)),
        (34, STREET_POINT, Point3(35, 155, -0.5)),
        (35, STREET_POINT, Point3(15, 155, -0.5)),
        (36, STREET_POINT, Point3(5, 150, -0.5)),
        (37, STREET_POINT, Point3(-2, 140, -0.5)),
        (38, STREET_POINT, Point3(-5, 130, -0.5)),
        (39, STREET_POINT, Point3(-5, 110, -0.5)),
        (40, STREET_POINT, Point3(-5, 90, -0.5)),
        (41, STREET_POINT, Point3(-2, 80, -0.5)),
        (42, STREET_POINT, Point3(5, 70, -0.5)),
        (43, STREET_POINT, Point3(15, 65, -0.5)),
        (44, STREET_POINT, Point3(35, 65, -0.5)),
        (45, STREET_POINT, Point3(65, 65, -0.5)),
        (46, STREET_POINT, Point3(95, 65, -0.5)),
        (47, STREET_POINT, Point3(125, 65, -0.5)),
        (48, STREET_POINT, Point3(155, 65, -0.5)),
        (49, STREET_POINT, Point3(155, 25, -0.5)),
        (50, STREET_POINT, Point3(125, 25, -0.5)),
        (51, STREET_POINT, Point3(95, 25, -0.5)),
        (52, STREET_POINT, Point3(55, 25, -0.5)),
        (53, STREET_POINT, Point3(25, 25, -0.5)),
        (54, STREET_POINT, Point3(-5, 25, -0.5))
    ]
}

BattleCells = {
    FunnyFarmGlobals.RicketyRoad: [
        (Point3(0, 20, -0.5), 30),
        (Point3(32, 20, -0.5), 315),
        (Point3(64, 20, -0.5), 0),
        (Point3(96, 20, -0.5), 180),
        (Point3(128, 20, -0.5), 225),
        (Point3(160, 20, -0.5), 315),
        (Point3(160, 70, -0.5), 90),
        (Point3(160, 100, -0.5), 90),
        (Point3(160, 130, -0.5), 135),
        (Point3(130, 130, -0.5), 135),
        (Point3(100, 130, -0.5), 225),
        (Point3(100, 100, -0.5), 270),
        (Point3(100, 70, -0.5), 45),
        (Point3(130, 70, -0.5), 135),
        (Point3(65, 70, -0.5), 180),
        (Point3(30, 70, -0.5), 45),
        (Point3(2, 80, -0.5), 300),
        (Point3(0, 113, -0.5), 270),
        (Point3(8, 147, -0.5), 220),
        (Point3(40, 150, -0.5), 0),
        (Point3(40, 180, -0.5), 90),
        (Point3(40, 210, -0.5), 225),
        (Point3(75, 210, -0.5), 180),
        (Point3(110, 210, -0.5), 225),
        (Point3(145, 210, -0.5), 90)
    ]
}

BuildingBlocks = {
    FunnyFarmGlobals.RicketyRoad: range(11, 19)
}
