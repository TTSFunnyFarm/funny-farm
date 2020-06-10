from panda3d.core import PNMImage, Filename, PNMImageHeader

import math

CHANNEL_AO = 0
CHANNEL_ROUGHNESS = 1
CHANNEL_METALLIC = 2
CHANNEL_EMISSIVE = 3

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

def getChannelName(channel):
    if channel == CHANNEL_AO:
        return "AO"
    elif channel == CHANNEL_ROUGHNESS:
        return "Roughness"
    elif channel == CHANNEL_METALLIC:
        return "Metallic"
    elif channel == CHANNEL_EMISSIVE:
        return "Emissive"

ao = Filename(raw_input("AO Image: "))
ao_srgb = bool(int(raw_input("sRGB (Edited in image program)? [1/0]: ")))
roughness = Filename(raw_input("Roughness Image: "))
roughness_srgb = bool(int(raw_input("sRGB (Edited in image program)? [1/0]: ")))
metallic = Filename(raw_input("Metallic Image: "))
metallic_srgb = bool(int(raw_input("sRGB (Edited in image program)? [1/0]: ")))
emissive = Filename(raw_input("Emissive Image: "))
emissive_srgb = bool(int(raw_input("sRGB (Edited in image program)? [1/0]: ")))

size = [1024, 1024]

fImgs = [[ao, ao_srgb], [roughness, roughness_srgb], [metallic, metallic_srgb], [emissive, emissive_srgb]]
imgs = {}

foundSize = False

for i in range(len(fImgs)):
    fImg, is_sRGB = fImgs[i]
    if fImg.exists():
        img = PNMImage()
        img.read(fImg)
        img.makeRgb()
        if is_sRGB:
            # Convert to linear
            print("Converting", getChannelName(i), "to linear")
            img.applyExponent(2.2)
        if not foundSize:
            size = [img.getReadXSize(), img.getReadYSize()]
            foundSize = True
        imgs[i] = img
    else:
        # assume it is a constant value
        val = float(fImg.getFullpath())
        if is_sRGB:
            print("Converting", getChannelName(i), "to linear")
            # Convert to linear
            val = math.pow(val, 2.2)
        imgs[i] = val

print("Size:", size)

output = PNMImage(*size)
output.setNumChannels(4)
output.setColorType(PNMImageHeader.CTFourChannel)
output.fill(1.0, 0.0, 0.0)
output.alphaFill(1.0)

for channel, img in imgs.items():
    img
    print("Filling in", getChannelName(channel), "channel...")
    if isinstance(img, float):
        print("Value", img)
    for x in range(size[0]):
        for y in range(size[1]):
            if isinstance(img, float):
                setChannel(output, x, y, channel, img)
            else:
                setChannel(output, x, y, channel, getChannel(img, x, y, 0))

outputFile = Filename(raw_input("Output image: "))
output.write(outputFile)
