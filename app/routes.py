from app import app
from app.forms import UploadForm
from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request, session

import uuid
import os

def unique_id():
    return hex(uuid.uuid4().time)[2:-1]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
@app.route('/index')
def index():
    if session.get('ID'):
        flash('Using existing cookie ' + session.get('ID'))
    else:
        session['ID'] = unique_id()
        flash('Created new cookie ' + session.get('ID'))

    return render_template('index.html', title='Home')


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