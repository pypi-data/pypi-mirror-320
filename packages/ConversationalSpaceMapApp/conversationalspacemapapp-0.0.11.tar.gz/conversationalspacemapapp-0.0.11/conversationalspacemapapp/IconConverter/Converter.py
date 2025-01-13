import icnsutil

# Load the PNG file
file = "./assets/conversationalspacemapapp.png"
output = ""

# compose
img = icnsutil.IcnsFile()
img.add_media(file=file)
img.write("./assets/conversationalspacemapapp.icns")
