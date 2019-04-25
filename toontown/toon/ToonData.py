class ToonData:

    def __init__(self, index, dna, name, hp, maxHp, money, maxMoney, bankMoney, maxBankMoney, maxCarry,
                 inventory, experience, trackAccess, hat, glasses, backpack, shoes, nametagStyle, cheesyEffect,
                 lastHood, level, levelExp, damage, defense, accuracy, clothesTopsList, clothesBottomsList,
                 hatList, glassesList, backpackList, shoesList, quests, questHistory, questCarryLimit, questingZone,
                 trackProgress, hoodsVisited, teleportAccess, fishingRod, fishCollection, fishTank, tutorialAck):
        self.index = index
        self.setDNA = dna
        self.setName = name
        self.setHp = hp
        self.setMaxHp = maxHp
        self.setMoney = money
        self.setMaxMoney = maxMoney
        self.setBankMoney = bankMoney
        self.setMaxBankMoney = maxBankMoney
        self.setMaxCarry = maxCarry
        self.setInventory = inventory
        self.setExperience = experience
        self.setTrackAccess = trackAccess
        self.setLastHood = lastHood
        self.setHat = hat
        self.setGlasses = glasses
        self.setBackpack = backpack
        self.setShoes = shoes
        self.setNametagStyle = nametagStyle
        self.setCheesyEffect = cheesyEffect
        self.setLevel = level
        self.setLevelExp = levelExp
        self.setDamage = damage
        self.setDefense = defense
        self.setAccuracy = accuracy
        self.setClothesTopsList = clothesTopsList
        self.setClothesBottomsList = clothesBottomsList
        self.setHatList = hatList
        self.setGlassesList = glassesList
        self.setBackpackList = backpackList
        self.setShoesList = shoesList
        self.setQuests = quests
        self.setQuestHistory = questHistory
        self.setQuestCarryLimit = questCarryLimit
        self.setQuestingZone = questingZone
        self.setTrackProgress = trackProgress
        self.setHoodsVisited = hoodsVisited
        self.setTeleportAccess = teleportAccess
        self.setFishingRod = fishingRod
        self.setFishCollection = fishCollection
        self.setFishTank = fishTank
        self.setTutorialAck = tutorialAck

    def export(self):
        jsonData = self.__dict__.copy()
        for key in jsonData.keys():
            if type(jsonData[key]) == bytes:
                jsonData[key] = 'bytes-' + str(jsonData[key])

        return jsonData

    @staticmethod
    def makeFromJsonData(jsonData):
        for key in jsonData.keys():
            if type(jsonData[key]) == str and jsonData[key].startswith('bytes-'):
                jsonData[key] = jsonData[key][6:].encode()

        toonData = ToonData(jsonData.get('index'), jsonData.get('setDNA'), jsonData.get('setName'),
                            jsonData.get('setHp', 20), jsonData.get('setMaxHp', 20), jsonData.get('setMoney', 0),
                            jsonData.get('setMaxMoney', 40), jsonData.get('setBankMoney', 0),
                            jsonData.get('setMaxBankMoney', 12000), jsonData.get('setMaxCarry', 20),
                            jsonData.get('setInventory'), jsonData.get('setExperience'),
                            jsonData.get('setTrackAccess', [0, 0, 0, 0, 1, 1, 0]), jsonData.get('setLastHood', 1000),
                            jsonData.get('setHat', [0, 0, 0]), jsonData.get('setGlasses', [0, 0, 0]),
                            jsonData.get('setBackpack', [0, 0, 0]), jsonData.get('setShoes', [0, 0, 0]),
                            jsonData.get('setNametagStyle', 'Mickey'), jsonData.get('setCheesyEffect', 0),
                            jsonData.get('setLevel', 1), jsonData.get('setLevelExp', 0),
                            jsonData.get('setDamage', [0, 0, 0, 0, 0, 0]), jsonData.get('setDefense', [0, 0, 0, 0]),
                            jsonData.get('setAccuracy', [0, 0, 0, 0, 0, 0]), jsonData.get('setClothesTopsList', []),
                            jsonData.get('setClothesBottomsList', []), jsonData.get('setHatList', []),
                            jsonData.get('setGlassesList', []), jsonData.get('setBackpackList', []),
                            jsonData.get('setShoesList', []), jsonData.get('setQuests', []),
                            jsonData.get('setQuestHistory', []), jsonData.get('setQuestCarryLimit', 1),
                            jsonData.get('setQuestingZone', 1000), jsonData.get('setTrackProgress', [-1, -1]),
                            jsonData.get('setHoodsVisited', []), jsonData.get('setTeleportAccess', []),
                            jsonData.get('setFishingRod', 0), jsonData.get('setFishCollection', []),
                            jsonData.get('setFishTank', []), jsonData.get('setTutorialAck', 0))
        return toonData
