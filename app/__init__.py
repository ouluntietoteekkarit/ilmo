from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from config import Config
from .config import load_auth_config


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

module_names = routes.find_form_modules()
for module_name in module_names:
    module = routes.load_module(module_name)
    routes.register_module_route(server, module)

db.create_all()
db.session.commit()

if __name__ == "__main__":
    server.run(debug=True)
