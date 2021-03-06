from app import app
from app.forms import UploadForm, Manage
from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request, make_response
from PIL import Image
from threading import Thread
from apa_tools import unique_id, pdf2png, async_scan, build_combinations, mark_roster
from collections import OrderedDict


import os, scantools, json, time, datetime


# Cookie expiration date
expire_date = datetime.datetime.now()
expire_date = expire_date + datetime.timedelta(days=90)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# TODO Add consitency to how I set and display the page title
@app.route('/')
@app.route('/index')
def index():

    # Load data from cookies or set None values to render page
    if request.cookies.get('teams'):
        teams = json.loads(request.cookies.get('teams'))
    else:
        teams = []

    if request.cookies.get('home_name'):
        homeTeamName = request.cookies.get('home_name')
    else:
        homeTeamName = "Not Set"

    if request.cookies.get('away_name'):
        awayTeamName = request.cookies.get('away_name')
    else:
        awayTeamName = "Not Set"

    if request.cookies.get('current_form'):
        current_form = request.cookies.get('current_form')
    else:
        current_form = "No Form Loaded"

    # Create response object so we can set cookie values
    resp = make_response(render_template('index.html', title='Home',
                                         teams=teams,
                                         homename=homeTeamName,
                                         awayname=awayTeamName,
                                         current_form = current_form))

    if not request.cookies.get('ID'):
        # Create a cookie ID, which is used to create a separate folder on the server for documents
        flash('Created new session ID')
        resp.set_cookie('ID', unique_id(), expires=expire_date)

    return resp


@app.route('/upload')
def upload():
    form=UploadForm()
    return render_template('upload.html', title='Upload PDF', form=form)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('index'))

        f = request.files['file']

        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(f.filename):
            flash('Invalid file type')
            return redirect(url_for('index'))

        # Valid file type uploaded to directory that matches the users cookie ID value (uuid)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID')), exist_ok=True)
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID'), filename))
        flash('File uploaded successfully')

        # Start backgound conversion and scan process
        path=os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID'))
        Thread(target=async_scan, args=(path, filename)).start()
        return redirect(url_for('files'))


@app.route('/files', methods=['GET'])
def files():
    f_dict={}
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID'))
    if os.path.exists(upload_path):
        f_list = os.listdir(upload_path)
        f_list.sort()

        # Priming the keys
        for f in f_list:
            f_dict[f.rsplit('.', 1)[0]]={}

        # Loading the available files per key
        for f in f_list:
            f_dict[f.rsplit('.', 1)[0]][f.rsplit('.', 1)[1]] = f

    return render_template('file_list.html', files=f_dict, currdir=app.config['UPLOAD_FOLDER'] + "/" + request.cookies.get('ID'))


@app.route('/convert/<filename>', methods=['GET'])
def convert(filename):
    convert_file = os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID'), filename)
    newname = filename.rsplit('.', 1)[0] + '.png'
    png_file = os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID'), newname)

    pdf2png(convert_file, "-r300", png_file)

    return redirect(url_for('files'))


@app.route('/scanpng/<filename>', methods=['GET'])
def scanpng(filename):
    scan_file = os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID'), filename)

    result = scantools.scan(filename, Image.open(scan_file))

    newname = os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID'), filename.rsplit('.', 1)[0] + '.txt')

    with open(newname, 'w') as f:
        f.write(result)

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('scan_result', result, expires=expire_date)
    resp.set_cookie('current_form', filename.rsplit('.', 1)[0], expires=expire_date)

    return resp


@app.route('/loadtxt/<filename>', methods=['GET'])
def loadtxt(filename):
    file = os.path.join(app.config['UPLOAD_FOLDER'], request.cookies.get('ID'), filename)

    with open(file, 'r') as f:
        result = f.read()

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('scan_result', result, expires=expire_date)
    resp.set_cookie('current_form', filename.rsplit('.', 1)[0], expires=expire_date)

    lines = result.splitlines()
    teams = scantools.findTeams(lines)
    homeTeamName = teams[0]
    awayTeamName = teams[1]

    players = scantools.findPlayers(lines)
    fixedPlayers = scantools.fixNames(players)
    hometeam = scantools.createRoster(fixedPlayers, 0, 1, 2, 3, 4)
    awayteam = scantools.createRoster(fixedPlayers, 5, 6, 7, 8, 9)
    if len(awayteam) == 0:
        if "bye" in homeTeamName.lower():
            t = homeTeamName
            homeTeamName = awayTeamName
            awayTeamName = t

    # Store results of the parsing into the cookie
    resp.set_cookie('teams', json.dumps(fixedPlayers), expires=expire_date)
    resp.set_cookie('home_roster', json.dumps(hometeam), expires=expire_date)
    resp.set_cookie('away_roster', json.dumps(awayteam), expires=expire_date)
    resp.set_cookie('home_name', homeTeamName, expires=expire_date)
    resp.set_cookie('away_name', awayTeamName, expires=expire_date)

    flash('Scan result loaded')

    return resp


@app.route('/lineups/<roster>', methods=['GET'])
def lineups(roster):

    # Load rosters from cookies
    if roster == "home":
        avail_lineups = json.loads(request.cookies.get('home_options'))
        roster = json.loads(request.cookies.get('home_roster'))
        team_name = request.cookies.get('home_name')
    else:
        avail_lineups = json.loads(request.cookies.get('away_options'))
        roster = json.loads(request.cookies.get('away_roster'))
        team_name = request.cookies.get('away_name')

    return render_template('lineups.html', available=avail_lineups, roster=roster, team=team_name)


@app.route('/manage', methods=['GET', 'POST'])
def manage():
    form=Manage()

    # Load rosters from cookies
    ht = json.loads(request.cookies.get('home_roster'))
    at = json.loads(request.cookies.get('away_roster'))
    htn = request.cookies.get('home_name')
    atn = request.cookies.get('away_name')

    # POST action - apply check box status to cookies
    if request.method == 'POST':
        # Set absent flag and played flag in home roster
        for k, v in ht.items():
            sl = request.form.getlist('h_sl_' + k)
            if sl == ['3']:
                ht[k]['SL'] = '3'
            if sl == ['4']:
                ht[k]['SL'] = '4'

            if k in request.form.getlist('h_absent'):
                ht[k]['Absent'] = 'Y'
            else:
                ht[k]['Absent'] = 'N'
            if k in request.form.getlist('h_played'):
                ht[k]['Played'] = 'Y'
            else:
                ht[k]['Played'] = 'N'

        # Set absent flag and played flag in away roster
        for k, v in at.items():
            sl = request.form.getlist('a_sl_' + k)
            if sl == ['3']:
                at[k]['SL'] = '3'
            if sl == ['4']:
                at[k]['SL'] = '4'

            if k in request.form.getlist('a_absent'):
                at[k]['Absent'] = 'Y'
            else:
                at[k]['Absent'] = 'N'
            if k in request.form.getlist('a_played'):
                at[k]['Played'] = 'Y'
            else:
                at[k]['Played'] = 'N'

    ht_options = build_combinations(ht)
    at_options = build_combinations(at)

    ht=mark_roster(ht, ht_options)
    at=mark_roster(at, at_options)

    resp = make_response(render_template('manage.html', title='Manage Roster', form=form,
                                         ht_option_count=len(ht_options),
                                         at_option_count=len(at_options),
                                         hometeam=OrderedDict(sorted(ht.items())),
                                         awayteam=OrderedDict(sorted(at.items())),
                                         homename=htn,
                                         awayname=atn))

    resp.set_cookie('home_roster', json.dumps(ht), expires=expire_date)
    resp.set_cookie('away_roster', json.dumps(at), expires=expire_date)
    resp.set_cookie('home_options', json.dumps(ht_options), expires=expire_date)
    resp.set_cookie('away_options', json.dumps(at_options), expires=expire_date)


    return resp
