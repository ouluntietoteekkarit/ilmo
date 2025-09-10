from __future__ import annotations
from typing import List, TYPE_CHECKING

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect

from config import Config
from .config import load_auth_config

if TYPE_CHECKING:
    from app.form_lib.form_module import ModuleInfo


def load_form_modules() -> List:
    forms = []
    module_names = routes.find_form_modules()
    for module_name in module_names:
        module = routes.load_module(module_name)
        forms.append(module.get_module_info())
    return forms


def register_form_module_routes(server: Flask, modules: List[ModuleInfo]) -> None:
    for module in modules:
        routes.register_module_route(server, module)


auth = HTTPBasicAuth()
csrf = CSRFProtect()
server = Flask(__name__)
Bootstrap(server)
server.config.from_object(Config)
app_context = server.app_context()
app_context.push()

db = SQLAlchemy(server)
migrate = Migrate(server, db)
(users, roles) = load_auth_config()

# MEMO: Cyclic dependency within the server package
from . import routes, config

form_modules = load_form_modules()
routes.register_index_route(server, form_modules)
register_form_module_routes(server, form_modules)
routes.register_legacy_redirects(server)

db.create_all()
db.session.commit()

if __name__ == "__main__":
    server.run(debug=True)
