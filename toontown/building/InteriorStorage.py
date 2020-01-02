# Similar to storage_interior.dna in a way
# The collection of items for toon interiors
from toontown.toonbase.FunnyFarmGlobals import *

ModelPath = 'phase_3.5/models/modules/'
TexturePath = 'phase_3.5/maps/'
ToonInteriors = [
    'toon_interior',
    'toon_interior_2',
    'toon_interior_L',
    'toon_interior_T'
]
ModelDict = {
    'TI_paper_trashcan': 'paper_trashcan',
    'TI_big_planter': 'big_planter',
    'TI_bookcase': 'bookcase',
    'TI_bookcase_low': 'bookcase_low',
    'TI_chair': 'chair',
    'TI_coatrack': 'coatrack',
    'TI_counter': 'counter',
    'TI_counterShort': 'counterShort',
    'TI_desk': 'desk',
    'TI_desk_only': 'desk_only',
    'TI_desk_only_wo_phone': 'desk_only_wo_phone',
    'TI_int_door': 'int_door',
    'TI_lamp_short': 'lamp_short',
    'TI_lamp_tall': 'lamp_tall',
    'TI_rug': 'rug',
    'TI_tie_rack': 'tie_rack',
    'TI_umbrella_stand': 'umbrella_stand',
    'TI_couch_1person': 'couch_1person',
    'TI_couch_2person': 'couch_2person',
    'TI_ending_table': 'ending_table'
}
TextureDict = {
    'TI_wallpaper': ['stripeB5'],
    'TI_wallpaper_border': ['stripeB5'],
    'TI_wainscotting': ['wall_paper_b3', 'wall_paper_b4'],
    'TI_floor': ['floor_create_toon', 'carpet'],
    'TI_molding': ['molding_wood1', 'molding_wood2'],
    'TI_couch': ['couch', 'couch2', 'couch3']
}
# This table is for interiors that we want to have specific colors & textures,
# in other words, we know exactly what we want them to look like.
ZoneStyles = {
    1510: {
        'TI_wallpaper': (0, 3),
        'TI_wallpaper_border': (0, 3),
        'TI_wainscotting': (1, 0),
        'TI_door': 1
    },
    1512: {
        'TI_door': 1
    },
    1514: {
        'TI_door': 1
    },
    1610: {
        'TI_door': 1
    },
    1618: {
        'TI_wallpaper': (0, 0),
        'TI_wallpaper_border': (0, 0),
        'TI_wainscotting': (0, 2),
        'TI_floor': (0, 1),
        'TI_molding': (1,),
        'TI_couch': (0,)
    },
    2510: {
        'TI_wallpaper': (0, 1),
        'TI_wallpaper_border': (0, 1),
        'TI_wainscotting': (0, 1)
    }
}

def findNode(category):
    modelName = ModelDict[category]
    np = loader.loadModel(ModelPath + modelName)
    return np

def findTexture(category, zoneId):
    style = ZoneStyles[zoneId][category]
    name = TextureDict[category][style[0]]
    if name == 'floor_create_toon':
        texture = loader.loadTexture('phase_3/maps/' + name + '.jpg')
    else:
        texture = loader.loadTexture(TexturePath + name + '.jpg')
    return texture

def findRandomTexture(category, randGen):
    name = randGen.choice(TextureDict[category])
    if name == 'floor_create_toon':
        texture = loader.loadTexture('phase_3/maps/' + name + '.jpg')
    else:
        texture = loader.loadTexture(TexturePath + name + '.jpg')
    return texture
