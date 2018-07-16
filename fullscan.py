import time
from PIL import Image
from tesserocr import PyTessBaseAPI

def scan(title, image):
    # Single scan instance based on setRectangle
    with PyTessBaseAPI() as api:
        api.SetImage(image)
        api.Recognize()
        _ocrResult = api.GetUTF8Text()
        _conf = api.MeanTextConf()
        print (title, _ocrResult)
        return _ocrResult

def scanAll():
    # Resolved settings for ALL scan areas
    uSheet1 = scan("01-18-2018 300DPI", Image.open("01-08-2018_scoresheet300.png"))
    print("End 1: ", time.strftime('%X %x %Z'))
    uSheet1 = scan("01-18-2018 600DPI", Image.open("01-08-2018_scoresheet600.png"))
    print("End 2: ", time.strftime('%X %x %Z'))
    uSheet2 = scan("12-18-2017 300DPI", Image.open("12-18-2017_scoresheet300.png"))
    print("End 3: ", time.strftime('%X %x %Z'))
    uSheet2 = scan("12-18-2017 600DPI", Image.open("12-18-2017_scoresheet600.png"))
    print("End 4: ", time.strftime('%X %x %Z'))
    uSheet3 = scan("08-14-2017 300DPI", Image.open("08-14-2017_scoresheet300.png"))
    print("End 5: ", time.strftime('%X %x %Z'))
    uSheet3 = scan("08-14-2017 600DPI", Image.open("08-14-2017_scoresheet600.png"))


# Test Multiple sheets and resolutions
print("Starting Time: ", time.strftime('%X %x %Z'))
scanAll()
print("All Done: ", time.strftime('%X %x %Z'))

