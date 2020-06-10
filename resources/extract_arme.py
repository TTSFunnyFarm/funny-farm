from panda3d.core import PNMImage, Filename, PNMImageHeader

CHANNEL_AO = 0
CHANNEL_ROUGHNESS = 1
CHANNEL_METALLIC = 2
CHANNEL_EMISSIVE = 3

def getChannelName(channel):
    if channel == CHANNEL_AO:
        return "AO"
    elif channel == CHANNEL_ROUGHNESS:
        return "Roughness"
    elif channel == CHANNEL_METALLIC:
        return "Metallic"
    elif channel == CHANNEL_EMISSIVE:
        return "Emissive"

def setChannel(img, x, y, channel, val):
    if channel == CHANNEL_AO:
        img.setRed(x, y, val)
    elif channel == CHANNEL_ROUGHNESS:
        img.setGreen(x, y, val)
    elif channel == CHANNEL_METALLIC:
        img.setBlue(x, y, val)
    elif channel == CHANNEL_EMISSIVE:
        img.setAlpha(x, y, val)

def getChannel(img, x, y, channel):
    if channel == CHANNEL_AO:
        return img.getRed(x, y)
    elif channel == CHANNEL_ROUGHNESS:
        return img.getGreen(x, y)
    elif channel == CHANNEL_METALLIC:
        return img.getBlue(x, y)
    elif channel == CHANNEL_EMISSIVE:
        return img.getAlpha(x, y)

armeFile = raw_input("ARME file: ")
armeFilename = Filename.fromOsSpecific(armeFile)

img = PNMImage()
img.read(armeFilename)

for i in range(4):
    name = getChannelName(i).lower()
    print("Writing", name)
    chImg = PNMImage(img.getReadXSize(), img.getReadYSize())
    chImg.setNumChannels(1)
    chImg.setColorType(PNMImageHeader.CTGrayscale)
    for x in range(img.getReadXSize()):
        for y in range(img.getReadYSize()):
            val = getChannel(img, x, y, i)
            chImg.setXel(x, y, val)
    chImg.write(Filename(armeFilename.getFullpathWoExtension() + "_" + name + ".png"))

print("Done")
