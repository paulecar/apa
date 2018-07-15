from app import app
from app.forms import UploadForm
from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request, session

import uuid

def unique_id():
    return hex(uuid.uuid4().time)[2:-1]

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
        f = request.files['file']
        f.save(secure_filename(f.filename))
        flash('file uploaded successfully')
        return redirect(url_for('index'))

