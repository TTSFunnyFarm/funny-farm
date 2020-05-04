from cryptography.fernet import Fernet
import json
import os

from direct.distributed.PyDatagram import *
from direct.distributed.PyDatagramIterator import *

from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toon.Experience import Experience
from toontown.toon.InventoryBase import InventoryBase


DB_SECRET = b'SrDlI9WqX4tsw6L4FkaYDtkCq-8fplC9q4iDsEeBrjI='

# If a Toon has broken experience values and needs to be fixed,
# set "useExpDataOverride" to True and set "expDataOverride"
# to the desired values.
useExpDataOverride = False

# Order of expDataOverride:
# [Power-Up, Trap, Lure, Sound, Throw, Squirt, Drop]
# Example: [0, 0, 0, 0, 1000, 1000, 0] - Sets Throw & Squirt to 1,000 exp; everything else is set to 0.
expDataOverride = [0, 0, 0, 0, 0, 0, 0]


def expMakeFromNetString(netString):
    dataList = []
    if type(netString) == str:
        dg = PyDatagram(netString.encode())
    else:
        dg = PyDatagram(netString)

    dgi = PyDatagramIterator(dg)
    for track in range(0, len(Tracks)):
        dataList.append(dgi.getUint16())

    return dataList


def invMakeFromNetString(netString):
    dataList = []
    if type(netString) == str:
        dg = PyDatagram(netString.encode())
    else:
        dg = PyDatagram(netString)

    dgi = PyDatagramIterator(dg)
    for track in range(0, len(Tracks)):
        subList = []
        for level in range(0, len(Levels[track])):
            if dgi.getRemainingSize() > 0:
                value = dgi.getUint8()
            else:
                value = 0
            subList.append(value)

        dataList.append(subList)

    return dataList


dbDir = 'convert'
for dbFile in os.listdir(dbDir):
    dbPath = os.path.join(dbDir, dbFile)
    toonData = None
    if os.path.exists(dbPath):
        with open(dbPath, 'r') as f:
            toonData = f.read()
            f.close()

    if toonData:
        fileData = toonData.encode()
        key, db = fileData[0:45], fileData[45:]
        fernet = Fernet(key)
        decryptedData = fernet.decrypt(db)
        jsonData = json.loads(decryptedData)

        expNetString = jsonData['setExperience']
        if useExpDataOverride:
            expData = expDataOverride
        else:
            expData = expMakeFromNetString(expNetString)

        expObj = Experience(None)
        expObj.experience = expData
        jsonData['setExperience'] = expObj.exportExperienceData()

        invNetString = jsonData['setInventory']
        invData = invMakeFromNetString(invNetString)
        invObj = InventoryBase(None)
        invObj.inventory = invData
        jsonData['setInventory'] = invObj.exportInventoryData()

        fileData = json.dumps(jsonData).encode('utf-8')
        fernet = Fernet(DB_SECRET)
        encryptedData = fernet.encrypt(fileData)
        toonDataToWrite = encryptedData

        with open(dbPath, 'wb') as f:
            f.write(toonDataToWrite)
            f.close()
