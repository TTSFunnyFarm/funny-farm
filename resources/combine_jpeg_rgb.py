from panda3d.core import Filename, PNMImage

jpgFile = raw_input("JPEG file: ")
aFile = raw_input("Alpha file: ")

fn = Filename.fromOsSpecific(jpgFile)
fnrgb = Filename.fromOsSpecific(aFile)

fnout = Filename(fn.getFullpathWoExtension() + ".png")
image = PNMImage(fn)

imagergb = PNMImage(fnrgb)
image.set_num_channels(4)
for x in range(image.get_x_size()):
    for y in range(image.get_y_size()):
        image.set_channel(x, y, 3, imagergb.getChannel(x, y, 0))
image.write(fnout)
