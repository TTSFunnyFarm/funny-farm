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

    def makeJsonData(self):
        jsonData = self.__dict__.copy()
        return jsonData

    @staticmethod
    def verifyToonData(toonData):
        # This is the default data for new Toon objects.
        # Layout goes like this: [field, type, defaultValue]
        # We include the type for the purpose of sanity checking.
        DefaultData = [
            # [field, type, defaultValue]
            ['index', int, None],
            ['setDNA', list, None],
            ['setName', str, None],
            ['setHp', int, 20],
            ['setMaxHp', int, 20],
            ['setMoney', int, 0],
            ['setMaxMoney', int, 40],
            ['setBankMoney', int, 0],
            ['setMaxBankMoney', int, 12000],
            ['setMaxCarry', int, 20],
            ['setInventory', str, None],
            ['setExperience', str, None],
            ['setTrackAccess', list, [0, 0, 0, 0, 1, 1, 0]],
            ['setHat', list, [0, 0, 0]],
            ['setGlasses', list, [0, 0, 0]],
            ['setBackpack', list, [0, 0, 0]],
            ['setShoes', list, [0, 0, 0]],
            ['setNametagStyle', str, 'Mickey'],
            ['setCheesyEffect', int, 0],
            ['setLastHood', int, 1000],
            ['setLevel', int, 1],
            ['setLevelExp', int, 0],
            ['setDamage', list, [0, 0, 0, 0, 0, 0]],
            ['setDefense', list, [0, 0, 0, 0]],
            ['setAccuracy', list, [0, 0, 0, 0, 0, 0]],
            ['setClothesTopsList', list, []],
            ['setClothesBottomsList', list, []],
            ['setHatList', list, []],
            ['setGlassesList', list, []],
            ['setBackpackList', list, []],
            ['setShoesList', list, []],
            ['setQuests', list, []],
            ['setQuestHistory', list, []],
            ['setQuestCarryLimit', int, 1],
            ['setQuestingZone', int, 1000],
            ['setTrackProgress', list, [-1, -1]],
            ['setHoodsVisited', list, []],
            ['setTeleportAccess', list, []],
            ['setFishingRod', int, 0],
            ['setFishCollection', list, []],
            ['setFishTank', list, []],
            ['setTutorialAck', int, 0]
        ]

        # If this is an instance of ToonData, we need to convert it into a
        # dict in order to perform any verification on it. Otherwise we
        # assume it is a dict that has been loaded from a JSON object.
        if isinstance(toonData, ToonData):
            toonData = toonData.__dict__.copy()

        # And if it's not a dict, well, we cannot move forward, so check that:
        if not isinstance(toonData, dict):
            # sad!
            return False, 'toonData is not a dictionary!'

        # index, setDNA, and setName are **absolutely** required.
        # There are no default values for these, for obvious reasons, so if
        # they don't exist within the toonData, we will need to stop right
        # there & throw an error; we cannot possibly continue on without them.
        index = toonData.get('index')
        setDNA = toonData.get('setDNA')
        setName = toonData.get('setName')
        if index is None or setDNA is None or setName is None:
            return False, 'One or more required database fields are missing!'

        if type(index) != int and type(setDNA) != list and type(setName) != str:
            return False, 'One or more required database fields contain a value of incorrect type!'

        return True, ''

    @staticmethod
    def makeFromJsonData(jsonData):
        valid, response = ToonData.verifyToonData(jsonData)
        if not valid:
            raise Exception(response)

        toonData = ToonData(index, dna, name, 20, 20, 0, 40, 0, 12000, 20, None, None, [0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], 'Mickey', 0, 1000, 1, 0,
                            [0, 0, 0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [], [], [], [], [], [],
                            [], [], 1, 1000, [-1, -1], [], [], 0, [], [], 0)
        return toonData
