from app import app
from app.forms import UploadForm
from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request, session
from PIL import Image


import uuid
import os
import locale, ghostscript
import scantools
import time


def unique_id():
    return hex(uuid.uuid4().time)[2:-1]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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


@app.route('/')
@app.route('/index')
def index():
    if session.get('ID'):
        flash('Using existing cookie ' + session.get('ID'))
    else:
        session['ID'] = unique_id()
        flash('Created new cookie ' + session.get('ID'))

    hometeam = ()
    awayteam = ()
    homeTeamName = ""
    awayTeamName = ""

    if session.get('scan_result'):
        flash('Using existing scan result ' + session.get('ID'))
        lines = session.get('scan_result').splitlines()
        teams = scantools.findTeams(lines)
        homeTeamName = teams[0]
        awayTeamName = teams[1]

        players = scantools.findPlayers(lines)
        # for player in players:
        #    print("player :", player)

        fixedPlayers = scantools.fixNames(players)
        # for fplayer in fixedPlayers:
        #    print("fplayer: ", fplayer)

        # invertedPlayers = invertPlayers(fixedPlayers)
        # print(invertedPlayers)
        hometeam = scantools.createRoster(fixedPlayers, 0, 1, 2, 3, 4)
        # print(homeTeamName)
        # for p in hometeam.items():
        #    print("hometeam :", p)

        awayteam = scantools.createRoster(fixedPlayers, 5, 6, 7, 8, 9)
        # print(awayTeamName)
        # for p in awayteam.items():
        #    print("awayteam: ", p)

    return render_template('index.html', title='Home', teams=fixedPlayers, hometeam=hometeam, awayteam=awayteam, homename=homeTeamName, awayname=awayTeamName)


@app.route('/upload')
def upload():
    return render_template('upload.html')


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
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], session.get('ID')), exist_ok=True)
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], session.get('ID'), filename))
        flash('file uploaded successfully')
        return redirect(url_for('index'))


@app.route('/files', methods=['GET'])
def files():
    f_list = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session.get('ID')))
    return render_template('file_list.html',files=f_list,currdir=app.config['UPLOAD_FOLDER'] + "/" + session.get('ID'))


@app.route('/convert/<filename>', methods=['GET'])
def convert(filename):
    convert_file = os.path.join(app.config['UPLOAD_FOLDER'], session.get('ID'), filename)
    newname = filename.rsplit('.', 1)[0] + '.png'
    png_file = os.path.join(app.config['UPLOAD_FOLDER'], session.get('ID'), newname)

    print("Conv Start: ", time.strftime('%X %x %Z'))
    pdf2png(convert_file, "-r300", png_file)
    print("Conv End: ", time.strftime('%X %x %Z'))

    f_list = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session.get('ID')))
    return render_template('file_list.html',files=f_list,currdir=app.config['UPLOAD_FOLDER'] + "/" + session.get('ID'))


@app.route('/scanpng/<filename>', methods=['GET'])
def scanpng(filename):
    scan_file = os.path.join(app.config['UPLOAD_FOLDER'], session.get('ID'), filename)

    print("Scan Start: ", time.strftime('%X %x %Z'))
    result = scantools.scan(filename, Image.open(scan_file))
    print("Scan End: ", time.strftime('%X %x %Z'))

    flash('Scanners:')
    flash(result)

    session['scan_result'] = result

    return redirect(url_for('index'))
