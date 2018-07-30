from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets import FileInput
from wtforms.validators import DataRequired, ValidationError, InputRequired, Required, EqualTo

class UploadForm(FlaskForm):
    filename = FileInput('File')
    submit = SubmitField('Upload')

class Manage(FlaskForm):
    submit = SubmitField('Apply Flags')
