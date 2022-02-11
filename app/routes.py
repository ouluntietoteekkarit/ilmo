from werkzeug.security import check_password_hash
from flask import render_template, request
from . import server, auth, users, roles
from .forms.pubivisa import PubiVisaController
from .forms.korttijalautapeliilta import KorttiJaLautapeliIltaController
from .forms.fuksilauluilta import FuksiLauluIltaController
from .forms.slumberparty import SlumberPartyController
from .forms.pakohuone import PakoHuoneController
from .forms.kyselyarvontajuttu import KyselyArvontaJuttuController
from .forms.fucu import FucuController
from .forms.kmp import KmpController
from .forms.pitsakalja import PitsaKaljaController


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


@server.route('/pubivisa', methods=['GET'])
def route_get_pubivisa():
    obj = PubiVisaController()
    return obj.get_request_handler(request)


@server.route('/pubivisa', methods=['POST'])
def route_post_pubivisa():
    obj = PubiVisaController()
    return obj.post_request_handler(request)


@server.route('/pubivisa_data', methods=['GET'])
@auth.login_required(role=['admin', 'pubivisa'])
def route_pubivisa_data():
    obj = PubiVisaController()
    return obj.get_data_request_handler(request)


@server.route('/pubivisa_data/pubivisa_model_data.csv')
@auth.login_required(role=['admin', 'pubivisa'])
def route_pubivisa_csv():
    obj = PubiVisaController()
    return obj.get_data_csv_request_handler(request)


@server.route('/korttijalautapeliilta', methods=['GET'])
def route_get_korttijalautapeliilta():
    obj = KorttiJaLautapeliIltaController()
    return obj.get_request_handler(request)


@server.route('/korttijalautapeliilta', methods=['POST'])
def route_post_korttijalautapeliilta():
    obj = KorttiJaLautapeliIltaController()
    return obj.post_request_handler(request)


@server.route('/korttijalautapeliilta_data', methods=['GET'])
@auth.login_required(role=['admin', 'korttijalautapeliilta'])
def route_korttijalautapeliilta_data():
    obj = KorttiJaLautapeliIltaController()
    return obj.get_data_request_handler(request)


@server.route('/korttijalautapeliilta_data/korttijalautapeliilta_model_data.csv')
@auth.login_required(role=['admin', 'korttijalautapeliilta'])
def route_korttijalautapeliilta_csv():
    obj = KorttiJaLautapeliIltaController()
    return obj.get_data_csv_request_handler(request)


@server.route('/fuksilauluilta', methods=['GET'])
def route_get_fuksilauluilta():
    obj = FuksiLauluIltaController()
    return obj.get_request_handler(request)


@server.route('/fuksilauluilta', methods=['POST'])
def route_post_fuksilauluilta():
    obj = FuksiLauluIltaController()
    return obj.post_request_handler(request)


@server.route('/fuksilauluilta_data', methods=['GET'])
@auth.login_required(role=['admin', 'fuksilauluilta'])
def route_fuksilauluilta_data():
    obj = FuksiLauluIltaController()
    return obj.get_data_request_handler(request)


@server.route('/fuksilauluilta_data/fuksilauluilta_model_data.csv')
@auth.login_required(role=['admin', 'fuksilauluilta'])
def route_fuksilauluilta_csv():
    obj = FuksiLauluIltaController()
    return obj.get_data_csv_request_handler(request)


@server.route('/slumberparty', methods=['GET'])
def route_get_slumberparty():
    obj = SlumberPartyController()
    return obj.get_request_handler(request)


@server.route('/slumberparty', methods=['POST'])
def route_post_slumberparty():
    obj = SlumberPartyController()
    return obj.post_request_handler(request)


@server.route('/slumberparty_data', methods=['GET'])
@auth.login_required(role=['admin', 'slumberparty'])
def route_slumberparty_data():
    obj = SlumberPartyController()
    return obj.get_data_request_handler(request)


@server.route('/slumberparty_data/slumberparty_model_data.csv')
@auth.login_required(role=['admin', 'slumberparty'])
def route_slumberparty_csv():
    obj = SlumberPartyController()
    return obj.get_data_csv_request_handler(request)


@server.route('/pakohuone', methods=['GET'])
def route_get_pakohuone():
    obj = PakoHuoneController()
    return obj.get_request_handler(request)


@server.route('/pakohuone', methods=['POST'])
def route_post_pakohuone():
    obj = PakoHuoneController()
    return obj.post_request_handler(request)


@server.route('/pakohuone_data', methods=['GET'])
@auth.login_required(role=['admin', 'pakohuone'])
def route_pakohuone_data():
    obj = PakoHuoneController()
    return obj.get_data_request_handler(request)


@server.route('/pakohuone_data/pakohuone_model_data.csv')
@auth.login_required(role=['admin', 'pakohuone'])
def route_pakohuone_csv():
    obj = PakoHuoneController()
    return obj.get_data_csv_request_handler(request)


@server.route('/kysely_arvonta_juttu', methods=['GET'])
def route_get_kysely_arvonta_juttu():
    obj = KyselyArvontaJuttuController()
    return obj.get_request_handler(request)


@server.route('/kysely_arvonta_juttu', methods=['POST'])
def route_post_kysely_arvonta_juttu():
    obj = KyselyArvontaJuttuController()
    return obj.post_request_handler(request)


@server.route('/kysely_arvonta_juttu_data', methods=['GET'])
@auth.login_required(role=['admin', 'kysely_arvonta_juttu'])
def route_kysely_arvonta_juttu_data():
    obj = KyselyArvontaJuttuController()
    return obj.get_data_request_handler(request)


@server.route('/kysely_arvonta_juttu_data/kysely_arvonta_juttu_model_data.csv')
@auth.login_required(role=['admin', 'kysely_arvonta_juttu'])
def route_kysely_arvonta_juttu_csv():
    obj = KyselyArvontaJuttuController()
    return obj.get_data_csv_request_handler(request)


@server.route('/fucu', methods=['GET'])
def route_get_fucu():
    obj = FucuController()
    return obj.get_request_handler(request)


@server.route('/fucu', methods=['POST'])
def route_post_fucu():
    obj = FucuController()
    return obj.post_request_handler(request)


#@server.route('/fucu_data', methods=['GET'])
#@auth.login_required(role=['admin', 'fucu'])
def route_fucu_data():
    obj = FucuController()
    return obj.get_data_request_handler(request)

route_fucu_data = auth.login_required(role=['admin', 'fucu'])(route_fucu_data)
server.add_url_rule('/fucu_data', 'route_fucu_data', route_fucu_data)

@server.route('/fucu_data/fucu_data.csv')
@auth.login_required(role=['admin', 'fucu'])
def route_fucu_csv():
    obj = FucuController()
    return obj.get_data_csv_request_handler(request)


@server.route('/kmp', methods=['GET'])
def route_get_kmp():
    obj = KmpController()
    return obj.get_request_handler(request)


@server.route('/kmp', methods=['POST'])
def route_post_kmp():
    obj = KmpController()
    return obj.post_request_handler(request)


@server.route('/kmp_data', methods=['GET'])
@auth.login_required(role=['admin', 'kmp'])
def route_kmp_data():
    obj = KmpController()
    return obj.get_data_request_handler(request)


@server.route('/kmp_data/kmp_data.csv')
@auth.login_required(role=['admin', 'kmp'])
def route_kmp_csv():
    obj = KmpController()
    return obj.get_data_csv_request_handler(request)


@server.route('/pitsakaljasitsit', methods=['GET'])
def route_get_pitsakaljasitsit():
    obj = PitsaKaljaController()
    return obj.get_request_handler(request)


@server.route('/pitsakaljasitsit', methods=['POST'])
def route_post_pitsakaljasitsit():
    obj = PitsaKaljaController()
    return obj.post_request_handler(request)


@server.route('/pitsakaljasitsit_data', methods=['GET'])
@auth.login_required(role=['admin', 'pitsakaljasitsit'])
def route_pitsakaljasitsit_data():
    obj = PitsaKaljaController()
    return obj.get_data_request_handler(request)


@server.route('/pitsakaljasitsit_data/pitsakaljasitsit_data.csv')
@auth.login_required(role=['admin', 'pitsakaljasitsit'])
def route_pitsakaljasitsit_csv():
    obj = PitsaKaljaController()
    return obj.get_data_csv_request_handler(request)
