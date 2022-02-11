from typing import List, Any
from types import ModuleType
from os.path import dirname, basename, isfile, join
from werkzeug.security import check_password_hash
from flask import render_template, request, Flask
import importlib.util

from . import server, auth, users, roles
from .forms.forms_util.form_module import FormModule


def _find_modules(folder:str, package: str) -> List[str]:
    from glob import glob
    pattern = join(folder, package.strip('.'), "*.py")
    modules = []
    for module in glob(pattern):
        if isfile(module) and module.find('__init__') == -1:
            modules.append(".".join([package, basename(module)[:-3]]))

    return modules


def find_form_modules():
    return _find_modules(dirname(__file__), ".forms")


def load_module(module_name: str) -> ModuleType:
    module_name = module_name.strip()
    package = None
    if module_name[0] == '.':
        package = __package__

    return importlib.import_module(module_name, package)


def register_module_route(server: Flask, form_info: FormModule):
    if not form_info.is_active():
        return

    controller = form_info.get_controller_type()
    form_name = form_info.get_form_name()

    def get_form_index() -> Any:
        return controller().get_request_handler(request)

    def post_form_index() -> Any:
        return controller().post_request_handler(request)

    def get_form_data() -> Any:
        return controller().get_data_request_handler(request)
    get_form_data = auth.login_required(role=['admin', form_name])(get_form_data)

    def get_form_data_csv() -> Any:
        return controller().get_data_csv_request_handler(request)
    get_form_data_csv = auth.login_required(role=['admin', form_name])(get_form_data_csv)

    index_url_path = '/{}'.format(form_name)
    data_url_path = '/{}/data'.format(form_name)
    data_csv_url_path = '/{}/data/{}.csv'.format(form_name, form_name)

    index_get_endpoint = 'route_get_{}'.format(form_name)
    index_post_endpoint = 'route_post_{}'.format(form_name)
    data_get_endpoint = 'route_get_{}_data'.format(form_name)
    data_get_csv_endpoint = 'route_get_{}_data_csv'.format(form_name)

    server.add_url_rule(index_url_path, index_get_endpoint, get_form_index, methods=['GET'])
    server.add_url_rule(index_url_path, index_post_endpoint, post_form_index, methods=['POST'])
    server.add_url_rule(data_url_path, data_get_endpoint, get_form_data)
    server.add_url_rule(data_csv_url_path, data_get_csv_endpoint, get_form_data_csv)


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@auth.get_user_roles
def get_user_roles(user):
    return roles.get(user)


@server.route('/')
def route_index():
    return render_template('index.html', title='OTiTin ilmot', page="index")
