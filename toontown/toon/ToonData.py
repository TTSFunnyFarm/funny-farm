import yaml.dist as yaml
import binascii

class ToonData(yaml.YAMLObject):
    yaml_tag = 'LocalToon'

    def __init__(self, index, dna, name, hp, maxHp, money, maxMoney, bankMoney, maxBankMoney, hat, glasses, backpack, shoes, nametagStyle, cheesyEffect, lastHood):
        self.index = index
        self.setDNA = dna
        self.setName = name
        self.setHp = hp
        self.setMaxHp = maxHp
        self.setMoney = money
        self.setMaxMoney = maxMoney
        self.setBankMoney = bankMoney
        self.setMaxBankMoney = maxBankMoney
        self.setLastHood = lastHood
        self.setHat = hat
        self.setGlasses = glasses
        self.setBackpack = backpack
        self.setShoes = shoes
        self.setNametagStyle = nametagStyle
        self.setCheesyEffect = cheesyEffect

    def encrypt(self):
        # To encrypt the data we're turning everything into a combination of hexadecimals and binary numbers.
        self.setDNA = binascii.hexlify(str(self.setDNA))
        self.setName = binascii.hexlify(self.setName)
        self.setHp = bin(self.setHp)
        self.setMaxHp = bin(self.setMaxHp)
        self.setMoney = bin(self.setMoney)
        self.setMaxMoney = bin(self.setMaxMoney)
        self.setBankMoney = bin(self.setBankMoney)
        self.setMaxBankMoney = bin(self.setMaxBankMoney)
        self.setNametagStyle = binascii.hexlify(self.setNametagStyle)
        self.setCheesyEffect = bin(self.setCheesyEffect)
        self.setLastHood = bin(self.setLastHood)
        self.setHat = binascii.hexlify(str(self.setHat))
        self.setGlasses = binascii.hexlify(str(self.setGlasses))
        self.setBackpack = binascii.hexlify(str(self.setBackpack))
        self.setShoes = binascii.hexlify(str(self.setShoes))

    def decrypt(self):
        # And now we do the opposite!
        import ast
        self.setDNA = ast.literal_eval(binascii.unhexlify(self.setDNA))
        self.setName = binascii.unhexlify(self.setName)
        self.setHp = int(self.setHp, 0)
        self.setMaxHp = int(self.setMaxHp, 0)
        self.setMoney = int(self.setMoney, 0)
        self.setMaxMoney = int(self.setMaxMoney, 0)
        self.setBankMoney = int(self.setBankMoney, 0)
        self.setMaxBankMoney = int(self.setMaxBankMoney, 0)
        self.setNametagStyle = binascii.unhexlify(self.setNametagStyle)
        self.setCheesyEffect = int(self.setCheesyEffect, 0)
        self.setLastHood = int(self.setLastHood, 0)
        self.setHat = ast.literal_eval(binascii.unhexlify(self.setHat))
        self.setGlasses = ast.literal_eval(binascii.unhexlify(self.setGlasses))
        self.setBackpack = ast.literal_eval(binascii.unhexlify(self.setBackpack))
        self.setShoes = ast.literal_eval(binascii.unhexlify(self.setShoes))
