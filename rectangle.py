from PIL import Image
from tesserocr import PyTessBaseAPI

def zoom(title, x, y, w, h, image, dpi):
    # Single scan instance based on setRectangle
    with PyTessBaseAPI() as api:
        if dpi==600:
            x=x*2
            y=y*2
            w=w*2
            h=h*2
        api.SetImage(image)
        api.SetRectangle(x, y, w, h)
        api.Recognize()
        _ocrResult = api.GetUTF8Text()
        _conf = api.MeanTextConf()
        print (title, x, y, w, h, _ocrResult)

def scanAll(image, dpi):
    # Resolved settings for ALL scan areas
    title = "Home Team Name/Venue:"
    zoom(title, 20,800,1000,100, image, dpi)

    title = "Home Roster Stats:"
    zoom(title, 157, 949, 1000, 450, image, dpi)

    title = "Home Roster Names:"
    zoom(title, 157, 950, 600, 450, image, dpi)

    title = "Away Team Name/Venue:"
    zoom(title, 1300, 800, 1000, 100, image, dpi)

    title = "Away Roster Stats:"
    zoom(title, 1383, 949, 300, 400, image, dpi)

    title = "Away Roster Names:"
    zoom(title, 1695, 949, 600, 400, image, dpi)

## Main()
dpi = 300
if dpi == 300:
    image = Image.open("01-01-18_scoresheet300.png")
else:
    image = Image.open("01-01-18_scoresheet600.png")

# Test loop
for y in range(949,950):
    for x in range(140, 160):
        for w in range(350, 351):
            for h in range(400, 401):
                zoom("TEST:", x, y, w, h, image, dpi)

# Final Settings
scanAll(image, dpi)
