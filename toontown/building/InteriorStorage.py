# Similar to storage_interior.dna in a way
# The collection of items for toon interiors
from toontown.toonbase.FunnyFarmGlobals import *
import random

ModelPath = 'phase_3.5/models/modules/'
TexturePath = 'phase_3.5/maps/'
ToonInteriors = {
    'TI_room': 'toon_interior',
    'TI_room_2': 'toon_interior_2',
    'TI_room_L': 'toon_interior_L',
    'TI_room_T': 'toon_interior_T',
    'TI_hall': 'tt_m_ara_int_toonhall'
}
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
# So, rather than using Disney's weird ass pseudorandom number generator thing
# we're just going to manually put in all the right numbers for colors/textures
# because otherwise we'd have to use the EXACT same zoneIds as Toontown (zoneIds are the seeds)
# So for instance we'd have to use 2519 for FF's gag shop to get the same style as
# the TTC gag shop. And I don't want to do that because it doesn't make sense.
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
    1515: {
        'TI_door': 1
    },
    1516: {
        'TI_door': 1
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
