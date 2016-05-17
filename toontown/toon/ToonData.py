import yaml.dist as yaml
import binascii
import ast

class ToonData(yaml.YAMLObject):
    yaml_tag = 'LocalToon'

    def __init__(self, index, dna, name, hp, maxHp, money, maxMoney, bankMoney, maxBankMoney, maxCarry, 
                inventory, experience, trackAccess, hat, glasses, backpack, shoes, nametagStyle, cheesyEffect, 
                lastHood, level, levelExp, damage, defense, accuracy):
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

    def encrypt(self):
        self.setDNA = binascii.hexlify(str(self.setDNA))
        self.setName = binascii.hexlify(self.setName)
        self.setHp = bin(self.setHp)
        self.setMaxHp = bin(self.setMaxHp)
        self.setMoney = bin(self.setMoney)
        self.setMaxMoney = bin(self.setMaxMoney)
        self.setBankMoney = bin(self.setBankMoney)
        self.setMaxBankMoney = bin(self.setMaxBankMoney)
        self.setMaxCarry = bin(self.setMaxCarry)
        self.setInventory = binascii.hexlify(str(self.setInventory))
        self.setExperience = binascii.hexlify(str(self.setExperience))
        self.setTrackAccess = binascii.hexlify(str(self.setTrackAccess))
        self.setNametagStyle = binascii.hexlify(self.setNametagStyle)
        self.setCheesyEffect = bin(self.setCheesyEffect)
        self.setLastHood = bin(self.setLastHood)
        self.setHat = binascii.hexlify(str(self.setHat))
        self.setGlasses = binascii.hexlify(str(self.setGlasses))
        self.setBackpack = binascii.hexlify(str(self.setBackpack))
        self.setShoes = binascii.hexlify(str(self.setShoes))
        self.setLevel = bin(self.setLevel)
        self.setLevelExp = bin(self.setLevelExp)
        self.setDamage = binascii.hexlify(str(self.setDamage))
        self.setDefense = binascii.hexlify(str(self.setDefense))
        self.setAccuracy = binascii.hexlify(str(self.setAccuracy))

    def decrypt(self):
        self.setDNA = ast.literal_eval(binascii.unhexlify(self.setDNA))
        self.setName = binascii.unhexlify(self.setName)
        self.setHp = int(self.setHp, 0)
        self.setMaxHp = int(self.setMaxHp, 0)
        self.setMoney = int(self.setMoney, 0)
        self.setMaxMoney = int(self.setMaxMoney, 0)
        self.setBankMoney = int(self.setBankMoney, 0)
        self.setMaxBankMoney = int(self.setMaxBankMoney, 0)
        self.setMaxCarry = int(self.setMaxCarry, 0)
        if binascii.unhexlify(self.setInventory) == 'None':
            self.setInventory = ast.literal_eval(binascii.unhexlify(self.setInventory))
        else:
            self.setInventory = binascii.unhexlify(self.setInventory)
        if binascii.unhexlify(self.setExperience) == 'None':
            self.setExperience = ast.literal_eval(binascii.unhexlify(self.setExperience))
        else:
            self.setExperience = binascii.unhexlify(self.setExperience)
        self.setTrackAccess = ast.literal_eval(binascii.unhexlify(self.setTrackAccess))
        self.setNametagStyle = binascii.unhexlify(self.setNametagStyle)
        self.setCheesyEffect = int(self.setCheesyEffect, 0)
        self.setLastHood = int(self.setLastHood, 0)
        self.setHat = ast.literal_eval(binascii.unhexlify(self.setHat))
        self.setGlasses = ast.literal_eval(binascii.unhexlify(self.setGlasses))
        self.setBackpack = ast.literal_eval(binascii.unhexlify(self.setBackpack))
        self.setShoes = ast.literal_eval(binascii.unhexlify(self.setShoes))
        self.setLevel = int(self.setLevel, 0)
        self.setLevelExp = int(self.setLevelExp, 0)
        self.setDamage = ast.literal_eval(binascii.unhexlify(self.setDamage))
        self.setDefense = ast.literal_eval(binascii.unhexlify(self.setDefense))
        self.setAccuracy = ast.literal_eval(binascii.unhexlify(self.setAccuracy))

