import os
from pathlib import Path


def _load_secret_key():
    filename = os.environ.get('ILMO_SECRET_KEY_FILE')
    if not filename:
        return os.urandom(64)

    key = Path(filename).read_text(encoding='utf-8').strip()
    if len(key) < 32:
        raise ValueError('The Flask secret key file must contain at least 32 characters')
    return key


def _make_db_uri():
    basedir = os.path.abspath(os.path.dirname(__file__))
    return os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')


class Config(object):

    SECRET_KEY = _load_secret_key()
    SQLALCHEMY_DATABASE_URI = _make_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_ENABLED = True
    TEMPLATES_AUTO_RELOAD = True
    BOOTSTRAP_FORM_GROUP_CLASSES = "my-1"
