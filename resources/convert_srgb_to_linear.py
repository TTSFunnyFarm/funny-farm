from panda3d.core import PNMImage, Filename

inputFile = raw_input("Input sRGB image: ")
inputFilename = Filename.fromOsSpecific(inputFile)
outputFile = raw_input("Output linear image: ")
outputFilename = Filename.fromOsSpecific(outputFile)

img = PNMImage()
img.read(inputFilename)
img.applyExponent(2.2)
img.write(outputFilename)

print("Done")
