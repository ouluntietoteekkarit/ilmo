from typing import List

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from config import Config
from .config import load_auth_config


def load_forms() -> List:
    forms = []
    module_names = routes.find_form_modules()
    for module_name in module_names:
        module = routes.load_module(module_name)
        form_info = module.get_module_info()
        routes.register_module_route(server, form_info)
        forms.append(form_info)
    return forms


auth = HTTPBasicAuth()
csrf = CSRFProtect()
server = Flask(__name__)
Bootstrap(server)
server.config.from_object(Config)

db = SQLAlchemy(server)
migrate = Migrate(server, db)
(users, roles) = load_auth_config()

# MEMO: Cyclic dependency within the server package
from . import routes, config

form_modules = load_forms()

db.create_all()
db.session.commit()

if __name__ == "__main__":
    server.run(debug=True)
