from wtforms.validators import InputRequired
from datetime import datetime
from typing import List

from app import db
from app.email import EmailRecipient, make_greet_line
from .forms_util.form_controller import FormController, DataTableInfo, Event, Quota
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import make_field_phone_number, make_field_departure_location, \
    make_field_name_consent, get_str_choices, get_quota_choices, FormBuilder, make_field_quota, \
    make_field_privacy_consent, make_field_required_participants, make_default_participant_form
from .forms_util.models import BasicModel, basic_model_csv_map, departure_location_csv_map, phone_number_csv_map

_form_name = file_path_to_form_name(__file__)

_PARTICIPANT_FUKSI = 'Fuksi'
_PARTICIPANT_PRO = 'Pro'
_PARTICIPANT_BOARD_MEMBER = 'Hallitus'
_PARTICIPANT_OTHER = 'Muu'

_DEPARTURE_BUS_STOP_UNI = 'Yliopisto'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Merikoskenkatu (tuiran bussipysäkki)'
_DEPARTURE_BUS_STATION = 'Linja-autoasema'


def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]


def _get_quotas() -> List[Quota]:
    return [
        Quota(_PARTICIPANT_FUKSI, 15, 5),
        Quota(_PARTICIPANT_PRO, 15, 5),
        Quota(_PARTICIPANT_BOARD_MEMBER, 15, 5),
        Quota(_PARTICIPANT_OTHER, 15, 5)
    ]


_Participant = make_default_participant_form()
_Form = FormBuilder().add_fields([
    make_field_required_participants(_Participant),
    make_field_phone_number([InputRequired()]),
    make_field_departure_location(get_str_choices(_get_departure_stops()), [InputRequired()]),
    make_field_quota('Kiintiö *', get_quota_choices(_get_quotas()), [InputRequired()]),
    make_field_name_consent(),
    make_field_privacy_consent()
]).build()


class _Model(BasicModel): #, PhoneNumberColumn, DepartureBusstopColumn):
    __tablename__ = _form_name
    kiintio = db.Column(db.String(32))


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = model.get_email()
        phone_number = model.get_phone_number()
        departure_location = model.get_departure_location()
        quota = model.kiintio
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Fuksicursiolle. Olet varasijalla.",
                "Jos fuculle jää peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Fuksicursiolle. Tässä vielä syöttämäsi tiedot: ",
                "\n\nNimi: ", firstname, " ", lastname,
                "\nSähköposti: ", email, "\nPuhelinnumero: ", phone_number,
                "\nLähtöpaikka: ", departure_location, "\nKiintiö: ", quota,
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])


# MEMO: (attribute, header_text)
_data_table_info = DataTableInfo(basic_model_csv_map() +
                                 phone_number_csv_map() +
                                 departure_location_csv_map() +
                                 [('kiintio', 'kiintio')])
_event = Event('OTiTin Fuksicursio', datetime(2021, 10, 29, 12, 00, 00),
               datetime(2021, 11, 4, 21, 00, 00), _get_quotas(), _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
