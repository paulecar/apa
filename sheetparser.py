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
        # print (title, _ocrResult)
        return _ocrResult


def findTeams(lines):
    for idx, line in enumerate(lines):
        if "Home Team" in line:
            print("might work:", idx)
        if "Team:" in line:
            print("Found Teams:", type(line), idx, line)
            break
    splitline = line.split("Team:")
    teams = [t.strip() for t in splitline]
    return teams[1], teams[2]


def findPlayers(lines):
    start = len(lines)
    stop = len(lines)
    cleanline = []
    for idx, line in enumerate(lines):
        if "SL MP" in line:
            start = idx
            stop = idx + 9
            # print("Found Players:", idx, start, stop, line)
        if idx==stop:
            break
        if idx > start:
            dirtyline = line.split()
            # Start of season lists player with fees to pay, which messes with the parse
            cleanline.append([i for i in dirtyline if i not in ('*','N','$25.00','$15.00')])
    return cleanline

def invertPlayers(pairs):
    invertedlist = list(map(list, zip(*pairs)))
    return invertedlist


def fixNames(players):
    cleanPlayers = []
    for pair in players:
        # 10 means wehave complete row with two players
        print(len(pair), pair)
        if len(pair) == 10:
            cleanPlayers.append([col.rstrip(',') for col in pair])
        # Less than 10 then we assume one column has "last,first' concat'ed
        if len(pair) < 10:
            cleanPair = []
            for col in pair:
                if col.find(',') > 0:
                    last, comma, first = col.partition(',')
                    cleanPair.append(last)
                    cleanPair.append(first)
                else:
                    cleanPair.append(col)
            # Extra check to remove blank columns
            extraClean = [i for i in cleanPair if i not in ('')]
            cleanPlayers.append(extraClean)
    return cleanPlayers


def createRoster(teamlists, sl, mp, id, last, first):
    roster = {}
    for row in teamlists:
        # print("Row:", row)
        # entry[apaId]: (skill, match, last, first )
        try:
            roster[row[id]] = (row[sl], row[mp], row[first], row[last])
        except IndexError:
            print("Failure in row: ", row )
    return roster


print("Start: ", time.strftime('%X %x %Z'))

ocrOutput = scan("File", Image.open("02-04-2018_scoresheet300.png"))
# ocrOutput = scan("File", Image.open("01-08-2018_scoresheet300.png"))
lines = ocrOutput.splitlines()
print("Scanned: ", time.strftime('%X %x %Z'))

teams = findTeams(lines)
homeTeamName = teams[0]
awayTeamName = teams[1]
print("teams: ", teams)

players = findPlayers(lines)
for player in players:
   print("player :", player)

fixedPlayers = fixNames(players)
for fplayer in fixedPlayers:
   print("fplayer: ", fplayer)

# invertedPlayers = invertPlayers(fixedPlayers)
# print(invertedPlayers)
homeTeam = createRoster(fixedPlayers,0,1,2,3,4)
print(homeTeamName)
for p in homeTeam.items():
    print("hometeam :", p)

awayTeam = createRoster(fixedPlayers,5,6,7,8,9)
print(awayTeamName)
for p in awayTeam.items():
    print("awayteam: ", p)

print("Done: ", time.strftime('%X %x %Z'))