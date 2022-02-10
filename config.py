import os


def _make_db_uri():
    basedir = os.path.abspath(os.path.dirname(__file__))
    return os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')


class Config(object):

    SECRET_KEY = os.urandom(64)
    SQLALCHEMY_DATABASE_URI = _make_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_ENABLED = True
