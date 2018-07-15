import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Key for form management and combat XSS/CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hilton_head_island'
    UPLOAD_FOLDER = './uploads'
    ALLOWED_EXTENSIONS = set(['pdf'])
