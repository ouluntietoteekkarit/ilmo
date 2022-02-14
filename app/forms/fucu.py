from wtforms import SelectField
from wtforms.validators import DataRequired
from datetime import datetime
from typing import List

from app import db
from app.email import EmailRecipient, make_greet_line
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import PhoneNumberField, DepartureBusstopField, BasicForm, ShowNameConsentField, get_str_choices
from .forms_util.models import BasicModel, PhoneNumberColumn, DepartureBusstopColumn, basic_model_csv_map, \
    departure_busstop_csv_map, phone_number_csv_map

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


def _get_participants() -> List[str]:
    return [
        _PARTICIPANT_FUKSI,
        _PARTICIPANT_PRO,
        _PARTICIPANT_BOARD_MEMBER,
        _PARTICIPANT_OTHER
    ]


class _Model(BasicModel, PhoneNumberColumn, DepartureBusstopColumn):
    __tablename__ = _form_name
    kiintio = db.Column(db.String(32))


@ShowNameConsentField()
@DepartureBusstopField(get_str_choices(_get_departure_stops()))
@PhoneNumberField()
class _Form(BasicForm):
    kiintio = SelectField('Kiintiö *', choices=get_str_choices(_get_participants()), validators=[DataRequired()])


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = model.get_email()
        phone_number = model.get_phone_number()
        departure_location = model.get_departure_busstop()
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


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    return DataTableInfo(basic_model_csv_map() +
                         phone_number_csv_map() +
                         departure_busstop_csv_map() +
                         [('kiintio', 'kiintio')])


_event = Event('OTiT Fuksicursio ilmoittautuminen', datetime(2021, 10, 29, 12, 00, 00), datetime(2024, 11, 4, 21, 00, 00), 5, 20, _Form.asks_name_consent)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    """Returns a singleton object containing this form's module information."""
    if not hasattr(get_module_info, 'result'):
        get_module_info.result = ModuleInfo(_Controller, True, _form_name, FormContext(_event, _Form, _Model, _get_data_table_info()))
    return get_module_info.result

# P U B L I C   M O D U L E   I N T E R F A C E   E N D
