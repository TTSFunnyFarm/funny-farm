from panda3d.core import PNMImage, Filename

inputFile = raw_input("Input linear image: ")
inputFilename = Filename.fromOsSpecific(inputFile)
outputFile = raw_input("Output sRGB image: ")
outputFilename = Filename.fromOsSpecific(outputFile)

img = PNMImage()
img.read(inputFilename)
img.applyExponent(1.0/2.2)
img.write(outputFilename)

print("Done")
