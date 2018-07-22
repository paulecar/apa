from tesserocr import PyTessBaseAPI

pattern = (
    [3, 4, 8, 9],           # 0 normal
    [3, 4, 5, 9, 10],       # 1 three part name in team 1
    [3, 4, 8, 9, 10],       # 2 three part name in team 2
    [3, 4, 5, 9, 10, 11],   # 3 three part name in both
    [3, 7, 8],              # 4 first/last joined in team 1
    [3, 4, 8],              # 5 first/last joined in team 2
    [3, 7],                 # 6 first/last joined in both
    [3],                    # 7 first/last joined, only one team present (BYE)
    [3, 4, 5]               # 8 three part name in team 1, only one team present (BYE)
)

def IsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def listCheck(l):
    return [i for i, s in enumerate(l) if not IsInt(s)]


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
    found = False
    for idx, line in enumerate(lines):
        # print("line", idx, line)
        if "Team:"  in line:
            # print("Found Teams:", type(line), idx, line)
            splitline = line.split("Team:")
            found = True
            break
        if "Team 0"  in line:
            # print("Found Teams:", type(line), idx, line)
            splitline = line.split("Team 0")
            found = True
            break

    if found:
        teams = [t.strip() for t in splitline]
    else:
        teams = ['', "Not Found", "Not Found"]
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
            # print("Dirty line: ", dirtyline, line)
            # Start of season lists player with fees to pay, which messes with the parse
            cleanline.append([i for i in dirtyline if i not in ('*','N','$25.00','$15.00')])
    return cleanline


def splitNames(p):
    # The function is splitting a name where
    # last,first has no space (i.e. in a single column)
    clean =[]
    for col in p:
        if col.find(',') > 0:
            last, comma, first = col.partition(',')
            clean.append(last)
            clean.append(first)
        else:
            clean.append(col)
    return clean


def fixNames(players):
    cleanPlayers = []
    for pair in players:
        # print(len(pair), pair)
        pair = [i for i in pair if i not in ('', '.')]
        pair_pattern = listCheck(pair)
        # print("Pattern:", pair_pattern)
        if pair_pattern == pattern[1] or \
           pair_pattern == pattern[8]:
            # print("fixin trouble 18:", pair_pattern, pair)
            pair[3] = ''.join((pair[3] + " " + pair[4]))
            del pair[4]
        elif pair_pattern == pattern[2]:
            # print("fixin trouble 2:", pair_pattern, pair)
            pair[8] = ''.join((pair[8] + " " + pair[9]))
            del pair[9]
        elif pair_pattern == pattern[3]:
            # print("fixin trouble 3:", pair_pattern, pair)
            pair[3] = ''.join((pair[3] + " " + pair[4]))
            pair[8] = ''.join((pair[8] + " " + pair[9]))
            del pair[4]
            del pair[9]
        elif pair_pattern == pattern[4] or \
             pair_pattern == pattern[5] or \
             pair_pattern == pattern[6] or \
             pair_pattern == pattern[7]:
            # print("fixin trouble 4567:", pair_pattern, pair)
            pair = splitNames(pair)

        cleanpair = [col.rstrip(',') for col in pair]
        extraClean = [i for i in cleanpair if i not in ('', '.')]
        if listCheck(cleanpair) != pattern[0]:
            print("Trouble with cleaning pair:", pair)
        cleanPlayers.append(extraClean)
    return cleanPlayers


def createRoster(teamlists, sl, mp, id, last, first):
    roster = {}
    for row in teamlists:
        # print("Row:", row)
        # format of each entry[apaId]: (skill, match, last, first )
        try:
            roster[row[id]] = (row[sl], row[mp], row[first] + ' ' + row[last])
        except IndexError:
            print("Failure in row: ", row )
    return roster