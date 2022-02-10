from werkzeug.security import check_password_hash
from flask import render_template, request
from . import server, auth, users, roles
from .forms.pubivisa import pubivisa_handler, pubivisa_data, pubivisa_csv
from .forms.korttijalautapeliilta import korttijalautapeliilta_handler, korttijalautapeliilta_data, korttijalautapeliilta_csv
from .forms.fuksilauluilta import FuksiLauluIltaController
from .forms.slumberparty import slumberparty_handler, slumberparty_data, slumberparty_csv
from .forms.pakohuone import pakohuone_handler, pakohuone_data, pakohuone_csv
from .forms.kyselyarvontajuttu import kysely_arvonta_juttu_handler, kysely_arvonta_juttu_data, kysely_arvonta_juttu_csv


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@auth.get_user_roles
def get_user_roles(user):
    return roles.get(user)


@server.route('/')
def route_index():
    return render_template('index.html', title='OTY:n ilmot', page="index")


@server.route('/pubivisa', methods=['GET', 'POST'])
def route_pubivisa():
    return pubivisa_handler(request)


@server.route('/pubivisa_data', methods=['GET'])
@auth.login_required(role=['admin', 'pubivisa'])
def route_pubivisa_data():
    return pubivisa_data()


@server.route('/pubivisa_data/pubivisa_model_data.csv')
@auth.login_required(role=['admin', 'pubivisa'])
def route_pubivisa_csv():
    return pubivisa_csv()


@server.route('/korttijalautapeliilta', methods=['GET', 'POST'])
def route_korttijalautapeliilta():
    return korttijalautapeliilta_handler(request)


@server.route('/korttijalautapeliilta_data', methods=['GET'])
@auth.login_required(role=['admin', 'korttijalautapeliilta'])
def route_korttijalautapeliilta_data():
    return korttijalautapeliilta_data()


@server.route('/korttijalautapeliilta_data/korttijalautapeliilta_model_data.csv')
@auth.login_required(role=['admin', 'korttijalautapeliilta'])
def route_korttijalautapeliilta_csv():
    return korttijalautapeliilta_csv()


@server.route('/fuksilauluilta', methods=['GET'])
def route_get_fuksilauluilta():
    obj = FuksiLauluIltaController()
    return obj.get_request_handler(request)


@server.route('/fuksilauluilta', methods=['POST'])
def route_post_fuksilauluilta():
    obj = FuksiLauluIltaController()
    return obj.post_request_handler(request)


@server.route('/fuksilauluilta_data', methods=['GET'])
#@auth.login_required(role=['admin', 'fuksilauluilta'])
def route_fuksilauluilta_data():
    obj = FuksiLauluIltaController()
    return obj.get_data_request_handler(request)


@server.route('/fuksilauluilta_data/fuksilauluilta_model_data.csv')
#@auth.login_required(role=['admin', 'fuksilauluilta'])
def route_fuksilauluilta_csv():
    obj = FuksiLauluIltaController()
    return obj.get_data_csv_request_handler(request)


@server.route('/slumberparty', methods=['GET', 'POST'])
def route_slumberparty():
    return slumberparty_handler(request)


@server.route('/slumberparty_data', methods=['GET'])
@auth.login_required(role=['admin', 'slumberparty'])
def route_slumberparty_data():
    return slumberparty_data()


@server.route('/slumberparty_data/slumberparty_model_data.csv')
@auth.login_required(role=['admin', 'slumberparty'])
def route_slumberparty_csv():
    return slumberparty_csv()


@server.route('/pakohuone', methods=['GET', 'POST'])
def route_pakohuone():
    return pakohuone_handler(request)


@server.route('/pakohuone_data', methods=['GET'])
@auth.login_required(role=['admin', 'pakohuone'])
def route_pakohuone_data():
    return pakohuone_data()


@server.route('/pakohuone_data/pakohuone_model_data.csv')
@auth.login_required(role=['admin', 'pakohuone'])
def route_pakohuone_csv():
    return pakohuone_csv()


@server.route('/kysely_arvonta_juttu', methods=['GET', 'POST'])
def route_kysely_arvonta_juttu():
    return kysely_arvonta_juttu_handler(request)


@server.route('/kysely_arvonta_juttu_data', methods=['GET'])
@auth.login_required(role=['admin', 'kysely_arvonta_juttu'])
def route_kysely_arvonta_juttu_data():
    return kysely_arvonta_juttu_data()


@server.route('/kysely_arvonta_juttu_data/kysely_arvonta_juttu_model_data.csv')
@auth.login_required(role=['admin', 'kysely_arvonta_juttu'])
def route_kysely_arvonta_juttu_csv():
    return kysely_arvonta_juttu_csv()
