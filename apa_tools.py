import uuid, os, time
import locale, ghostscript
import scantools
from PIL import Image
from itertools import combinations


def unique_id():
    return hex(uuid.uuid4().time)[2:-1]


def pdf2png(pdf_input_path, dpi, output_path):
    args = ["pdf2png", # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=png16m",
            dpi,
            "-sOutputFile=" + output_path,
            pdf_input_path]
    # arguments have to be bytes, encode them
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    ghostscript.Ghostscript(*args)


def async_scan(path, filename):
    pngname = filename.rsplit('.', 1)[0] + '.png'
    txtname = filename.rsplit('.', 1)[0] + '.txt'

    convert_file = os.path.join(path, filename)
    png_file = os.path.join(path, pngname)
    txt_file = os.path.join(path, txtname)

    print("Conv Start: ", time.strftime('%X %x %Z'))
    pdf2png(convert_file, "-r300", png_file)
    print("Conv End: ", time.strftime('%X %x %Z'))

    print("Scan Start: ", time.strftime('%X %x %Z'))
    result = scantools.scan(filename, Image.open(png_file))
    print("Scan End: ", time.strftime('%X %x %Z'))

    with open(txt_file, 'w') as f:
        f.write(result)

    # TODO Write metadata file (i.e. team names, etc)


def build_combinations(roster):
    available_tonight = {}

    # Drop players that are marked as Absent for the evening
    for apa_id in roster.keys():
        if roster[apa_id]['Absent'] != 'Y':
            available_tonight[apa_id] = roster[apa_id]

    # From the available players, calculate all possible combinations
    c = combinations(available_tonight.keys(), 5)
    all_line_ups = list(c)

    # From all possible combinations calculate available combinations (SL<=23)
    available_line_ups=[]
    skill_level='SL'
    for lu in all_line_ups:
        total_sl=0
        for player in lu:
            total_sl=total_sl+int(roster[player][skill_level])
        if total_sl <= 23:
            available_line_ups.append(lu)

    # Create list of players who have already played
    matches_played=False
    match_played=[]
    for k, v in roster.items():
        if v['Played'] == 'Y':
            matches_played=True
            match_played.append(k)

    # Now eliminate combinations based on matches played
    remaining_line_ups=[]
    if matches_played:
        for available_line_up in available_line_ups:
            line_up_still_avail=True
            for player in match_played:
                if player not in available_line_up:
                    line_up_still_avail=False
            if line_up_still_avail:
                remaining_line_ups.append(available_line_up)
    else:
        remaining_line_ups=available_line_ups

    return remaining_line_ups


def mark_roster(roster, options):
    for player in roster:
        roster[player]['Option'] = 'N'

    for roster_player in roster:
        for option in options:
            for player in option:
                if roster_player == player:
                    roster[roster_player]['Option'] = 'Y'
                    break

    return roster
